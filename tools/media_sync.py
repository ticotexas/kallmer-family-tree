#!/usr/bin/env python3
"""Read-only media audit for the Kallmer Family Archive.

Compares the genealogy master-media vault with the website photo exhibit by
SHA-256 content hash. This first-phase tool never copies, moves, renames,
deletes, or modifies files or indexes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_MASTER_ROOT = Path("/home/tlk/Documents/Genealogy_Work/Genealogy_Media")
DEFAULT_WEBSITE_ROOT = Path("/home/tlk/Projects/kallmer-family-tree/photos")
SUPPORTED_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"})
HASH_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True, slots=True)
class Asset:
    side: str
    root: Path
    path: Path
    relative_path: Path
    filename: str
    basename_key: str
    extension: str
    size: int
    mtime: float
    sha256: str
    category: str
    person_id: str | None

    @property
    def display_path(self) -> str:
        if self.side == "website":
            return f"photos/{self.relative_path.as_posix()}"
        return self.relative_path.as_posix()

    @property
    def modified_text(self) -> str:
        return datetime.fromtimestamp(self.mtime).astimezone().isoformat(timespec="seconds")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only SHA-256 audit of genealogy master media and website photos."
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print the human-readable audit report (the default action).",
    )
    parser.add_argument(
        "--restoration-plan",
        action="store_true",
        help="Print a read-only proposal for restoring website-only media to the master archive.",
    )
    parser.add_argument(
        "--restore-website-only",
        action="store_true",
        help="Safely copy website-only media into proposed vault destinations. Dry-run unless --apply is also supplied.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform requested restore/import changes. Never overwrites existing files.",
    )
    parser.add_argument(
        "--import-inbox",
        type=Path,
        metavar="FILE",
        help="Import one inbox image into the vault and matching website person folder. Dry-run unless --apply is supplied.",
    )
    parser.add_argument(
        "--process-inbox",
        action="store_true",
        help=(
            "Process all supported images in 00-Inbox/To_Process. "
            "People are matched automatically from filenames. "
            "Dry-run unless --apply is supplied."
        ),
    )
    parser.add_argument(
        "--person-id",
        action="append",
        dest="person_ids",
        metavar="PERSON_ID",
        help=(
            "Genealogy person ID for --import-inbox, for example I0179. "
            "Repeat --person-id to publish shared media to multiple people."
        ),
    )
    parser.add_argument(
        "--category",
        choices=("Documents", "Gravestones", "Places", "People"),
        help=(
            "Override the archival category for --import-inbox. "
            "Without this option, only clear filename terms are classified; "
            "unknown items default to Documents."
        ),
    )
    parser.add_argument(
        "--master-root",
        type=Path,
        default=DEFAULT_MASTER_ROOT,
        help=f"Master media root (default: {DEFAULT_MASTER_ROOT})",
    )
    parser.add_argument(
        "--website-root",
        type=Path,
        default=DEFAULT_WEBSITE_ROOT,
        help=f"Website photos root (default: {DEFAULT_WEBSITE_ROOT})",
    )
    return parser.parse_args(argv)


def validate_root(path: Path, label: str) -> Path:
    expanded = path.expanduser()
    try:
        resolved = expanded.resolve(strict=True)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: {label} root does not exist: {expanded}") from None
    except OSError as exc:
        raise SystemExit(f"ERROR: Cannot resolve {label} root {expanded}: {exc}") from None

    if not resolved.is_dir():
        raise SystemExit(f"ERROR: {label} root is not a directory: {resolved}")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(HASH_CHUNK_SIZE):
                digest.update(chunk)
    except OSError as exc:
        raise RuntimeError(f"Cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def infer_category(relative_path: Path) -> str:
    text = " ".join(part.casefold().replace("_", "-") for part in relative_path.parts)
    rules = (
        (("gravestone", "headstone", "tombstone", "cemetery", "grave"), "Gravestones"),
        (("obituary", "obituaries", "-obit", " obit"), "Documents"),
        (("diploma", "postcard", "certificate", "death-cert", "birth-cert", "marriage-cert",
          "passenger-list", "passengerlist", "clipping", "newspaper", "document", "record",
        "census",
          "employee-profile", "employee profile"), "Documents"),
        (("house", "homestead", "farmstead", "residence", "church", "school-building", "building"), "Places"),
        (("portrait", "portraits"), "Portraits"),
        (("family-photo", "family photos", "family-photograph", "group-photo"), "Family photographs"),
    )
    for needles, category in rules:
        if any(needle in text for needle in needles):
            return category
    return "Other"


def infer_person_id(side: str, relative_path: Path) -> str | None:
    if side != "website" or not relative_path.parts:
        return None
    folder = relative_path.parts[0]
    if len(folder) >= 5 and folder[0].upper() == "I" and folder[1:5].isdigit():
        return folder[:5].upper()
    return None


def iter_image_paths(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort(key=str.casefold)
        filenames.sort(key=str.casefold)
        directory = Path(dirpath)
        for filename in filenames:
            path = directory / filename
            if path.suffix.casefold() in SUPPORTED_EXTENSIONS and not path.is_symlink():
                yield path


def scan_root(root: Path, side: str) -> tuple[list[Asset], list[str]]:
    assets: list[Asset] = []
    errors: list[str] = []
    for path in iter_image_paths(root):
        try:
            stat = path.stat()
            relative = path.relative_to(root)
            assets.append(
                Asset(
                    side=side,
                    root=root,
                    path=path,
                    relative_path=relative,
                    filename=path.name,
                    basename_key=path.name.casefold(),
                    extension=path.suffix.casefold(),
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    sha256=sha256_file(path),
                    category=infer_category(relative),
                    person_id=infer_person_id(side, relative),
                )
            )
        except (OSError, RuntimeError) as exc:
            errors.append(str(exc))
    assets.sort(key=lambda asset: asset.display_path.casefold())
    return assets, errors


def group_by_hash(assets: Iterable[Asset]) -> dict[str, list[Asset]]:
    groups: dict[str, list[Asset]] = defaultdict(list)
    for asset in assets:
        groups[asset.sha256].append(asset)
    return dict(groups)


def print_heading(title: str, char: str = "=") -> None:
    print(title)
    print(char * len(title))


def print_asset(asset: Asset, *, show_hash: bool = False) -> None:
    print(asset.display_path)
    print(f"    Category: {asset.category}")
    print(f"    Size: {asset.size:,} bytes")
    print(f"    Modified: {asset.modified_text}")
    if show_hash:
        print(f"    SHA-256: {asset.sha256}")


def print_empty() -> None:
    print("None found.")


def print_hash_group(sha256: str, assets: Sequence[Asset]) -> None:
    print(f"SHA-256: {sha256}")
    print(f"Copies: {len(assets)}")
    for asset in sorted(assets, key=lambda item: (item.side, item.display_path.casefold())):
        print(f"    [{asset.side.upper()}] {asset.display_path}")
    print()


def generate_report(master_root: Path, website_root: Path) -> int:
    master_assets, master_errors = scan_root(master_root, "master")
    website_assets, website_errors = scan_root(website_root, "website")
    all_assets = master_assets + website_assets

    master_by_hash = group_by_hash(master_assets)
    website_by_hash = group_by_hash(website_assets)
    all_by_hash = group_by_hash(all_assets)

    master_hashes = set(master_by_hash)
    website_hashes = set(website_by_hash)
    published_hashes = master_hashes & website_hashes

    published_master = [asset for asset in master_assets if asset.sha256 in website_hashes]
    unpublished_master = [asset for asset in master_assets if asset.sha256 not in website_hashes]
    website_only = [asset for asset in website_assets if asset.sha256 not in master_hashes]

    duplicate_groups = {digest: items for digest, items in all_by_hash.items() if len(items) > 1}
    shared_website = {
        digest: items
        for digest, items in website_by_hash.items()
        if len(items) > 1
    }
    master_duplicates = {
        digest: items
        for digest, items in master_by_hash.items()
        if len(items) > 1
    }

    basename_groups: dict[str, list[Asset]] = defaultdict(list)
    for asset in all_assets:
        basename_groups[asset.basename_key].append(asset)
    filename_collisions = {
        basename: items
        for basename, items in basename_groups.items()
        if len({item.sha256 for item in items}) > 1
    }

    print_heading("MEDIA AUDIT")
    print()
    print(f"Master root:                    {master_root}")
    print(f"Website root:                   {website_root}")
    print()
    print(f"Master image files:             {len(master_assets):,}")
    print(f"Website image files:            {len(website_assets):,}")
    print(f"Unique content hashes:          {len(all_by_hash):,}")
    print(f"Published master files:         {len(published_master):,}")
    print(f"Published unique hashes:        {len(published_hashes):,}")
    print(f"Unpublished master files:       {len(unpublished_master):,}")
    print(f"Website-only files:             {len(website_only):,}")
    print(f"Duplicate content groups:       {len(duplicate_groups):,}")
    print(f"Shared website groups:          {len(shared_website):,}")
    print(f"Filename collision groups:      {len(filename_collisions):,}")
    print(f"Unreadable-file errors:         {len(master_errors) + len(website_errors):,}")
    print()

    print_heading("UNPUBLISHED MASTER MEDIA")
    print()
    if not unpublished_master:
        print_empty()
    else:
        for asset in unpublished_master:
            print_asset(asset, show_hash=True)
            print()
    print()

    print_heading("WEBSITE-ONLY MEDIA")
    print()
    print("These files have no matching master-archive copy.")
    print("Do not delete them. They may be the only surviving archival copy.")
    print()
    if not website_only:
        print_empty()
    else:
        for asset in website_only:
            print_asset(asset, show_hash=True)
            print()
    print()

    print_heading("SHARED WEBSITE MEDIA")
    print()
    print("Identical content appears in multiple website person folders or filenames.")
    print("This is often intentional for shared gravestones, family photographs, or documents.")
    print("No cleanup action is implied.")
    print()
    if not shared_website:
        print_empty()
    else:
        for digest in sorted(shared_website):
            print_hash_group(digest, shared_website[digest])
    print()

    print_heading("DUPLICATES WITHIN MASTER")
    print()
    print("These master-archive files have identical content. Review only; no deletion is implied.")
    print()
    if not master_duplicates:
        print_empty()
    else:
        for digest in sorted(master_duplicates):
            print_hash_group(digest, master_duplicates[digest])
    print()

    print_heading("FILENAME COLLISIONS")
    print()
    print("The same filename is used for different image content.")
    print("Matching filenames do not establish that files are duplicates.")
    print()
    if not filename_collisions:
        print_empty()
    else:
        for basename in sorted(filename_collisions):
            items = filename_collisions[basename]
            print(f"Filename: {items[0].filename}")
            print(f"Distinct hashes: {len({item.sha256 for item in items})}")
            for asset in sorted(items, key=lambda item: (item.side, item.display_path.casefold())):
                print(f"    [{asset.side.upper()}] {asset.display_path}")
                print(f"        SHA-256: {asset.sha256}")
            print()
    print()

    print_heading("SCAN ERRORS")
    print()
    errors = master_errors + website_errors
    if not errors:
        print_empty()
    else:
        for error in errors:
            print(error)

    return 1 if errors else 0



def proposed_destination(asset: Asset, master_root: Path) -> Path:
    """Return a proposed vault destination without creating or modifying anything."""
    if asset.side != "website":
        raise ValueError("Restoration proposals apply only to website assets")

    person_folder = asset.relative_path.parts[0] if asset.relative_path.parts else "Unassigned"
    if asset.category == "Gravestones":
        bucket = "Gravestones"
    elif asset.category == "Documents":
        bucket = "Documents"
    elif asset.category == "Places":
        bucket = "Places"
    else:
        bucket = "People"
    return master_root / "30-Photographs" / bucket / person_folder / asset.filename


def generate_restoration_plan(master_root: Path, website_root: Path) -> int:
    master_assets, master_errors = scan_root(master_root, "master")
    website_assets, website_errors = scan_root(website_root, "website")

    master_hashes = {asset.sha256 for asset in master_assets}
    website_only = [asset for asset in website_assets if asset.sha256 not in master_hashes]
    gravestones = [asset for asset in website_only if asset.category == "Gravestones"]
    documents = [asset for asset in website_only if asset.category == "Documents"]
    places = [asset for asset in website_only if asset.category == "Places"]
    people = [asset for asset in website_only if asset.category not in {"Gravestones", "Documents", "Places"}]

    print_heading("MEDIA RESTORATION PLAN")
    print()
    print("Read-only proposal. No files or directories are created or changed.")
    print()
    print(f"Master root:                    {master_root}")
    print(f"Website root:                   {website_root}")
    print()
    print(f"Website-only image files:       {len(website_only):,}")
    print(f"Proposed people-photo copies:   {len(people):,}")
    print(f"Proposed gravestone copies:     {len(gravestones):,}")
    print(f"Proposed document copies:       {len(documents):,}")
    print(f"Proposed place-photo copies:    {len(places):,}")
    print(f"Unreadable-file errors:         {len(master_errors) + len(website_errors):,}")
    print()

    def print_proposals(title: str, assets: Sequence[Asset]) -> None:
        print_heading(title)
        print()
        if not assets:
            print_empty()
        else:
            for asset in assets:
                destination = proposed_destination(asset, master_root)
                print(f"FROM: {asset.display_path}")
                print(f"TO:   {destination}")
                print(f"      SHA-256: {asset.sha256}")
                print()
        print()

    print_proposals("PROPOSED PEOPLE ARCHIVE COPIES", people)
    print_proposals("PROPOSED GRAVESTONE ARCHIVE COPIES", gravestones)
    print_proposals("PROPOSED DOCUMENT ARCHIVE COPIES", documents)
    print_proposals("PROPOSED PLACE ARCHIVE COPIES", places)

    print_heading("SCAN ERRORS")
    print()
    errors = master_errors + website_errors
    if not errors:
        print_empty()
    else:
        for error in errors:
            print(error)

    return 1 if errors else 0



def restore_website_only(master_root: Path, website_root: Path, *, apply: bool) -> int:
    master_assets, master_errors = scan_root(master_root, "master")
    website_assets, website_errors = scan_root(website_root, "website")
    errors = master_errors + website_errors
    if errors:
        print("ERROR: Scan errors were found; no copies will be attempted.", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    master_hashes = {asset.sha256 for asset in master_assets}
    website_only = [asset for asset in website_assets if asset.sha256 not in master_hashes]

    print_heading("WEBSITE-TO-VAULT RESTORATION")
    print()
    print("Mode: " + ("APPLY" if apply else "DRY RUN"))
    print("Existing destination files are never overwritten.")
    print("Each applied copy is SHA-256 verified after writing.")
    print()

    copied = 0
    skipped_existing = 0
    failed = 0

    for asset in website_only:
        destination = proposed_destination(asset, master_root)
        if destination.exists():
            skipped_existing += 1
            print(f"SKIP EXISTS: {destination}")
            continue

        if not apply:
            print(f"WOULD COPY: {asset.path}")
            print(f"        TO: {destination}")
            continue

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset.path, destination)
            copied_hash = sha256_file(destination)
            if copied_hash != asset.sha256:
                destination.unlink(missing_ok=True)
                raise RuntimeError("post-copy SHA-256 mismatch; copied file removed")
            copied += 1
            print(f"COPIED: {asset.path}")
            print(f"    TO: {destination}")
        except (OSError, RuntimeError) as exc:
            failed += 1
            print(f"FAILED: {asset.path} -> {destination}: {exc}", file=sys.stderr)

    print()
    print(f"Website-only candidates: {len(website_only):,}")
    print(f"Copied:                  {copied:,}")
    print(f"Skipped existing:        {skipped_existing:,}")
    print(f"Failed:                   {failed:,}")
    if not apply:
        print("No files were changed. Re-run with --apply only after reviewing this dry run.")
    return 1 if failed else 0


def slugify_person_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "-", ascii_name).strip("-")
    if not slug:
        raise SystemExit(f"ERROR: Cannot create folder name from person name: {name!r}")
    return slug


def find_person_record(data, person_id: str):
    if isinstance(data, dict):
        if str(data.get("id", "")).upper() == person_id:
            return data
        for value in data.values():
            found = find_person_record(value, person_id)
            if found is not None:
                return found
    elif isinstance(data, list):
        for value in data:
            found = find_person_record(value, person_id)
            if found is not None:
                return found
    return None


def find_person_folder(website_root: Path, person_id: str) -> str:
    normalized = person_id.upper()
    if len(normalized) != 5 or not normalized.startswith("I") or not normalized[1:].isdigit():
        raise SystemExit(f"ERROR: Invalid person ID: {person_id}")
    matches = sorted(
        path.name for path in website_root.iterdir()
        if path.is_dir() and path.name.upper().startswith(normalized + "--")
    )
    if len(matches) > 1:
        raise SystemExit(f"ERROR: Multiple website person folders found for {normalized}: {matches}")
    if matches:
        return matches[0]

    family_json = website_root.parent / "public-data" / "family.json"
    try:
        data = json.loads(family_json.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: No website person folder found for {normalized}, and data file is missing: {family_json}"
        ) from None
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read genealogy data {family_json}: {exc}") from None

    record = find_person_record(data, normalized)
    if record is None:
        raise SystemExit(f"ERROR: Person {normalized} not found in {family_json}")
    name = str(record.get("name") or record.get("birth_name") or "").strip()
    if not name:
        raise SystemExit(f"ERROR: Person {normalized} has no usable name in {family_json}")
    return f"{normalized}--{slugify_person_name(name)}"


def infer_import_category(filename: str) -> str:
    """Return the conservative archival bucket for one inbox import."""
    text = filename.casefold().replace("_", "-")

    gravestone_terms = (
        "gravestone",
        "headstone",
        "tombstone",
        "cemetery",
        "grave",
    )
    place_terms = (
        "house",
        "homestead",
        "farmstead",
        "residence",
        "church",
        "school-building",
        "building",
    )
    people_terms = (
        "portrait",
        "portraits",
        "family-photo",
        "family-photos",
        "family-photograph",
        "group-photo",
    )

    if any(term in text for term in gravestone_terms):
        return "Gravestones"
    if any(term in text for term in place_terms):
        return "Places"
    if any(term in text for term in people_terms):
        return "People"
    return "Documents"


def rebuild_photo_indexes(website_root: Path) -> int:
    """Run the project's canonical photo-index builder."""
    project_root = website_root.parent
    script = project_root / "tools" / "build_photo_indexes.py"

    if not script.is_file():
        print(f"ERROR: Photo-index builder not found: {script}", file=sys.stderr)
        return 1

    print()
    print_heading("PHOTO INDEX REBUILD")
    print()
    print(f"Running: {sys.executable} tools/build_photo_indexes.py")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=project_root,
        check=False,
    )
    if result.returncode != 0:
        print(
            f"ERROR: Photo-index rebuild failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        return result.returncode or 1

    print("Photo indexes rebuilt successfully.")
    return 0


def import_inbox_file(
    master_root: Path,
    website_root: Path,
    source: Path,
    person_ids: Sequence[str],
    *,
    apply: bool,
    category_override: str | None = None,
    rebuild_indexes: bool = True,
) -> int:
    source = source.expanduser().resolve(strict=True)
    if not source.is_file():
        raise SystemExit(f"ERROR: Inbox path is not a file: {source}")
    if source.suffix.casefold() not in SUPPORTED_EXTENSIONS:
        raise SystemExit(f"ERROR: Unsupported image extension: {source.suffix}")

    normalized_ids = []
    for person_id in person_ids:
        normalized = person_id.upper()
        if normalized not in normalized_ids:
            normalized_ids.append(normalized)

    person_folders = [
        find_person_folder(website_root, person_id)
        for person_id in normalized_ids
    ]
    bucket = category_override or infer_import_category(source.name)

    primary_person_folder = person_folders[0]
    vault_destination = (
        master_root
        / "30-Photographs"
        / bucket
        / primary_person_folder
        / source.name
    )
    website_destinations = [
        website_root / person_folder / source.name
        for person_folder in person_folders
    ]
    source_hash = sha256_file(source)

    print_heading("INBOX MEDIA IMPORT")
    print()
    print("Mode: " + ("APPLY" if apply else "DRY RUN"))
    print("People:")
    for person_folder in person_folders:
        print(f"    {person_folder}")
    print(f"Category:      {bucket}")
    print(f"Source:        {source}")
    print(f"Vault target:  {vault_destination}")
    print("Website targets:")
    for destination in website_destinations:
        print(f"    {destination}")
    print(f"SHA-256:       {source_hash}")
    print()

    all_destinations = [vault_destination, *website_destinations]
    conflicts = [path for path in all_destinations if path.exists()]
    if conflicts:
        print("ERROR: Destination already exists; nothing changed.", file=sys.stderr)
        for path in conflicts:
            print(f"    {path}", file=sys.stderr)
        return 1

    if not apply:
        print("WOULD MOVE inbox file to one vault master.")
        print(
            f"WOULD copy the verified vault file to "
            f"{len(website_destinations)} website person folder(s)."
        )
        print("WOULD verify every copy by SHA-256.")
        print("WOULD rebuild the website photo indexes after successful verification.")
        print("No files or directories were changed.")
        return 0

    created_website_files: list[Path] = []

    try:
        vault_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(vault_destination))
        if sha256_file(vault_destination) != source_hash:
            raise RuntimeError("vault move SHA-256 mismatch")

        for destination in website_destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vault_destination, destination)
            created_website_files.append(destination)
            if sha256_file(destination) != source_hash:
                raise RuntimeError(
                    f"website copy SHA-256 mismatch: {destination}"
                )

    except (OSError, RuntimeError) as exc:
        for destination in created_website_files:
            destination.unlink(missing_ok=True)
        print(f"FAILED: {exc}", file=sys.stderr)
        print(
            "The vault master may already have been moved successfully; "
            "website copies created during this attempt were removed.",
            file=sys.stderr,
        )
        return 1

    print("IMPORTED successfully.")
    print(f"Vault: {vault_destination}")
    print("Website copies:")
    for destination in website_destinations:
        print(f"    {destination}")
    print("Vault master and all website copies verified by SHA-256.")

    if rebuild_indexes:
        index_result = rebuild_photo_indexes(website_root)
        if index_result != 0:
            print(
                "WARNING: Media import succeeded and SHA-256 verification passed, "
                "but the photo-index rebuild failed.",
                file=sys.stderr,
            )
            return index_result

    return 0

