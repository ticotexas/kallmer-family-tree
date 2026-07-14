#!/usr/bin/env python3
"""
Rename photo folders to readable names and generate gallery indexes.

Run from the project root:

    python3 tools/build_photo_indexes.py

Example:
    photos/I0013
becomes:
    photos/I0013--Floyd-Frederick-Kallmer

The script also creates:
    photos/index.json
    photos/<person-folder>/index.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PEOPLE_FILE = PROJECT_ROOT / "public-data" / "family.json"
PHOTOS_DIR = PROJECT_ROOT / "photos"

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"
}

IGNORED_FILENAMES = {
    "index.json",
    ".ds_store",
    "thumbs.db",
}


def slugify_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-") or "Unknown"


def caption_from_filename(filename: str) -> str:
    stem = Path(filename).stem

    if stem.lower() == "portrait":
        return "Portrait"

    text = re.sub(r"^\d+[-_ ]*", "", stem)
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # Preserve likely years and acronyms while title-casing ordinary words.
    words = []
    for word in text.split():
        if re.fullmatch(r"\d{4}", word) or word.isupper():
            words.append(word)
        else:
            words.append(word.capitalize())

    return " ".join(words) or "Photograph"


def load_people() -> dict[str, dict[str, Any]]:
    if not PEOPLE_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {PEOPLE_FILE.relative_to(PROJECT_ROOT)}. "
            "Run this script from inside the Kallmer project."
        )

    payload = json.loads(PEOPLE_FILE.read_text(encoding="utf-8"))
    return {
        person["id"]: person
        for person in payload.get("people", [])
        if person.get("id")
    }


def person_id_from_folder(folder_name: str) -> str | None:
    match = re.match(r"^(I\d+)(?:--.*)?$", folder_name)
    return match.group(1) if match else None


def load_existing_captions(index_path: Path) -> dict[str, dict[str, str]]:
    if not index_path.exists():
        return {}

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    entries = payload if isinstance(payload, list) else payload.get("photos", [])
    result: dict[str, dict[str, str]] = {}

    for entry in entries:
        if isinstance(entry, str):
            result[entry] = {"caption": "", "alt": ""}
        elif isinstance(entry, dict):
            filename = entry.get("file") or entry.get("filename") or entry.get("src")
            if filename:
                result[filename] = {
                    "caption": entry.get("caption", ""),
                    "alt": entry.get("alt", ""),
                }

    return result


def image_sort_key(path: Path) -> tuple[int, str]:
    name = path.name.lower()

    # portrait.png remains first when present.
    if name == "portrait.png":
        return (0, name)
    if name.startswith("portrait"):
        return (1, name)

    return (2, name)


def build_gallery_index(folder: Path, person_name: str) -> int:
    existing = load_existing_captions(folder / "index.json")

    image_files = sorted(
        (
            path for path in folder.iterdir()
            if path.is_file()
            and path.name.lower() not in IGNORED_FILENAMES
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=image_sort_key,
    )

    entries = []
    for image in image_files:
        saved = existing.get(image.name, {})
        entries.append({
            "file": image.name,
            "caption": saved.get("caption") or caption_from_filename(image.name),
            "alt": saved.get("alt") or person_name,
        })

    (folder / "index.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return len(entries)


def main() -> int:
    people = load_people()
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    folder_map: dict[str, str] = {}
    renamed = 0
    indexed = 0
    photos_found = 0

    folders = sorted(path for path in PHOTOS_DIR.iterdir() if path.is_dir())

    for folder in folders:
        person_id = person_id_from_folder(folder.name)
        if not person_id:
            print(f"Skipping unrecognized folder: {folder.name}")
            continue

        person = people.get(person_id)
        if not person:
            print(f"Skipping {folder.name}: {person_id} is not in family.json")
            continue

        readable_name = slugify_name(person.get("name", person_id))
        desired_name = f"{person_id}--{readable_name}"
        desired_folder = PHOTOS_DIR / desired_name

        if folder != desired_folder:
            if desired_folder.exists():
                print(
                    f"Cannot rename {folder.name}: {desired_name} already exists.",
                    file=sys.stderr,
                )
                continue

            folder.rename(desired_folder)
            folder = desired_folder
            renamed += 1
            print(f"Renamed: {person_id} -> {desired_name}")

        folder_map[person_id] = folder.name
        count = build_gallery_index(folder, person.get("name", person_id))
        indexed += 1
        photos_found += count
        print(f"Indexed: {folder.name} ({count} photo{'s' if count != 1 else ''})")

    (PHOTOS_DIR / "index.json").write_text(
        json.dumps(dict(sorted(folder_map.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Renamed {renamed} folder(s).")
    print(f"Generated {indexed} gallery index file(s).")
    print(f"Found {photos_found} photograph(s).")
    print("Updated photos/index.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
