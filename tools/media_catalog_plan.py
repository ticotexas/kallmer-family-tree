#!/usr/bin/env python3
"""Build a provisional media-catalog migration plan.

Input is the read-only JSON produced by media_catalog_migrate.py.

This tool does not touch genealogy media or website files. It assigns
deterministic provisional Mxxxxx identities to unique SHA-256 objects and
describes their current archival, publication, association, and cleanup state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


EXPECTED_SCHEMA = "kallmer-media-migration-analysis-v1"
PLAN_SCHEMA = "kallmer-media-catalog-plan-v1"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a read-only provisional Kallmer media catalog plan."
    )
    parser.add_argument(
        "--analysis",
        type=Path,
        default=Path("/tmp/kallmer-media-migration-analysis.json"),
        help=(
            "Migration analysis JSON "
            "(default: /tmp/kallmer-media-migration-analysis.json)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/kallmer-media-catalog-plan.json"),
        help=(
            "Output plan JSON "
            "(default: /tmp/kallmer-media-catalog-plan.json)"
        ),
    )
    return parser.parse_args(argv)


def load_analysis(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: Analysis file not found: {path}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read {path}: {exc}") from None

    if payload.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit(
            f"ERROR: Expected schema {EXPECTED_SCHEMA!r}, "
            f"found {payload.get('schema')!r}"
        )

    return payload


def media_state(group: dict) -> dict:
    masters = group.get("master_files", [])
    website = group.get("website_files", [])
    people = group.get("people", [])
    categories = group.get("categories", [])
    filenames = group.get("filenames", [])
    flags = set(group.get("flags", []))

    if not masters:
        master_state = "missing"
    elif len(masters) == 1:
        master_state = "single"
    else:
        master_state = "duplicate_identical"

    if not website:
        publication_state = "unpublished"
    elif len(people) <= 1:
        publication_state = "published"
    else:
        publication_state = "shared"

    naming_state = (
        "consistent"
        if len(filenames) <= 1
        else "legacy_inconsistent"
    )

    blocking_review = []

    if "website_only" in flags:
        blocking_review.append("website_only")
    if "category_conflict" in flags:
        blocking_review.append("category_conflict")
    if "unresolved_website_owner" in flags:
        blocking_review.append("unresolved_website_owner")

    cleanup_tasks = []

    if master_state == "duplicate_identical":
        cleanup_tasks.append("consolidate_duplicate_vault_masters")

    if naming_state == "legacy_inconsistent":
        cleanup_tasks.append("normalize_legacy_filenames")

    return {
        "master_state": master_state,
        "publication_state": publication_state,
        "naming_state": naming_state,
        "ready_for_catalog": not blocking_review,
        "blocking_review": blocking_review,
        "cleanup_tasks": cleanup_tasks,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    analysis = load_analysis(args.analysis)
    groups = sorted(
        analysis.get("groups", []),
        key=lambda group: group["sha256"],
    )

    media = []

    for number, group in enumerate(groups, start=1):
        media_id = f"M{number:06d}"
        state = media_state(group)

        categories = group.get("categories", [])
        category = categories[0] if len(categories) == 1 else None

        people = [
            person["id"]
            for person in group.get("people", [])
        ]

        media.append(
            {
                "id": media_id,
                "sha256": group["sha256"],
                "size": group["size"],
                "category": category,
                "people": people,
                "legacy": {
                    "master_files": group.get("master_files", []),
                    "website_files": group.get("website_files", []),
                    "filenames": group.get("filenames", []),
                },
                "state": state,
            }
        )

    summary = {
        "media_objects": len(media),
        "ready_for_catalog": sum(
            item["state"]["ready_for_catalog"]
            for item in media
        ),
        "blocking_review": sum(
            not item["state"]["ready_for_catalog"]
            for item in media
        ),
        "duplicate_master_cleanup": sum(
            "consolidate_duplicate_vault_masters"
            in item["state"]["cleanup_tasks"]
            for item in media
        ),
        "filename_cleanup": sum(
            "normalize_legacy_filenames"
            in item["state"]["cleanup_tasks"]
            for item in media
        ),
        "shared_media": sum(
            item["state"]["publication_state"] == "shared"
            for item in media
        ),
        "unpublished_media": sum(
            item["state"]["publication_state"] == "unpublished"
            for item in media
        ),
    }

    output = {
        "schema": PLAN_SCHEMA,
        "source_analysis": str(args.analysis),
        "summary": summary,
        "media": media,
    }

    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("KALLMER MEDIA CATALOG PLAN")
    print("==========================")
    print()
    print("READ ONLY — no vault or website files were changed.")
    print()
    print(f"Media objects:             {summary['media_objects']}")
    print(f"Ready for catalog:         {summary['ready_for_catalog']}")
    print(f"Blocking review:           {summary['blocking_review']}")
    print(f"Shared media:              {summary['shared_media']}")
    print(f"Unpublished media:         {summary['unpublished_media']}")
    print(f"Duplicate-master cleanup:  {summary['duplicate_master_cleanup']}")
    print(f"Filename cleanup:          {summary['filename_cleanup']}")
    print()
    print(f"Wrote: {args.output}")
    print()

    print("FIRST 10 MEDIA IDENTITIES")
    print("=========================")
    print()

    for item in media[:10]:
        people = ", ".join(item["people"]) or "none"
        filenames = ", ".join(item["legacy"]["filenames"])
        print(f"{item['id']}  {item['sha256'][:12]}...")
        print(f"    Category: {item['category'] or 'REVIEW'}")
        print(f"    People:   {people}")
        print(f"    Files:    {filenames}")
        print(
            "    State:    "
            f"{item['state']['master_state']}, "
            f"{item['state']['publication_state']}, "
            f"{item['state']['naming_state']}"
        )
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
