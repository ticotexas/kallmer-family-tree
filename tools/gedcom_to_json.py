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

def clean_xref(value):
    return value.strip().strip("@")

def year_from_date(date_text):
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", date_text or "")
    return match.group(1) if match else ""

people = {}
families = {}

current_type = None
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
            current_type = "INDI"
            current_id = clean_xref(tag)
            people[current_id] = {
                "id": current_id,
                "name": "",
                "birth_date": "",
                "birth_year": "",
                "birth_place": "",
                "death_date": "",
                "death_year": "",
                "death_place": "",
                "living": True,
                "parents": set(),
                "spouses": set(),
                "children": set(),
                "siblings": set(),
                "families_as_spouse": set(),
                "families_as_child": set(),
                "marriages": []
            }

        elif tag.startswith("@") and value == "FAM":
            current_type = "FAM"
            current_id = clean_xref(tag)
            families[current_id] = {
                "id": current_id,
                "husband": "",
                "wife": "",
                "children": [],
                "marriage_date": "",
                "marriage_place": ""
            }

        else:
            current_type = None
            current_id = None

        continue

    if current_type == "INDI" and current_id in people:
        person = people[current_id]

        if level == "1":
            current_event = tag

            if tag == "NAME":
                person["name"] = value.replace("/", "").strip()

            elif tag == "DEAT":
                person["living"] = False

            elif tag == "FAMS":
                person["families_as_spouse"].add(clean_xref(value))

            elif tag == "FAMC":
                person["families_as_child"].add(clean_xref(value))

            continue

        if level == "2":
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

    elif current_type == "FAM" and current_id in families:
        family = families[current_id]

        if level == "1":
            current_event = tag

            if tag == "HUSB":
                family["husband"] = clean_xref(value)

            elif tag == "WIFE":
                family["wife"] = clean_xref(value)

            elif tag == "CHIL":
                family["children"].append(clean_xref(value))

            continue

        if level == "2" and current_event == "MARR":
            if tag == "DATE":
                family["marriage_date"] = value
            elif tag == "PLAC":
                family["marriage_place"] = value

for family in families.values():
    husband = family["husband"]
    wife = family["wife"]
    children = family["children"]

    parents = [p for p in [husband, wife] if p in people]

    if husband in people and wife in people:
        people[husband]["spouses"].add(wife)
        people[wife]["spouses"].add(husband)

        marriage = {
            "spouse": wife,
            "date": family["marriage_date"],
            "place": family["marriage_place"]
        }
        people[husband]["marriages"].append(marriage)

        marriage = {
            "spouse": husband,
            "date": family["marriage_date"],
            "place": family["marriage_place"]
        }
        people[wife]["marriages"].append(marriage)

    for child in children:
        if child not in people:
            continue

        for parent in parents:
            people[child]["parents"].add(parent)
            people[parent]["children"].add(child)

        for sibling in children:
            if sibling != child and sibling in people:
                people[child]["siblings"].add(sibling)

public_people = []

for person in people.values():
    birth_year = int(person["birth_year"]) if person["birth_year"].isdigit() else None

    living = person["living"]

    if birth_year and birth_year < 1915:
        living = False

    if not birth_year and not person["death_date"] and person["id"] not in {"I0000", "I0001", "I0002"}:
        living = False

    if living:
        display_birth = person["birth_year"] or person["birth_date"]
        display_death = ""
        display_place = person["birth_place"]
    else:
        display_birth = person["birth_year"] or person["birth_date"] or "?"
        display_death = person["death_year"] or person["death_date"] or "?"
        display_place = person["death_place"] or person["birth_place"]

    public_people.append({
        "id": person["id"],
        "name": person["name"],
        "living": living,
        "birth": display_birth,
        "death": display_death,
        "place": display_place,
        "birth_place": person["birth_place"],
        "death_place": person["death_place"],
        "parents": sorted(person["parents"]),
        "spouses": sorted(person["spouses"]),
        "children": sorted(person["children"]),
        "siblings": sorted(person["siblings"]),
        "marriages": person["marriages"],
    })

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(
    json.dumps({
        "people": public_people,
        "families": list(families.values())
    }, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wrote {len(public_people)} public-safe people and {len(families)} families to {out_path}")