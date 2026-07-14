#!/usr/bin/env python3
"""
Rename story folders to readable names and generate story indexes.

Run from the project root:

    python3 tools/build_story_indexes.py

Example:
    stories/I0013
becomes:
    stories/I0013--Floyd-Frederick-Kallmer

The script also creates:
    stories/index.json
    stories/<person-folder>/index.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PEOPLE_FILE = PROJECT_ROOT / "public-data" / "family.json"
STORIES_DIR = PROJECT_ROOT / "stories"

SUPPORTED_EXTENSIONS = {".md", ".markdown"}
IGNORED_FILENAMES = {"index.json", ".ds_store", "thumbs.db"}


def slugify_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-") or "Unknown"


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    text = re.sub(r"^\d+[-_ ]*", "", stem)
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()

    words = []
    for word in text.split():
        if word.isupper():
            words.append(word)
        else:
            words.append(word.capitalize())

    return " ".join(words) or "Story"


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


def load_existing_index(index_path: Path) -> dict[str, dict[str, str]]:
    if not index_path.exists():
        return {}

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    result: dict[str, dict[str, str]] = {}

    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, str):
                result[entry] = {"title": ""}
            elif isinstance(entry, dict):
                filename = entry.get("file") or entry.get("filename")
                if filename:
                    result[filename] = {
                        "title": entry.get("title", "")
                    }

    return result


def story_sort_key(path: Path) -> tuple[int, str]:
    match = re.match(r"^(\d+)", path.name)
    number = int(match.group(1)) if match else 999999
    return number, path.name.lower()


def build_story_index(folder: Path) -> int:
    existing = load_existing_index(folder / "index.json")

    story_files = sorted(
        (
            path for path in folder.iterdir()
            if path.is_file()
            and path.name.lower() not in IGNORED_FILENAMES
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=story_sort_key,
    )

    # Keep the simple filename list format for full compatibility with tree.html.
    filenames = [path.name for path in story_files]

    (folder / "index.json").write_text(
        json.dumps(filenames, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return len(filenames)


def main() -> int:
    people = load_people()
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    folder_map: dict[str, str] = {}
    renamed = 0
    indexed = 0
    stories_found = 0

    folders = sorted(path for path in STORIES_DIR.iterdir() if path.is_dir())

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
        desired_folder = STORIES_DIR / desired_name

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
        count = build_story_index(folder)
        indexed += 1
        stories_found += count
        print(f"Indexed: {folder.name} ({count} stor{'y' if count == 1 else 'ies'})")

    (STORIES_DIR / "index.json").write_text(
        json.dumps(dict(sorted(folder_map.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Renamed {renamed} folder(s).")
    print(f"Generated {indexed} story index file(s).")
    print(f"Found {stories_found} stor{'y' if stories_found == 1 else 'ies'}.")
    print("Updated stories/index.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
