#!/usr/bin/env python3
"""Initialize the permanent Kallmer Family Archive media catalog."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


EXPECTED_PLAN_SCHEMA = "kallmer-media-catalog-plan-v1"
CATALOG_SCHEMA = "kallmer-media-catalog-v1"

DEFAULT_PLAN = Path("/tmp/kallmer-media-catalog-plan.json")
DEFAULT_MASTER_ROOT = Path(
    "/home/tlk/Documents/Genealogy_Work/Genealogy_Media"
)
DEFAULT_CANDIDATE = Path(
    "/tmp/kallmer-media-catalog-candidate.json"
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize the permanent genealogy media catalog."
    )
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--master-root", type=Path, default=DEFAULT_MASTER_ROOT)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create the permanent catalog. Never overwrites.",
    )
    return parser.parse_args(argv)


def load_plan(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: Plan not found: {path}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read plan {path}: {exc}") from None

    if payload.get("schema") != EXPECTED_PLAN_SCHEMA:
        raise SystemExit(
            f"ERROR: Expected {EXPECTED_PLAN_SCHEMA!r}, "
            f"found {payload.get('schema')!r}"
        )

    return payload


def media_number(media_id: str) -> int:
    if not (
        len(media_id) == 7
        and media_id.startswith("M")
        and media_id[1:].isdigit()
    ):
        raise ValueError(f"Invalid media ID: {media_id!r}")
    return int(media_id[1:])


def build_catalog(plan: dict) -> dict:
    items = []

    for item in plan.get("media", []):
        legacy = item.get("legacy", {})
        state = item.get("state", {})

        master_paths = [
            entry["path"]
            for entry in legacy.get("master_files", [])
        ]

        people = list(item.get("people", []))

        canonical_path = (
            master_paths[0]
            if len(master_paths) == 1
            else None
        )

        items.append(
            {
                "id": item["id"],
                "sha256": item["sha256"],
                "size": item["size"],
                "category": item["category"],
                "master": {
                    "canonical_path": canonical_path,
                    "current_paths": master_paths,
                    "state": state["master_state"],
                },
                "associations": {
                    "people": people,
                    "evidence": (
                        "legacy_website_placement"
                        if people
                        else "none"
                    ),
                },
                "publication": {
                    "state": state["publication_state"],
                    "legacy_website_files": legacy.get(
                        "website_files", []
                    ),
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
                "derivation": {
                    "derived_from": None,
                    "kind": None,
                },
                "migration": {
                    "naming_state": state["naming_state"],
                    "legacy_filenames": legacy.get(
                        "filenames", []
                    ),
                    "cleanup_tasks": state.get(
                        "cleanup_tasks", []
                    ),
                },
            }
        )

    items.sort(key=lambda item: media_number(item["id"]))

    highest = max(
        (media_number(item["id"]) for item in items),
        default=0,
    )

    return {
        "schema": CATALOG_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "identity_policy": {
            "media_id": (
                "Permanent archive identity. "
                "Never renumber or reuse an assigned Mxxxxx ID."
            ),
            "sha256": (
                "Content identity and duplicate detection. "
                "A materially different file receives a new media ID."
            ),
        },
        "next_media_number": highest + 1,
        "media": items,
    }


def validate_catalog(catalog: dict) -> list[str]:
    errors = []
    ids = []
    hashes = []

    for item in catalog.get("media", []):
        media_id = item.get("id")
        digest = item.get("sha256")

        try:
            media_number(str(media_id))
        except ValueError as exc:
            errors.append(str(exc))

        ids.append(media_id)
        hashes.append(digest)

        if not item.get("category"):
            errors.append(f"{media_id}: category is empty")

        if not item.get("master", {}).get("current_paths", []):
            errors.append(f"{media_id}: no canonical-vault source path")

    if len(ids) != len(set(ids)):
        errors.append("Duplicate media IDs found")

    if len(hashes) != len(set(hashes)):
        errors.append("Duplicate SHA-256 objects found")

    return errors


def summarize(catalog: dict) -> dict:
    media = catalog["media"]

    return {
        "objects": len(media),
        "people": sum(m["category"] == "People" for m in media),
        "gravestones": sum(m["category"] == "Gravestones" for m in media),
        "places": sum(m["category"] == "Places" for m in media),
        "documents": sum(m["category"] == "Documents" for m in media),
        "artifacts": sum(m["category"] == "Artifacts" for m in media),
        "shared": sum(len(m["associations"]["people"]) > 1 for m in media),
        "unassociated": sum(not m["associations"]["people"] for m in media),
        "duplicate_master": sum(
            m["master"]["state"] == "duplicate_identical"
            for m in media
        ),
        "cleanup": sum(
            bool(m["migration"]["cleanup_tasks"])
            for m in media
        ),
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    plan = load_plan(args.plan)
    catalog = build_catalog(plan)

    errors = validate_catalog(catalog)

    if errors:
        print("CATALOG VALIDATION FAILED")
        print("=========================")
        for error in errors:
            print(f"- {error}")
        return 1

    summary = summarize(catalog)

    args.candidate.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.candidate, catalog)

    destination = (
        args.master_root.expanduser()
        / "90-Metadata"
        / "media_catalog.json"
    )

    print("KALLMER PERMANENT MEDIA CATALOG")
    print("===============================")
    print()
    print("Mode:", "APPLY" if args.apply else "DRY RUN")
    print()
    print(f"Media objects:             {summary['objects']}")
    print(f"People category:           {summary['people']}")
    print(f"Gravestones category:      {summary['gravestones']}")
    print(f"Places category:           {summary['places']}")
    print(f"Documents category:        {summary['documents']}")
    print(f"Artifacts category:        {summary['artifacts']}")
    print(f"Shared media:              {summary['shared']}")
    print(f"No person association yet: {summary['unassociated']}")
    print(f"Duplicate-master groups:   {summary['duplicate_master']}")
    print(f"Objects needing cleanup:   {summary['cleanup']}")
    print()
    print(
        f"Next permanent media ID:   "
        f"M{catalog['next_media_number']:06d}"
    )
    print()
    print(f"Candidate: {args.candidate}")
    print(f"Permanent: {destination}")
    print()

    if not args.apply:
        print("No permanent archive files were changed.")
        return 0

    if destination.exists():
        raise SystemExit(
            f"ERROR: Permanent catalog already exists: {destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    write_json(destination, catalog)

    if destination.read_bytes() != args.candidate.read_bytes():
        destination.unlink(missing_ok=True)
        raise SystemExit("ERROR: Permanent catalog verification failed")

    print("Permanent media catalog created and byte-verified.")
    print("No media files were moved, renamed, copied, or deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
