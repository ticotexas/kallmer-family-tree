#!/usr/bin/env python3
"""Catalog-native inbox workflow for the Kallmer Family Archive.

Dry-run by default. With --apply, safely ingests supported inbox images into
central category folders, assigns permanent Mxxxxx IDs, and atomically updates
the permanent media catalog.

Identity rules:
- media_catalog.json is authoritative for media identity;
- SHA-256 identifies identical content and prevents duplicate masters;
- Mxxxxx IDs are permanent and never reused;
- filenames are descriptive, not relationship metadata;
- person associations are explicit catalog metadata;
- filename/name matching is suggestion evidence only.

Apply safety:
- preflights the entire batch before changing anything;
- never overwrites destination media files;
- verifies every moved master by SHA-256;
- writes the catalog atomically only after all moves verify;
- rolls moved files back to the inbox if verification/catalog update fails;
- exact duplicate inbox files are not deleted automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


MASTER_ROOT = Path("/home/tlk/Documents/Genealogy_Work/Genealogy_Media")
PROJECT_ROOT = Path("/home/tlk/Projects/kallmer-family-tree")

CATALOG_PATH = MASTER_ROOT / "90-Metadata" / "media_catalog.json"
INBOX_PATH = MASTER_ROOT / "00-Inbox" / "To_Process"
FAMILY_JSON = PROJECT_ROOT / "public-data" / "family.json"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
CATALOG_SCHEMA = "kallmer-media-catalog-v1"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or apply catalog-native genealogy media inbox ingestion."
    )
    parser.add_argument("--inbox", type=Path, default=INBOX_PATH)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the reviewed plan. Dry-run is the default.",
    )
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_tokens(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return tuple(
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9]+", ascii_text)
        if token
    )


def load_catalog(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: Media catalog not found: {path}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read media catalog {path}: {exc}") from None

    if payload.get("schema") != CATALOG_SCHEMA:
        raise SystemExit(
            f"ERROR: Unexpected media catalog schema: {payload.get('schema')!r}"
        )
    return payload


def load_people(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read genealogy data {path}: {exc}") from None

    people = payload.get("people", []) if isinstance(payload, dict) else []
    return [p for p in people if isinstance(p, dict) and p.get("id")]


def person_names(person: dict) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    def add(value: object, source: str) -> None:
        text = str(value or "").strip()
        if text and (text, source) not in results:
            results.append((text, source))

    add(person.get("name"), "preferred")
    add(person.get("birth_name"), "birth")

    for alternate in person.get("alternate_names") or []:
        if isinstance(alternate, dict):
            add(alternate.get("name"), "alternate")
        else:
            add(alternate, "alternate")

    nickname = str(person.get("nickname") or "").strip()
    preferred_tokens = normalize_tokens(str(person.get("name") or ""))
    if nickname and len(preferred_tokens) >= 2:
        add(f"{nickname} {preferred_tokens[-1]}", "nickname")

    return results


def name_variants(name: str) -> set[tuple[str, ...]]:
    tokens = normalize_tokens(name)
    if len(tokens) < 2:
        return set()

    variants = {tokens, (tokens[0], tokens[-1])}
    if len(tokens) >= 3:
        variants.add((tokens[0], tokens[1][0], tokens[-1]))
    return variants


def sequence_present(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    width = len(needle)
    return any(
        haystack[start : start + width] == needle
        for start in range(len(haystack) - width + 1)
    )


def build_person_match_data(people: Iterable[dict]) -> list[dict]:
    result = []
    for person in people:
        variants = []
        for name, source in person_names(person):
            for variant in name_variants(name):
                variants.append({"tokens": variant, "name": name, "source": source})
        result.append(
            {
                "id": str(person["id"]).upper(),
                "preferred_name": str(person.get("name") or "").strip(),
                "variants": variants,
            }
        )
    return result


def suggest_people(filename: str, people: Sequence[dict]) -> list[dict]:
    stem_tokens = normalize_tokens(Path(filename).stem)
    matches = []

    for person in people:
        best = None
        for variant in person["variants"]:
            tokens = variant["tokens"]
            if not sequence_present(stem_tokens, tokens):
                continue

            candidate = {
                "id": person["id"],
                "preferred_name": person["preferred_name"],
                "matched_name": variant["name"],
                "name_source": variant["source"],
                "score": len(tokens),
            }
            if best is None or candidate["score"] > best["score"]:
                best = candidate

        if best is not None:
            matches.append(best)

    matches.sort(key=lambda item: (-item["score"], item["id"]))
    return matches


def infer_category(filename: str) -> str:
    text = " ".join(normalize_tokens(Path(filename).stem))

    if any(term in text for term in (
        "gravestone", "headstone", "tombstone", "grave", "cemetery"
    )):
        return "Gravestones"
    if any(term in text for term in (
        "house", "homestead", "farmstead", "residence", "church", "school building"
    )):
        return "Places"
    if any(term in text for term in (
        "portrait", "family photo", "family photograph", "group photo"
    )):
        return "People"
    return "Documents"


def media_id(number: int) -> str:
    return f"M{number:06d}"


def safe_leaf(filename: str) -> str:
    # Preserve readable filenames while removing path/control hazards.
    name = Path(filename).name.replace("\x00", "")
    name = re.sub(r"[\r\n\t]+", " ", name).strip()
    if not name or name in {".", ".."}:
        raise ValueError(f"Unsafe filename: {filename!r}")
    return name


def destination_for(master_root: Path, category: str, mid: str, source: Path) -> Path:
    return master_root / "30-Photographs" / category / f"{mid}--{safe_leaf(source.name)}"


def build_plan(catalog: dict, inbox: Path, people: Sequence[dict]) -> list[dict]:
    existing_by_hash = {item["sha256"]: item for item in catalog["media"]}
    next_number = int(catalog["next_media_number"])

    files = sorted(
        (
            path
            for path in inbox.iterdir()
            if path.is_file() and path.suffix.casefold() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )

    plan = []
    new_count = 0

    for source in files:
        digest = sha256_file(source)
        source_size = source.stat().st_size
        existing = existing_by_hash.get(digest)
        suggestions = suggest_people(source.name, people)
        suggested_ids = []
        seen = set()
        for match in suggestions:
            if match["id"] not in seen:
                seen.add(match["id"])
                suggested_ids.append(match["id"])

        if existing:
            plan.append(
                {
                    "source": source,
                    "size": source_size,
                    "sha256": digest,
                    "kind": "existing",
                    "media_id": existing["id"],
                    "category": existing["category"],
                    "suggestions": suggestions,
                    "suggested_ids": suggested_ids,
                    "existing": existing,
                }
            )
            continue

        mid = media_id(next_number + new_count)
        new_count += 1
        category = infer_category(source.name)
        plan.append(
            {
                "source": source,
                "size": source_size,
                "sha256": digest,
                "kind": "new",
                "media_id": mid,
                "category": category,
                "suggestions": suggestions,
                "suggested_ids": suggested_ids,
                "existing": None,
            }
        )

    return plan


def print_plan(plan: Sequence[dict], catalog: dict, inbox: Path, apply: bool) -> None:
    print("KALLMER CATALOG-NATIVE MEDIA INBOX")
    print("==================================")
    print()
    print("Mode:", "APPLY" if apply else "READ-ONLY PLAN")
    print(f"Inbox: {inbox}")
    print(f"Files: {len(plan)}")
    print(
        "Next permanent ID if new media are applied: "
        f"{media_id(int(catalog['next_media_number']))}"
    )
    print()

    for index, item in enumerate(plan, start=1):
        print(f"{index}. {item['source'].name}")
        print(f"   SHA-256:  {item['sha256']}")
        if item["kind"] == "existing":
            print(
                f"   Existing: {item['media_id']} — identical content already cataloged"
            )
        else:
            print(f"   Proposed: {item['media_id']}")
        print(f"   Category: {item['category']}")

        if item["suggestions"]:
            print("   Suggested people:")
            for match in item["suggestions"]:
                print(
                    f"      {match['id']}  {match['preferred_name']}  "
                    f"(matched {match['name_source']} name “{match['matched_name']}”)"
                )
        else:
            print(
                "   Suggested people: none — valid for archival ingestion without a person link"
            )

        if item["kind"] == "existing":
            current = item["existing"].get("associations", {}).get("people", [])
            additions = [pid for pid in item["suggested_ids"] if pid not in current]
            if additions:
                print("   Association additions on apply: " + ", ".join(additions))
            else:
                print("   Association additions on apply: none")
            print("   Inbox duplicate: retained; no automatic deletion")
        else:
            target = destination_for(MASTER_ROOT, item["category"], item["media_id"], item["source"])
            print(f"   Vault target: {target}")
            print(
                "   Associations on apply: "
                + (", ".join(item["suggested_ids"]) if item["suggested_ids"] else "none")
            )
        print()

    new_count = sum(item["kind"] == "new" for item in plan)
    duplicate_count = len(plan) - new_count
    no_match_count = sum(not item["suggested_ids"] for item in plan)
    print("SUMMARY")
    print("=======")
    print()
    print(f"Inbox files:              {len(plan)}")
    print(f"New media objects:        {new_count}")
    print(f"Already cataloged hashes: {duplicate_count}")
    print(f"No name suggestion:       {no_match_count}")
    print()


def make_new_record(item: dict, relative_target: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    people = list(item["suggested_ids"])
    return {
        "id": item["media_id"],
        "sha256": item["sha256"],
        "size": item["size"],
        "category": item["category"],
        "master": {
            "canonical_path": relative_target,
            "current_paths": [relative_target],
            "state": "single",
        },
        "associations": {
            "people": people,
            "evidence": "inbox_filename_name_match" if people else "none",
        },
        "publication": {
            "state": "unpublished",
            "legacy_website_files": [],
        },
        "metadata": {
            "title": None,
            "media_type": None,
            "date": None,
            "place": None,
            "caption": None,
            "source": None,
            "notes": None,
        },
        "derivation": {"derived_from": None, "kind": None},
        "migration": {
            "naming_state": "catalog_native",
            "legacy_filenames": [item["source"].name],
            "cleanup_tasks": [],
            "ingested_at": now,
        },
    }


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


def apply_plan(plan: Sequence[dict], catalog: dict, catalog_path: Path) -> None:
    master_root = MASTER_ROOT
    # Full preflight before any mutation.
    catalog_ids = {item["id"] for item in catalog["media"]}
    catalog_hashes = {item["sha256"] for item in catalog["media"]}
    targets: dict[str, Path] = {}

    for item in plan:
        if item["kind"] != "new":
            continue
        if item["media_id"] in catalog_ids:
            raise SystemExit(f"ERROR: Media ID already exists: {item['media_id']}")
        if item["sha256"] in catalog_hashes:
            raise SystemExit(
                f"ERROR: Hash became cataloged after planning: {item['source'].name}"
            )
        target = destination_for(
            master_root, item["category"], item["media_id"], item["source"]
        )
        if target.exists():
            raise SystemExit(f"ERROR: Vault target already exists: {target}")
        if str(target) in targets:
            raise SystemExit(f"ERROR: Duplicate planned target: {target}")
        targets[str(target)] = target

    updated = json.loads(json.dumps(catalog))
    moved: list[tuple[Path, Path]] = []

    try:
        # Move and verify new masters.
        for item in plan:
            if item["kind"] != "new":
                continue
            source = item["source"]
            target = destination_for(
                master_root, item["category"], item["media_id"], source
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            moved.append((target, source))

            actual = sha256_file(target)
            if actual != item["sha256"]:
                raise RuntimeError(
                    f"SHA verification failed for {item['media_id']}: {target}"
                )

            relative_target = target.relative_to(master_root).as_posix()
            updated["media"].append(make_new_record(item, relative_target))

        # Existing hashes: only add explicit suggested associations.
        by_id = {entry["id"]: entry for entry in updated["media"]}
        for item in plan:
            if item["kind"] != "existing":
                continue
            record = by_id[item["media_id"]]
            current = record.setdefault("associations", {}).setdefault("people", [])
            changed = False
            for pid in item["suggested_ids"]:
                if pid not in current:
                    current.append(pid)
                    changed = True
            current.sort()
            if changed:
                record["associations"]["evidence"] = "inbox_filename_name_match"

        new_count = sum(item["kind"] == "new" for item in plan)
        updated["next_media_number"] = int(catalog["next_media_number"]) + new_count
        updated["media"].sort(key=lambda entry: int(entry["id"][1:]))

        # Recheck uniqueness before committing catalog.
        ids = [entry["id"] for entry in updated["media"]]
        hashes = [entry["sha256"] for entry in updated["media"]]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Catalog update would create duplicate media IDs")
        if len(hashes) != len(set(hashes)):
            raise RuntimeError("Catalog update would create duplicate SHA-256 objects")

        atomic_write_json(catalog_path, updated)

    except Exception:
        # Restore moved new masters to their original inbox locations.
        rollback_errors = []
        for target, source in reversed(moved):
            try:
                if target.exists() and not source.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(source))
            except Exception as exc:  # best-effort emergency reporting
                rollback_errors.append(f"{target} -> {source}: {exc}")
        if rollback_errors:
            print("ROLLBACK ERRORS:")
            for error in rollback_errors:
                print("  " + error)
        raise

    print("APPLY COMPLETE")
    print("==============")
    print()
    for item in plan:
        if item["kind"] == "new":
            target = destination_for(
                master_root, item["category"], item["media_id"], item["source"]
            )
            print(f"{item['media_id']}  imported and SHA-verified")
            print(f"    {target}")
        else:
            print(f"{item['media_id']}  existing media; associations reviewed")
            print(f"    inbox duplicate retained: {item['source']}")
    print()
    print(f"Catalog next media number: {updated['next_media_number']}")
    print("Website publishing was not performed.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    catalog_path = args.catalog.expanduser()
    inbox = args.inbox.expanduser()

    catalog = load_catalog(catalog_path)
    people = build_person_match_data(load_people(FAMILY_JSON))
    plan = build_plan(catalog, inbox, people)
    print_plan(plan, catalog, inbox, args.apply)

    if not args.apply:
        print("No files or catalog metadata were changed.")
        print("Re-run with --apply only after reviewing this exact plan.")
        return 0

    apply_plan(plan, catalog, catalog_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
