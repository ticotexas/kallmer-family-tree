#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: python3 tools/gedcom_to_json.py /path/to/Kallmer.ged data/family.json")
    sys.exit(1)

ged_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

if not ged_path.exists():
    print(f"GEDCOM not found: {ged_path}")
    sys.exit(1)

def year_from_date(date_text):
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", date_text or "")
    return match.group(1) if match else ""

people = {}
current_id = None
current_event = None

for raw in ged_path.read_text(encoding="utf-8", errors="replace").splitlines():
    parts = raw.split(" ", 2)
    if len(parts) < 2:
        continue

    level, tag = parts[0], parts[1]
    value = parts[2] if len(parts) > 2 else ""

    if level == "0":
        current_event = None
        if tag.startswith("@") and value == "INDI":
            current_id = tag.strip("@")
            people[current_id] = {
                "id": current_id,
                "name": "",
                "birth_date": "",
                "birth_year": "",
                "birth_place": "",
                "death_date": "",
                "death_year": "",
                "death_place": "",
                "living": True
            }
        else:
            current_id = None
        continue

    if current_id is None:
        continue

    if level == "1":
        current_event = tag

        if tag == "NAME":
            people[current_id]["name"] = value.replace("/", "").strip()

        if tag == "DEAT":
            people[current_id]["living"] = False

        continue

    if level == "2":
        person = people[current_id]

        if current_event == "BIRT":
            if tag == "DATE":
                person["birth_date"] = value
                person["birth_year"] = year_from_date(value)
            elif tag == "PLAC":
                person["birth_place"] = value

        elif current_event == "DEAT":
            if tag == "DATE":
                person["death_date"] = value
                person["death_year"] = year_from_date(value)
            elif tag == "PLAC":
                person["death_place"] = value

public_people = []

for person in people.values():

    birth_year = int(person["birth_year"]) if person["birth_year"].isdigit() else None

    living = person["living"]

    if birth_year and birth_year < 1915:
        living = False

    if not birth_year and not person["death_date"] and person["id"] not in {"I0000", "I0001", "I0002"}:
        living = False

    if living:
        display_birth = person["birth_year"]
        display_death = ""
        display_place = ""
    else:
        display_birth = person["birth_year"] or person["birth_date"]
        display_death = person["death_year"] or person["death_date"]
        display_place = person["death_place"] or person["birth_place"]

    public_people.append({
        "id": person["id"],
        "name": person["name"],
        "living": living,
        "birth": display_birth,
        "death": display_death,
        "place": display_place,
    })


out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(
    json.dumps({"people": public_people}, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wrote {len(public_people)} public-safe people to {out_path}")