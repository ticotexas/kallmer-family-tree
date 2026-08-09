#!/usr/bin/env python3
"""
Manage explicit person associations for catalog-native genealogy media.

The permanent media catalog is authoritative.

Safety:
- dry-run by default; --apply is required for mutation;
- validates media and person identifiers;
- vault masters are never modified;
- website files are never created or removed;
- publication state is never modified;
- duplicate additions and absent removals are rejected as no-ops;
- removal is refused while that person's publication is still tracked;
- catalog writes are atomic.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER_ROOT = Path("/home/tlk/Documents/Genealogy_Work/Genealogy_Media")
CATALOG_PATH = MASTER_ROOT / "90-Metadata" / "media_catalog.json"
FAMILY_JSON = PROJECT_ROOT / "public-data" / "family.json"
CATALOG_SCHEMA = "kallmer-media-catalog-v1"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add or remove one person association from catalog media."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--add-person",
        nargs=2,
        metavar=("MXXXXXX", "IXXXX"),
        help="Associate one catalog media object with one person.",
    )
    action.add_argument(
        "--remove-person",
        nargs=2,
        metavar=("MXXXXXX", "IXXXX"),
        help="Remove one person association from one catalog media object.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify catalog metadata. Dry-run is the default.",
    )
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    parser.add_argument("--family-json", type=Path, default=FAMILY_JSON)
    return parser.parse_args(argv)


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(path: Path) -> dict:
    payload = load_json(path)
    if payload.get("schema") != CATALOG_SCHEMA:
        raise SystemExit(
            f"ERROR: Expected catalog schema {CATALOG_SCHEMA!r}, "
            f"found {payload.get('schema')!r}"
        )
    if not isinstance(payload.get("media"), list):
        raise SystemExit("ERROR: Catalog has no media list")
    return payload


def load_people(path: Path) -> dict[str, dict]:
    payload = load_json(path)
    return {
        person["id"]: person
        for person in payload.get("people", [])
        if isinstance(person, dict) and person.get("id")
    }


def normalize_media_id(value: str) -> str:
    value = value.strip().upper()
    if not re.fullmatch(r"M\d{6}", value):
        raise SystemExit("ERROR: Media ID must look like M000157")
    return value


def normalize_person_id(value: str) -> str:
    value = value.strip().upper()
    if not re.fullmatch(r"I\d+", value):
        raise SystemExit("ERROR: Person ID must look like I0387")
    return value


def find_record(catalog: dict, media_id: str) -> dict:
    matches = [item for item in catalog["media"] if item.get("id") == media_id]
    if len(matches) != 1:
        raise SystemExit(
            f"ERROR: Expected exactly one catalog record for {media_id}; "
            f"found {len(matches)}"
        )
    return matches[0]


def person_name(person: dict) -> str:
    return person.get("name") or "(unnamed person)"


def published_person_ids(record: dict) -> set[str]:
    publication = record.get("publication", {})
    result: set[str] = set()

    for key in ("website_files", "legacy_website_files"):
        for item in publication.get(key, []):
            if isinstance(item, dict) and item.get("person_id"):
                result.add(item["person_id"])

    return result


def build_plan(
    catalog: dict,
    people: dict[str, dict],
    action: str,
    media_id: str,
    person_id: str,
) -> dict:
    record = find_record(catalog, media_id)

    if person_id not in people:
        raise SystemExit(f"ERROR: {person_id} is not present in family.json")

    current = list(record.get("associations", {}).get("people", []))
    before = sorted(dict.fromkeys(current))

    if action == "add":
        if person_id in before:
            raise SystemExit(
                f"ERROR: {media_id} is already associated with {person_id}; "
                "nothing to change."
            )
        after = sorted(before + [person_id])

    else:
        if person_id not in before:
            raise SystemExit(
                f"ERROR: {media_id} is not associated with {person_id}; "
                "nothing to remove."
            )

        if person_id in published_person_ids(record):
            raise SystemExit(
                f"ERROR: {media_id} is still published for {person_id}. "
                "Unpublish that person's website copy before removing "
                "the association."
            )

        after = [pid for pid in before if pid != person_id]

    return {
        "action": action,
        "media_id": media_id,
        "person_id": person_id,
        "person_name": person_name(people[person_id]),
        "before": before,
        "after": after,
    }


def print_people(label: str, ids: list[str], people: dict[str, dict]) -> None:
    print(label)
    if not ids:
        print("  (none)")
        return

    for pid in ids:
        person = people.get(pid, {})
        print(f"  {pid}  {person_name(person)}")


def print_plan(plan: dict, people: dict[str, dict], apply: bool) -> None:
    verb = "ADD" if plan["action"] == "add" else "REMOVE"

    print("# MEDIA ASSOCIATION PLAN")
    print()
    print(f"Mode:       {'APPLY' if apply else 'DRY RUN'}")
    print(f"Action:     {verb}")
    print(f"Media:      {plan['media_id']}")
    print(f"Person:     {plan['person_id']}  {plan['person_name']}")
    print()
    print_people("Before:", plan["before"], people)
    print()
    print_people("After:", plan["after"], people)
    print()
    print("Vault master:      unchanged")
    print("Website files:     unchanged")
    print("Publication state: unchanged")

    if not apply:
        print()
        print("No catalog metadata was changed.")
        print("Re-run with --apply only after reviewing this plan.")


def apply_plan(plan: dict, catalog: dict, catalog_path: Path) -> None:
    updated = json.loads(json.dumps(catalog))
    record = find_record(updated, plan["media_id"])

    associations = record.setdefault("associations", {})
    associations["people"] = plan["after"]

    # This operation is an explicit curator decision rather than an
    # inference from legacy placement or filename matching.
    associations["evidence"] = "explicit_curator_association"

    atomic_write_json(catalog_path, updated)

    print()
    print("# APPLY COMPLETE")
    print()
    print(
        f"{plan['media_id']} association "
        f"{'added' if plan['action'] == 'add' else 'removed'}: "
        f"{plan['person_id']}  {plan['person_name']}"
    )
    print("Catalog metadata updated atomically.")
    print("Vault master was not modified.")
    print("Website publication was not modified.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    catalog_path = args.catalog.expanduser()
    family_json = args.family_json.expanduser()

    catalog = load_catalog(catalog_path)
    people = load_people(family_json)

    if args.add_person:
        action = "add"
        raw_media_id, raw_person_id = args.add_person
    else:
        action = "remove"
        raw_media_id, raw_person_id = args.remove_person

    media_id = normalize_media_id(raw_media_id)
    person_id = normalize_person_id(raw_person_id)

    plan = build_plan(catalog, people, action, media_id, person_id)
    print_plan(plan, people, args.apply)

    if args.apply:
        apply_plan(plan, catalog, catalog_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
