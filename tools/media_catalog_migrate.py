#!/usr/bin/env python3
"""Read-only media migration analyzer for the Kallmer Family Archive.

This tool discovers the existing media model without modifying it.

It:
- hashes vault and website images with SHA-256;
- groups byte-identical files as one logical media object;
- reconstructs person associations from website person folders;
- identifies duplicate vault masters;
- identifies shared media;
- identifies filename inconsistencies;
- identifies unpublished vault media;
- identifies website-only media;
- identifies category conflicts;
- writes optional detailed JSON outside the archive.

It never copies, moves, renames, deletes, or edits archive/website files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_MASTER_ROOT = Path(
    "/home/tlk/Documents/Genealogy_Work/Genealogy_Media"
)
DEFAULT_WEBSITE_ROOT = Path(
    "/home/tlk/Projects/kallmer-family-tree/photos"
)

SUPPORTED_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
)

HASH_CHUNK_SIZE = 1024 * 1024

KNOWN_CATEGORIES = frozenset(
    {"People", "Gravestones", "Places", "Documents", "Artifacts"}
)


@dataclass(frozen=True, slots=True)
class FileRecord:
    side: str
    path: Path
    relative_path: Path
    filename: str
    size: int
    sha256: str
    category: str | None
    person_id: str | None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only migration analysis of vault and website genealogy media."
        )
    )
    parser.add_argument(
        "--master-root",
        type=Path,
        default=DEFAULT_MASTER_ROOT,
        help=f"Vault root (default: {DEFAULT_MASTER_ROOT})",
    )
    parser.add_argument(
        "--website-root",
        type=Path,
        default=DEFAULT_WEBSITE_ROOT,
        help=f"Website photos root (default: {DEFAULT_WEBSITE_ROOT})",
    )
    parser.add_argument(
        "--json",
        type=Path,
        metavar="FILE",
        help=(
            "Write the detailed analysis as JSON. "
            "Use /tmp during migration review."
        ),
    )
    parser.add_argument(
        "--show-groups",
        type=int,
        default=20,
        metavar="N",
        help="Show up to N notable groups in each report section (default: 20).",
    )
    return parser.parse_args(argv)


def validate_root(path: Path, label: str) -> Path:
    expanded = path.expanduser()
    try:
        resolved = expanded.resolve(strict=True)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: {label} does not exist: {expanded}") from None
    except OSError as exc:
        raise SystemExit(
            f"ERROR: Cannot resolve {label} {expanded}: {exc}"
        ) from None

    if not resolved.is_dir():
        raise SystemExit(f"ERROR: {label} is not a directory: {resolved}")

    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while chunk := handle.read(HASH_CHUNK_SIZE):
            digest.update(chunk)

    return digest.hexdigest()


def iter_images(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort(key=str.casefold)
        filenames.sort(key=str.casefold)

        directory = Path(dirpath)

        for filename in filenames:
            path = directory / filename

            if path.is_symlink():
                continue

            if path.suffix.casefold() in SUPPORTED_EXTENSIONS:
                yield path


def master_category(relative_path: Path) -> str | None:
    parts = relative_path.parts

    try:
        index = parts.index("30-Photographs")
    except ValueError:
        return None

    if index + 1 >= len(parts):
        return None

    candidate = parts[index + 1]

    if candidate in KNOWN_CATEGORIES:
        return candidate

    return None


def website_person_id(relative_path: Path) -> str | None:
    if not relative_path.parts:
        return None

    folder = relative_path.parts[0]
    match = re.match(r"^(I\d+)(?:--.*)?$", folder, flags=re.IGNORECASE)

    if not match:
        return None

    return match.group(1).upper()


def scan(
    root: Path,
    side: str,
) -> tuple[list[FileRecord], list[str]]:
    records: list[FileRecord] = []
    errors: list[str] = []

    for path in iter_images(root):
        try:
            relative = path.relative_to(root)
            stat = path.stat()

            records.append(
                FileRecord(
                    side=side,
                    path=path,
                    relative_path=relative,
                    filename=path.name,
                    size=stat.st_size,
                    sha256=sha256_file(path),
                    category=(
                        master_category(relative)
                        if side == "master"
                        else None
                    ),
                    person_id=(
                        website_person_id(relative)
                        if side == "website"
                        else None
                    ),
                )
            )
        except (OSError, RuntimeError) as exc:
            errors.append(f"{path}: {exc}")

    records.sort(
        key=lambda item: (
            item.side,
            item.relative_path.as_posix().casefold(),
        )
    )

    return records, errors


def load_people(website_root: Path) -> dict[str, str]:
    family_json = website_root.parent / "public-data" / "family.json"

    try:
        payload = json.loads(family_json.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}

    result: dict[str, str] = {}

    for person in payload.get("people", []):
        if not isinstance(person, dict):
            continue

        person_id = str(person.get("id") or "").upper().strip()
        name = str(person.get("name") or "").strip()

        if person_id:
            result[person_id] = name

    return result


def build_groups(
    master_records: Sequence[FileRecord],
    website_records: Sequence[FileRecord],
    people: dict[str, str],
) -> list[dict]:
    grouped: dict[str, list[FileRecord]] = defaultdict(list)

    for record in (*master_records, *website_records):
        grouped[record.sha256].append(record)

    groups: list[dict] = []

    for digest in sorted(grouped):
        records = grouped[digest]

        masters = [
            record for record in records
            if record.side == "master"
        ]
        website = [
            record for record in records
            if record.side == "website"
        ]

        person_ids = sorted(
            {
                record.person_id
                for record in website
                if record.person_id
            }
        )

        categories = sorted(
            {
                record.category
                for record in masters
                if record.category
            }
        )

        filenames = sorted(
            {record.filename for record in records},
            key=str.casefold,
        )

        flags: list[str] = []

        if len(masters) > 1:
            flags.append("duplicate_master")

        if len(person_ids) > 1:
            flags.append("shared_media")

        if len(filenames) > 1:
            flags.append("inconsistent_filenames")

        if masters and not website:
            flags.append("unpublished_master")

        if website and not masters:
            flags.append("website_only")

        if len(categories) > 1:
            flags.append("category_conflict")

        if any(
            record.person_id is None
            for record in website
        ):
            flags.append("unresolved_website_owner")

        groups.append(
            {
                "sha256": digest,
                "size": records[0].size,
                "master_files": [
                    {
                        "path": record.relative_path.as_posix(),
                        "category": record.category,
                        "filename": record.filename,
                    }
                    for record in masters
                ],
                "website_files": [
                    {
                        "path": record.relative_path.as_posix(),
                        "person_id": record.person_id,
                        "person_name": (
                            people.get(record.person_id, "")
                            if record.person_id
                            else ""
                        ),
                        "filename": record.filename,
                    }
                    for record in website
                ],
                "people": [
                    {
                        "id": person_id,
                        "name": people.get(person_id, ""),
                    }
                    for person_id in person_ids
                ],
                "categories": categories,
                "filenames": filenames,
                "flags": flags,
            }
        )

    return groups


def count_flag(groups: Sequence[dict], flag: str) -> int:
    return sum(flag in group["flags"] for group in groups)


def print_heading(title: str) -> None:
    print(title)
    print("=" * len(title))


def print_group(group: dict) -> None:
    print(f"SHA-256: {group['sha256']}")
    print(f"Size:    {group['size']:,} bytes")

    if group["categories"]:
        print(f"Category evidence: {', '.join(group['categories'])}")
    else:
        print("Category evidence: none")

    if group["people"]:
        print("People:")
        for person in group["people"]:
            label = person["id"]
            if person["name"]:
                label += f"  {person['name']}"
            print(f"    {label}")
    else:
        print("People: none established from website placement")

    print("Vault files:")
    if group["master_files"]:
        for item in group["master_files"]:
            print(f"    {item['path']}")
    else:
        print("    none")

    print("Website files:")
    if group["website_files"]:
        for item in group["website_files"]:
            owner = item["person_id"] or "UNRESOLVED"
            print(f"    [{owner}] {item['path']}")
    else:
        print("    none")

    print(f"Filenames: {', '.join(group['filenames'])}")
    print(f"Flags:     {', '.join(group['flags']) or 'none'}")
    print()


def print_section(
    title: str,
    groups: Sequence[dict],
    flag: str,
    limit: int,
) -> None:
    selected = [
        group
        for group in groups
        if flag in group["flags"]
    ]

    print_heading(title)
    print()
    print(f"Groups: {len(selected)}")
    print()

    for group in selected[:limit]:
        print_group(group)

    if len(selected) > limit:
        print(f"... {len(selected) - limit} additional group(s) omitted.")
        print()


def build_payload(
    master_root: Path,
    website_root: Path,
    master_records: Sequence[FileRecord],
    excluded_master_records: Sequence[FileRecord],
    website_records: Sequence[FileRecord],
    groups: Sequence[dict],
    errors: Sequence[str],
) -> dict:
    return {
        "schema": "kallmer-media-migration-analysis-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "master_root": str(master_root),
        "website_root": str(website_root),
        "summary": {
            "master_files": len(master_records),
            "excluded_nonvault_images": len(excluded_master_records),
            "website_files": len(website_records),
            "unique_media_objects": len(groups),
            "duplicate_master_groups": count_flag(
                groups, "duplicate_master"
            ),
            "shared_media_groups": count_flag(
                groups, "shared_media"
            ),
            "inconsistent_filename_groups": count_flag(
                groups, "inconsistent_filenames"
            ),
            "unpublished_master_groups": count_flag(
                groups, "unpublished_master"
            ),
            "website_only_groups": count_flag(
                groups, "website_only"
            ),
            "category_conflict_groups": count_flag(
                groups, "category_conflict"
            ),
            "unresolved_website_owner_groups": count_flag(
                groups, "unresolved_website_owner"
            ),
            "scan_errors": len(errors),
        },
        "groups": list(groups),
        "excluded_nonvault_images": [
            {
                "path": record.relative_path.as_posix(),
                "sha256": record.sha256,
                "size": record.size,
            }
            for record in excluded_master_records
        ],
        "errors": list(errors),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    master_root = validate_root(args.master_root, "Master archive")
    website_root = validate_root(args.website_root, "Website photos")

    all_master_records, master_errors = scan(master_root, "master")
    website_records, website_errors = scan(website_root, "website")

    master_records = [
        record
        for record in all_master_records
        if (
            record.relative_path.parts
            and record.relative_path.parts[0] == "30-Photographs"
        )
    ]

    excluded_master_records = [
        record
        for record in all_master_records
        if record not in master_records
    ]

    errors = master_errors + website_errors
    people = load_people(website_root)

    groups = build_groups(
        master_records,
        website_records,
        people,
    )

    payload = build_payload(
        master_root,
        website_root,
        master_records,
        excluded_master_records,
        website_records,
        groups,
        errors,
    )

    print_heading("KALLMER MEDIA MIGRATION ANALYSIS")
    print()
    print("READ ONLY — no archive or website files were changed.")
    print()
    print(f"Canonical vault image files:   {len(master_records):,}")
    print(f"Excluded non-vault images:     {len(excluded_master_records):,}")
    print(f"Website image files:           {len(website_records):,}")
    print(f"Unique media objects:          {len(groups):,}")
    print()
    print(
        "Duplicate vault-master groups: "
        f"{count_flag(groups, 'duplicate_master'):,}"
    )
    print(
        "Shared-media groups:            "
        f"{count_flag(groups, 'shared_media'):,}"
    )
    print(
        "Inconsistent-filename groups:   "
        f"{count_flag(groups, 'inconsistent_filenames'):,}"
    )
    print(
        "Unpublished-master groups:      "
        f"{count_flag(groups, 'unpublished_master'):,}"
    )
    print(
        "Website-only groups:            "
        f"{count_flag(groups, 'website_only'):,}"
    )
    print(
        "Category-conflict groups:       "
        f"{count_flag(groups, 'category_conflict'):,}"
    )
    print(
        "Unresolved website-owner groups:"
        f" {count_flag(groups, 'unresolved_website_owner'):,}"
    )
    print(f"Scan errors:                    {len(errors):,}")
    print()

    print_section(
        "DUPLICATE VAULT MASTERS",
        groups,
        "duplicate_master",
        args.show_groups,
    )

    print_section(
        "SHARED MEDIA",
        groups,
        "shared_media",
        args.show_groups,
    )

    print_section(
        "INCONSISTENT FILENAMES",
        groups,
        "inconsistent_filenames",
        args.show_groups,
    )

    print_section(
        "CATEGORY CONFLICTS",
        groups,
        "category_conflict",
        args.show_groups,
    )

    print_section(
        "WEBSITE-ONLY MEDIA",
        groups,
        "website_only",
        args.show_groups,
    )

    if args.json:
        output = args.json.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print_heading("DETAILED ANALYSIS")
        print()
        print(f"Wrote: {output}")
        print()

    if errors:
        print_heading("SCAN ERRORS")
        print()
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
