#!/usr/bin/env python3
"""Safely install finished genealogy stories from the archive inbox.

Dry-run by default.

Expected inbox layout:

    00-Inbox/To_Process/
        William Kallmer/
            01-growing-up-in-storm-lake.md
            02-school-basketball-and-ladon.md

The person-directory name is resolved against public-data/family.json.
Person ownership is never guessed silently: exactly one match is required
before a story can be installed.

Stories are not catalog media and do not receive M-numbers.

Apply safety:
- preflights the entire batch before changing anything;
- blocks ambiguous or unresolved person folders;
- blocks unsupported files and destination filename collisions;
- validates basic embedded-story Markdown conventions;
- never overwrites an existing story;
- rebuilds story indexes using build_story_indexes.py;
- verifies installed files and index membership;
- restores moved files to the inbox if apply or verification fails.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Sequence


MASTER_ROOT = Path("/home/tlk/Documents/Genealogy_Work/Genealogy_Media")
PROJECT_ROOT = Path("/home/tlk/Projects/kallmer-family-tree")

INBOX_PATH = MASTER_ROOT / "00-Inbox" / "To_Process"
FAMILY_JSON = PROJECT_ROOT / "public-data" / "family.json"
STORIES_DIR = PROJECT_ROOT / "stories"
INDEX_BUILDER = PROJECT_ROOT / "tools" / "build_story_indexes.py"

SUPPORTED_EXTENSIONS = {".md", ".markdown"}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or apply finished genealogy story installation."
    )
    parser.add_argument("--inbox", type=Path, default=INBOX_PATH)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the reviewed plan. Dry-run is the default.",
    )
    return parser.parse_args(argv)


def normalize_tokens(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return tuple(
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9]+", ascii_text)
        if token
    )


def slugify_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip("-") or "Unknown"


def load_people(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: Cannot read genealogy data {path}: {exc}") from None

    return [
        person
        for person in payload.get("people", [])
        if isinstance(person, dict) and person.get("id") and person.get("name")
    ]


def person_names(person: dict) -> list[str]:
    names: list[str] = []

    def add(value: object) -> None:
        text = str(value or "").strip()
        if text and text not in names:
            names.append(text)

    add(person.get("name"))
    add(person.get("birth_name"))

    for alternate in person.get("alternate_names") or []:
        if isinstance(alternate, dict):
            add(alternate.get("name"))
        else:
            add(alternate)

    nickname = str(person.get("nickname") or "").strip()
    preferred_tokens = normalize_tokens(str(person.get("name") or ""))
    if nickname and len(preferred_tokens) >= 2:
        add(f"{nickname} {preferred_tokens[-1]}")

    return names


def folder_matches_name(folder_name: str, person_name: str) -> bool:
    wanted = normalize_tokens(folder_name)
    candidate = normalize_tokens(person_name)

    if not wanted or not candidate:
        return False

    if wanted == candidate:
        return True

    # Human-friendly abbreviation:
    # "William Kallmer" matches "William Frederick Kallmer".
    if (
        len(wanted) == 2
        and len(candidate) >= 2
        and wanted[0] == candidate[0]
        and wanted[-1] == candidate[-1]
    ):
        return True

    return False


def resolve_person(folder_name: str, people: Sequence[dict]) -> list[dict]:
    matches = []

    for person in people:
        matched_names = [
            name
            for name in person_names(person)
            if folder_matches_name(folder_name, name)
        ]
        if matched_names:
            matches.append(
                {
                    "id": str(person["id"]).upper(),
                    "name": str(person["name"]).strip(),
                    "matched_names": matched_names,
                }
            )

    matches.sort(key=lambda item: item["id"])
    return matches


def begins_with_h1(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Cannot read Markdown file {path}: {exc}") from exc

    for line in text.splitlines():
        if not line.strip():
            continue
        return bool(re.match(r"^\s*#\s+\S", line))

    return False


def build_plan(inbox: Path, people: Sequence[dict]) -> list[dict]:
    if not inbox.exists():
        raise SystemExit(f"ERROR: Inbox does not exist: {inbox}")
    if not inbox.is_dir():
        raise SystemExit(f"ERROR: Inbox is not a directory: {inbox}")

    entries = sorted(inbox.iterdir(), key=lambda path: path.name.casefold())
    plan = []

    for entry in entries:
        if not entry.is_dir():
            plan.append(
                {
                    "source_dir": None,
                    "folder_name": entry.name,
                    "kind": "loose",
                    "matches": [],
                    "files": [],
                    "unsupported": [entry],
                    "errors": [
                        "Loose Inbox entries are not accepted; place stories "
                        "inside a named person directory."
                    ],
                }
            )
            continue

        matches = resolve_person(entry.name, people)
        errors: list[str] = []

        if not matches:
            errors.append("No person match.")
        elif len(matches) > 1:
            errors.append("Ambiguous person match.")

        supported = sorted(
            (
                path
                for path in entry.iterdir()
                if path.is_file() and path.suffix.casefold() in SUPPORTED_EXTENSIONS
            ),
            key=lambda path: path.name.casefold(),
        )

        unsupported = sorted(
            (
                path
                for path in entry.iterdir()
                if not (
                    path.is_file()
                    and path.suffix.casefold() in SUPPORTED_EXTENSIONS
                )
            ),
            key=lambda path: path.name.casefold(),
        )

        if unsupported:
            errors.append("Unsupported or nested Inbox entries are present.")

        if not supported:
            errors.append("No supported story files found.")

        person = matches[0] if len(matches) == 1 else None
        destination = None
        file_plans = []

        if person:
            destination = (
                STORIES_DIR
                / f"{person['id']}--{slugify_name(person['name'])}"
            )

            for source in supported:
                target = destination / source.name
                file_errors = []

                if target.exists():
                    file_errors.append("Destination filename already exists.")

                try:
                    if begins_with_h1(source):
                        file_errors.append(
                            "Story begins with an H1 heading; embedded stories "
                            "must begin with story text."
                        )
                except ValueError as exc:
                    file_errors.append(str(exc))

                if file_errors:
                    errors.extend(
                        f"{source.name}: {message}"
                        for message in file_errors
                    )

                file_plans.append(
                    {
                        "source": source,
                        "target": target,
                        "errors": file_errors,
                    }
                )

        existing_count = 0
        if destination and destination.exists():
            existing_count = sum(
                1
                for path in destination.iterdir()
                if path.is_file()
                and path.suffix.casefold() in SUPPORTED_EXTENSIONS
            )

        plan.append(
            {
                "source_dir": entry,
                "folder_name": entry.name,
                "kind": "person",
                "matches": matches,
                "person": person,
                "destination": destination,
                "files": file_plans,
                "unsupported": unsupported,
                "existing_count": existing_count,
                "errors": errors,
            }
        )

    return plan


def print_plan(plan: Sequence[dict], inbox: Path, apply: bool) -> None:
    print("KALLMER STORIES INBOX")
    print("=====================")
    print()
    print("Mode:", "APPLY" if apply else "READ-ONLY PLAN")
    print(f"Inbox: {inbox}")
    print()

    if not plan:
        print("Inbox contains no entries.")
        print()
        return

    for number, item in enumerate(plan, start=1):
        print(f"{number}. {item['folder_name']}/")

        if item["kind"] == "loose":
            print("   ERROR: Loose Inbox entry.")
            for error in item["errors"]:
                print(f"   ERROR: {error}")
            print()
            continue

        matches = item["matches"]

        if len(matches) == 1:
            person = matches[0]
            print(f"   Matched person: {person['id']} — {person['name']}")
            print(f"   Destination:    {item['destination']}")
            print(f"   Existing stories: {item['existing_count']}")
            print(f"   Incoming stories: {len(item['files'])}")
            planned_total = item["existing_count"] + len(item["files"])
            if item["errors"]:
                print(f"   Planned total: {planned_total} stories (apply blocked)")
            else:
                print(f"   Result after apply: {planned_total} stories")
        elif not matches:
            print("   Matched person: NONE")
        else:
            print("   Matched person: AMBIGUOUS")
            print("   Candidates:")
            for match in matches:
                print(f"      {match['id']} — {match['name']}")

        if item["files"]:
            print("   Stories:")
            for file_item in item["files"]:
                marker = "BLOCKED" if file_item["errors"] else "OK"
                print(f"      [{marker}] {file_item['source'].name}")

        if item["unsupported"]:
            print("   Unsupported/nested entries:")
            for path in item["unsupported"]:
                print(f"      {path.name}")

        for error in item["errors"]:
            print(f"   ERROR: {error}")

        print()

    errors = sum(len(item["errors"]) for item in plan)
    incoming = sum(len(item["files"]) for item in plan)
    resolved = sum(
        item.get("person") is not None
        for item in plan
        if item["kind"] == "person"
    )

    print("SUMMARY")
    print("=======")
    print()
    print(f"Inbox entries:      {len(plan)}")
    print(f"Resolved people:    {resolved}")
    print(f"Incoming stories:   {incoming}")
    print(f"Blocking errors:    {errors}")
    print()


def rebuild_indexes() -> None:
    # Keep parent output ahead of subprocess output when stdout is piped.
    sys.stdout.flush()
    sys.stderr.flush()
    result = subprocess.run(
        [sys.executable, str(INDEX_BUILDER)],
        cwd=PROJECT_ROOT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Story index builder failed with exit status {result.returncode}"
        )


def verify_index_membership(person_dir: Path, filenames: Sequence[str]) -> None:
    index_path = person_dir / "index.json"

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot verify story index {index_path}: {exc}") from exc

    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected story index format: {index_path}")

    missing = [filename for filename in filenames if filename not in payload]
    if missing:
        raise RuntimeError(
            f"Story index verification failed for {person_dir.name}: "
            + ", ".join(missing)
        )


def apply_plan(plan: Sequence[dict]) -> None:
    blocking = [
        error
        for item in plan
        for error in item["errors"]
    ]
    if blocking:
        raise SystemExit(
            f"ERROR: Apply blocked by {len(blocking)} preflight error(s)."
        )

    # Recheck all destinations immediately before mutation.
    targets: set[str] = set()

    for item in plan:
        if item["kind"] != "person":
            continue

        for file_item in item["files"]:
            source = file_item["source"]
            target = file_item["target"]

            if not source.exists():
                raise SystemExit(
                    f"ERROR: Inbox source disappeared after planning: {source}"
                )
            if target.exists():
                raise SystemExit(
                    f"ERROR: Destination appeared after planning: {target}"
                )
            if str(target) in targets:
                raise SystemExit(f"ERROR: Duplicate planned target: {target}")

            targets.add(str(target))

    moved: list[tuple[Path, Path]] = []

    try:
        for item in plan:
            if item["kind"] != "person":
                continue

            destination = item["destination"]
            destination.mkdir(parents=True, exist_ok=True)

            for file_item in item["files"]:
                source = file_item["source"]
                target = file_item["target"]
                shutil.move(str(source), str(target))
                moved.append((target, source))

        rebuild_indexes()

        for item in plan:
            if item["kind"] != "person":
                continue

            filenames = []

            for file_item in item["files"]:
                target = file_item["target"]
                if not target.is_file():
                    raise RuntimeError(
                        f"Installed story verification failed: {target}"
                    )
                filenames.append(target.name)

            verify_index_membership(item["destination"], filenames)

        # Remove only person directories that are genuinely empty.
        for item in plan:
            source_dir = item.get("source_dir")
            if (
                item["kind"] == "person"
                and source_dir
                and source_dir.exists()
                and not any(source_dir.iterdir())
            ):
                source_dir.rmdir()

    except Exception:
        print()
        print("APPLY FAILED — ROLLING BACK")
        print("===========================")

        rollback_errors = []

        for target, source in reversed(moved):
            try:
                if target.exists() and not source.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(source))
            except Exception as exc:
                rollback_errors.append(f"{target} -> {source}: {exc}")

        try:
            rebuild_indexes()
        except Exception as exc:
            rollback_errors.append(f"story index rebuild: {exc}")

        if rollback_errors:
            print()
            print("ROLLBACK ERRORS:")
            for error in rollback_errors:
                print(f"  {error}")

        raise

    print()
    print("APPLY COMPLETE")
    print("==============")
    print()

    installed = 0

    for item in plan:
        if item["kind"] != "person":
            continue

        print(f"{item['person']['id']} — {item['person']['name']}")
        for file_item in item["files"]:
            print(f"    installed and indexed: {file_item['target'].name}")
            installed += 1

    print()
    print(f"Installed and verified {installed} stor{'y' if installed == 1 else 'ies'}.")
    print("Story indexes rebuilt successfully.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    inbox = args.inbox.expanduser()

    people = load_people(FAMILY_JSON)
    plan = build_plan(inbox, people)
    print_plan(plan, inbox, args.apply)

    if not args.apply:
        print("No story files or indexes were changed.")
        print("Re-run with --apply only after reviewing this exact plan.")
        return 0

    if not plan:
        print("Nothing to apply.")
        return 0

    apply_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
