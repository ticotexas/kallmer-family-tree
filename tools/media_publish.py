#!/usr/bin/env python3
"""
Catalog-native website publisher for the Kallmer Family Archive.

The permanent media catalog is authoritative. This tool publishes a catalog
media object into every explicitly associated person's website photo gallery,
or removes only website copies previously created by this tool.

Safety:
- dry-run by default; --apply is required for mutation;
- vault masters are never modified;
- source and destination SHA-256 values are verified;
- existing website files are never overwritten;
- unpublish removes only catalog-tracked generated website copies whose hash
  still matches the catalog object;
- legacy-only publication is not removed by this first version;
- website index files are rebuilt with the existing build_photo_indexes.py;
- catalog writes are atomic;
- website/index changes are rolled back if the operation fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER_ROOT = Path("/home/tlk/Documents/Genealogy_Work/Genealogy_Media")
CATALOG_PATH = MASTER_ROOT / "90-Metadata" / "media_catalog.json"
FAMILY_JSON = PROJECT_ROOT / "public-data" / "family.json"
PHOTOS_DIR = PROJECT_ROOT / "photos"
INDEX_BUILDER = PROJECT_ROOT / "tools" / "build_photo_indexes.py"
CATALOG_SCHEMA = "kallmer-media-catalog-v1"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish or unpublish one catalog media object."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--publish", metavar="MXXXXXX")
    action.add_argument("--unpublish", metavar="MXXXXXX")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify website files/indexes and catalog metadata.",
    )
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    parser.add_argument("--master-root", type=Path, default=MASTER_ROOT)
    parser.add_argument("--website-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def normalize_media_id(value: str) -> str:
    value = value.strip().upper()
    if not re.fullmatch(r"M\d{6}", value):
        raise SystemExit("ERROR: Media ID must look like M000268")
    return value


def slugify_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-") or "Unknown"


def load_people(path: Path) -> dict[str, dict]:
    payload = load_json(path)
    return {
        person["id"]: person
        for person in payload.get("people", [])
        if person.get("id")
    }


def find_record(catalog: dict, media_id: str) -> dict:
    matches = [m for m in catalog["media"] if m.get("id") == media_id]
    if len(matches) != 1:
        raise SystemExit(
            f"ERROR: Expected exactly one catalog record for {media_id}; "
            f"found {len(matches)}"
        )
    return matches[0]


def generated_filename(record: dict, master: Path) -> str:
    # Keep the permanent M-number visible on the published derivative.
    if master.name.startswith(record["id"] + "--"):
        return master.name
    return f"{record['id']}--{master.name}"


def website_targets(
    record: dict, people: dict[str, dict], photos_dir: Path, filename: str
) -> list[dict]:
    person_ids = list(record.get("associations", {}).get("people", []))
    if not person_ids:
        raise SystemExit(
            f"ERROR: {record['id']} has no explicit person associations; "
            "publication requires at least one person."
        )

    targets = []
    for pid in person_ids:
        person = people.get(pid)
        if not person:
            raise SystemExit(
                f"ERROR: Associated person {pid} is not present in public-data/family.json"
            )
        person_name = person.get("name") or pid
        folder_name = f"{pid}--{slugify_name(person_name)}"
        target = photos_dir / folder_name / filename
        targets.append(
            {
                "person_id": pid,
                "person_name": person_name,
                "folder": folder_name,
                "path": target,
                "relative_path": f"{folder_name}/{filename}",
                "filename": filename,
            }
        )
    return targets


def tracked_generated_files(record: dict) -> list[dict]:
    publication = record.get("publication", {})
    files = publication.get("website_files", [])
    return files if isinstance(files, list) else []


def snapshot_indexes(photos_dir: Path) -> dict[Path, bytes]:
    snapshots: dict[Path, bytes] = {}
    if not photos_dir.exists():
        return snapshots
    for path in photos_dir.rglob("index.json"):
        if path.is_file():
            snapshots[path] = path.read_bytes()
    return snapshots


def restore_indexes(photos_dir: Path, snapshots: dict[Path, bytes]) -> None:
    current = set()
    if photos_dir.exists():
        current = {p for p in photos_dir.rglob("index.json") if p.is_file()}

    for path in current - set(snapshots):
        path.unlink()

    for path, content in snapshots.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def run_index_builder(website_root: Path) -> None:
    builder = website_root / "tools" / "build_photo_indexes.py"
    if not builder.is_file():
        raise RuntimeError(f"Index builder not found: {builder}")
    subprocess.run(
        ["python3", str(builder)],
        cwd=str(website_root),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def publication_state_for_count(count: int) -> str:
    return "shared" if count > 1 else "published"


def build_publish_plan(
    record: dict,
    master_root: Path,
    website_root: Path,
    people: dict[str, dict],
) -> dict:
    rel = record.get("master", {}).get("canonical_path")
    if not rel:
        raise SystemExit(
            f"ERROR: {record['id']} has no canonical master yet. "
            "Run legacy master cleanup/migration before catalog-native publishing."
        )

    master = master_root / rel
    if not master.is_file():
        raise SystemExit(f"ERROR: Canonical master is missing: {master}")

    actual_hash = sha256_file(master)
    if actual_hash != record.get("sha256"):
        raise SystemExit(
            f"ERROR: Canonical master SHA-256 mismatch for {record['id']}"
        )

    filename = generated_filename(record, master)
    targets = website_targets(
        record, people, website_root / "photos", filename
    )

    publication = record.get("publication", {})
    tracked = tracked_generated_files(record)
    legacy = publication.get("legacy_website_files", [])

    covered_people = {
        item.get("person_id")
        for item in [*tracked, *legacy]
        if isinstance(item, dict) and item.get("person_id")
    }

    already_published = [
        target for target in targets
        if target["person_id"] in covered_people
    ]
    targets = [
        target for target in targets
        if target["person_id"] not in covered_people
    ]

    if not targets:
        raise SystemExit(
            f"ERROR: {record['id']} is already published for all associated people; "
            "nothing to publish."
        )

    for item in targets:
        if item["path"].exists():
            raise SystemExit(
                f"ERROR: Website target already exists; refusing overwrite: {item['path']}"
            )

    return {
        "action": "publish",
        "record": record,
        "master": master,
        "targets": targets,
        "already_published": already_published,
    }


def build_unpublish_plan(
    record: dict,
    website_root: Path,
) -> dict:
    tracked = tracked_generated_files(record)
    if not tracked:
        legacy = record.get("publication", {}).get("legacy_website_files", [])
        if legacy:
            raise SystemExit(
                f"ERROR: {record['id']} is legacy-published but has no generated "
                "website_files tracked by media_publish.py. This first version "
                "will not remove legacy publication."
            )
        raise SystemExit(
            f"ERROR: {record['id']} has no catalog-tracked generated website files "
            "to unpublish."
        )

    targets = []
    for entry in tracked:
        rel = entry.get("path")
        if not rel:
            raise SystemExit(
                f"ERROR: {record['id']} has a malformed website_files entry"
            )
        path = website_root / "photos" / rel
        if not path.is_file():
            raise SystemExit(
                f"ERROR: Tracked website file is missing; refusing partial unpublish: {path}"
            )
        actual = sha256_file(path)
        if actual != record.get("sha256"):
            raise SystemExit(
                f"ERROR: Tracked website file hash differs from {record['id']}: {path}"
            )
        targets.append(
            {
                "person_id": entry.get("person_id"),
                "person_name": entry.get("person_name"),
                "path": path,
                "relative_path": rel,
                "filename": entry.get("filename") or path.name,
            }
        )

    return {
        "action": "unpublish",
        "record": record,
        "targets": targets,
    }


def print_plan(plan: dict, apply: bool) -> None:
    record = plan["record"]
    action = plan["action"]
    print("# KALLMER CATALOG-NATIVE WEBSITE PUBLISHER")
    print()
    print("Mode:", "APPLY" if apply else "READ-ONLY PLAN")
    print("Action:", action.upper())
    print("Media:", record["id"])
    print("Category:", record.get("category"))
    print("SHA-256:", record.get("sha256"))
    print("People:", ", ".join(record.get("associations", {}).get("people", [])) or "(none)")

    if action == "publish":
        print("Master:", plan["master"])
        print()
        already_published = plan.get("already_published", [])
        if already_published:
            print("Already published:")
            for target in already_published:
                print(
                    f"  {target['person_id']}  {target['person_name']}"
                )
            print()

        print("Website copies to create:")
        for target in plan["targets"]:
            print(
                f"  {target['person_id']}  {target['person_name']}\n"
                f"    {target['path']}"
            )
    else:
        print()
        print("Website copies to remove:")
        for target in plan["targets"]:
            print(
                f"  {target.get('person_id')}  {target.get('person_name')}\n"
                f"    {target['path']}"
            )

    print()
    if not apply:
        print("No website files, indexes, or catalog metadata were changed.")
        print("Re-run with --apply only after reviewing this exact plan.")


def apply_publish(
    plan: dict,
    catalog: dict,
    catalog_path: Path,
    website_root: Path,
) -> None:
    record = plan["record"]
    snapshots = snapshot_indexes(website_root / "photos")
    created_files: list[Path] = []
    created_dirs: list[Path] = []

    updated = json.loads(json.dumps(catalog))
    updated_record = find_record(updated, record["id"])

    try:
        for target in plan["targets"]:
            dest = target["path"]
            if dest.exists():
                raise RuntimeError(f"Website target appeared after planning: {dest}")

            if not dest.parent.exists():
                dest.parent.mkdir(parents=True, exist_ok=False)
                created_dirs.append(dest.parent)

            shutil.copy2(plan["master"], dest)
            created_files.append(dest)

            if sha256_file(dest) != record["sha256"]:
                raise RuntimeError(f"SHA verification failed after copy: {dest}")

        run_index_builder(website_root)

        publication = updated_record.setdefault("publication", {})
        existing_generated = publication.get("website_files", [])
        legacy = publication.setdefault("legacy_website_files", [])

        new_generated = [
            {
                "path": target["relative_path"],
                "person_id": target["person_id"],
                "person_name": target["person_name"],
                "filename": target["filename"],
            }
            for target in plan["targets"]
        ]

        publication["website_files"] = existing_generated + new_generated

        published_people = {
            item.get("person_id")
            for item in [*publication["website_files"], *legacy]
            if isinstance(item, dict) and item.get("person_id")
        }
        publication["state"] = publication_state_for_count(len(published_people))

        atomic_write_json(catalog_path, updated)

    except Exception:
        for path in reversed(created_files):
            if path.exists() and sha256_file(path) == record["sha256"]:
                path.unlink()
        restore_indexes(website_root / "photos", snapshots)
        for folder in reversed(created_dirs):
            try:
                if folder.exists() and not any(folder.iterdir()):
                    folder.rmdir()
            except OSError:
                pass
        raise

    print()
    print("# APPLY COMPLETE")
    print()
    print(f"{record['id']} published and SHA-verified.")
    print(f"Website copies: {len(plan['targets'])}")
    print("Website indexes rebuilt.")
    print("Vault master was not modified.")


def apply_unpublish(
    plan: dict,
    catalog: dict,
    catalog_path: Path,
    website_root: Path,
) -> None:
    record = plan["record"]
    snapshots = snapshot_indexes(website_root / "photos")
    removed: list[tuple[Path, bytes]] = []

    updated = json.loads(json.dumps(catalog))
    updated_record = find_record(updated, record["id"])

    try:
        for target in plan["targets"]:
            path = target["path"]
            if not path.is_file():
                raise RuntimeError(f"Tracked website file disappeared: {path}")
            if sha256_file(path) != record["sha256"]:
                raise RuntimeError(f"SHA mismatch before removal: {path}")
            content = path.read_bytes()
            path.unlink()
            removed.append((path, content))

        run_index_builder(website_root)

        publication = updated_record.setdefault("publication", {})
        publication["website_files"] = []
        legacy = publication.get("legacy_website_files", [])
        publication["state"] = (
            publication_state_for_count(len(legacy)) if legacy else "unpublished"
        )

        atomic_write_json(catalog_path, updated)

    except Exception:
        for path, content in removed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        restore_indexes(website_root / "photos", snapshots)
        raise

    # Remove only now-empty person directories after successful catalog commit.
    for target in plan["targets"]:
        folder = target["path"].parent
        try:
            if folder.exists() and not any(folder.iterdir()):
                folder.rmdir()
        except OSError:
            pass

    print()
    print("# APPLY COMPLETE")
    print()
    print(f"{record['id']} unpublished.")
    print(f"Website copies removed: {len(plan['targets'])}")
    print("Website indexes rebuilt.")
    print("Vault master and person associations were not modified.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    catalog_path = args.catalog.expanduser()
    master_root = args.master_root.expanduser()
    website_root = args.website_root.expanduser()

    catalog = load_catalog(catalog_path)
    people = load_people(website_root / "public-data" / "family.json")

    if args.publish:
        media_id = normalize_media_id(args.publish)
        record = find_record(catalog, media_id)
        plan = build_publish_plan(record, master_root, website_root, people)
    else:
        media_id = normalize_media_id(args.unpublish)
        record = find_record(catalog, media_id)
        plan = build_unpublish_plan(record, website_root)

    print_plan(plan, args.apply)

    if not args.apply:
        return 0

    if plan["action"] == "publish":
        apply_publish(plan, catalog, catalog_path, website_root)
    else:
        apply_unpublish(plan, catalog, catalog_path, website_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