def normalize_name_tokens(value: str) -> tuple[str, ...]:
    """Normalize a person name or filename fragment into comparable tokens."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return tuple(
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9]+", ascii_text)
        if token
    )


def person_name_strings(person: dict) -> list[str]:
    """Return useful names for matching one genealogy person."""
    names: list[str] = []

    for field in ("name", "birth_name"):
        value = str(person.get(field) or "").strip()
        if value and value not in names:
            names.append(value)

    for alternate in person.get("alternate_names") or []:
        if isinstance(alternate, dict):
            value = str(alternate.get("name") or "").strip()
        else:
            value = str(alternate or "").strip()
        if value and value not in names:
            names.append(value)

    nickname = str(person.get("nickname") or "").strip()
    primary = normalize_name_tokens(str(person.get("name") or ""))
    if nickname and len(primary) >= 2:
        nickname_tokens = normalize_name_tokens(nickname)
        if nickname_tokens:
            nickname_name = " ".join((*nickname_tokens, primary[-1]))
            if nickname_name not in names:
                names.append(nickname_name)

    return names


def name_match_variants(name: str) -> set[tuple[str, ...]]:
    """Create conservative filename variants for one known person name."""
    tokens = normalize_name_tokens(name)
    variants: set[tuple[str, ...]] = set()

    if len(tokens) < 2:
        return variants

    variants.add(tokens)

    # First + last is useful for filenames that omit middle names.
    variants.add((tokens[0], tokens[-1]))

    # First + middle initial + last handles names such as Vinton_E_Huffey.
    if len(tokens) >= 3:
        variants.add((tokens[0], tokens[1][0], tokens[-1]))

    return variants


def find_token_sequence(
    haystack: Sequence[str],
    needle: Sequence[str],
) -> list[int]:
    """Return every starting position where needle occurs contiguously."""
    if not needle or len(needle) > len(haystack):
        return []

    result = []
    width = len(needle)
    for index in range(len(haystack) - width + 1):
        if tuple(haystack[index:index + width]) == tuple(needle):
            result.append(index)
    return result


def load_people_for_matching(website_root: Path) -> list[dict]:
    family_json = website_root.parent / "public-data" / "family.json"
    try:
        payload = json.loads(family_json.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ERROR: Genealogy data file is missing: {family_json}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read genealogy data {family_json}: {exc}") from None

    people = payload.get("people", []) if isinstance(payload, dict) else []
    return [
        person
        for person in people
        if isinstance(person, dict) and person.get("id")
    ]


def build_name_variant_index(
    people: Sequence[dict],
) -> dict[tuple[str, ...], set[str]]:
    """Map conservative filename name-variants to genealogy person IDs."""
    index: dict[tuple[str, ...], set[str]] = defaultdict(set)

    for person in people:
        person_id = str(person["id"]).upper()
        for name in person_name_strings(person):
            for variant in name_match_variants(name):
                index[variant].add(person_id)

    return dict(index)


def resolve_people_from_filename(
    filename: str,
    people: Sequence[dict],
    variant_index: dict[tuple[str, ...], set[str]],
) -> tuple[list[str], list[str]]:
    """Resolve people named in a media filename without guessing ambiguities."""
    stem_tokens = normalize_name_tokens(Path(filename).stem)

    candidates = []
    for variant, person_ids in variant_index.items():
        for start in find_token_sequence(stem_tokens, variant):
            candidates.append(
                (
                    start,
                    start + len(variant),
                    variant,
                    tuple(sorted(person_ids)),
                )
            )

    # Prefer the most specific name at each location. Unique matches outrank
    # ambiguous matches when their specificity is otherwise equal.
    candidates.sort(
        key=lambda item: (
            -len(item[2]),
            len(item[3]),
            item[0],
        )
    )

    occupied: set[int] = set()
    matches: list[tuple[int, str]] = []
    ambiguous: list[str] = []
    seen_people: set[str] = set()

    for start, end, variant, person_ids in candidates:
        positions = set(range(start, end))
        if positions & occupied:
            continue

        readable = " ".join(variant)

        if len(person_ids) != 1:
            ambiguous.append(
                f"{readable} -> {', '.join(person_ids)}"
            )
            occupied.update(positions)
            continue

        person_id = person_ids[0]
        if person_id in seen_people:
            continue

        matches.append((start, person_id))
        seen_people.add(person_id)
        occupied.update(positions)

    matches.sort()
    return [person_id for _, person_id in matches], ambiguous


def process_inbox(
    master_root: Path,
    website_root: Path,
    *,
    apply: bool,
) -> int:
    """Process all supported images currently waiting in To_Process."""
    inbox = master_root / "00-Inbox" / "To_Process"

    if not inbox.is_dir():
        raise SystemExit(f"ERROR: Inbox directory does not exist: {inbox}")

    files = sorted(
        (
            path for path in inbox.iterdir()
            if path.is_file()
            and not path.is_symlink()
            and path.suffix.casefold() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )

    print_heading("INBOX BATCH PROCESSING")
    print()
    print("Mode: " + ("APPLY" if apply else "DRY RUN"))
    print(f"Inbox: {inbox}")
    print(f"Supported files found: {len(files)}")
    print()

    if not files:
        print("No supported inbox images found.")
        return 0

    people = load_people_for_matching(website_root)
    people_by_id = {
        str(person["id"]).upper(): person
        for person in people
    }
    variant_index = build_name_variant_index(people)

    resolved: list[tuple[Path, list[str]]] = []
    skipped = 0

    print_heading("AUTO-MATCH PLAN")
    print()

    for number, source in enumerate(files, start=1):
        person_ids, ambiguous = resolve_people_from_filename(
            source.name,
            people,
            variant_index,
        )

        print(f"{number}. {source.name}")
        print(f"   Category: {infer_import_category(source.name)}")

        if ambiguous:
            print("   Status: AMBIGUOUS — SKIPPED")
            for detail in ambiguous:
                print(f"   Ambiguous: {detail}")
            skipped += 1
            print()
            continue

        if not person_ids:
            print("   Status: UNRESOLVED — SKIPPED")
            skipped += 1
            print()
            continue

        print("   People:")
        for person_id in person_ids:
            person = people_by_id[person_id]
            print(f"     {person_id}  {person.get('name', '')}")

        resolved.append((source, person_ids))
        print()

    print_heading("BATCH EXECUTION")
    print()

    succeeded = 0
    failed = 0

    for source, person_ids in resolved:
        result = import_inbox_file(
            master_root,
            website_root,
            source,
            person_ids,
            apply=apply,
            rebuild_indexes=False,
        )
        if result == 0:
            succeeded += 1
        else:
            failed += 1
        print()

    if apply and succeeded:
        index_result = rebuild_photo_indexes(website_root)
        if index_result != 0:
            failed += 1

    print()
    print_heading("BATCH SUMMARY")
    print()
    print(f"Inbox files:       {len(files)}")
    print(f"Resolved:          {len(resolved)}")
    print(f"Skipped:           {skipped}")
    if apply:
        print(f"Imported:          {succeeded}")
        print(f"Failed:            {failed}")
    else:
        print(f"Ready to import:   {succeeded}")
        print("No files were changed. Re-run with --apply after reviewing this plan.")

    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    master_root = validate_root(args.master_root, "Master archive")
    website_root = validate_root(args.website_root, "Website photos")
    if args.import_inbox and args.process_inbox:
        raise SystemExit("ERROR: Use --import-inbox or --process-inbox, not both")
    if args.import_inbox and not args.person_ids:
        raise SystemExit("ERROR: --import-inbox requires at least one --person-id")
    if args.person_ids and not args.import_inbox:
        raise SystemExit("ERROR: --person-id is valid only with --import-inbox")
    if args.category and not args.import_inbox:
        raise SystemExit("ERROR: --category is valid only with --import-inbox")
    if args.apply and not (
        args.restore_website_only
        or args.import_inbox
        or args.process_inbox
    ):
        raise SystemExit(
            "ERROR: --apply requires --restore-website-only, "
            "--import-inbox, or --process-inbox"
        )
    if args.process_inbox:
        return process_inbox(
            master_root,
            website_root,
            apply=args.apply,
        )
    if args.import_inbox:
        return import_inbox_file(
            master_root,
            website_root,
            args.import_inbox,
            args.person_ids,
            apply=args.apply,
            category_override=args.category,
        )
    if args.restore_website_only:
        return restore_website_only(master_root, website_root, apply=args.apply)
    if args.restoration_plan:
        return generate_restoration_plan(master_root, website_root)
    return generate_report(master_root, website_root)


if __name__ == "__main__":
    sys.exit(main())
