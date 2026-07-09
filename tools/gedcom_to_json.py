#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

if len(sys.argv) not in {2, 3}:
    print("Usage:")
    print("  python3 tools/gedcom_to_json.py data/Kallmer.ged")
    print("  python3 tools/gedcom_to_json.py data/Kallmer.ged public-data/family.json  # old single-output mode")
    sys.exit(1)

ged_path = Path(sys.argv[1])

if not ged_path.exists():
    print(f"GEDCOM not found: {ged_path}")
    sys.exit(1)

# Default two-output paths, relative to the project root.
public_out_path = Path("public-data/family.json")
private_out_path = Path("data/family-private.json")

# Backward-compatible mode: if an output path is supplied, write only public-safe JSON there.
single_out_path = Path(sys.argv[2]) if len(sys.argv) == 3 else None

def clean_xref(value):
    return value.strip().strip("@")

def year_from_date(date_text):
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", date_text or "")
    return match.group(1) if match else ""

def sorted_list(value):
    return sorted(value) if value else []

def write_json(path, people_list, families_list, label):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "people": people_list,
            "families": families_list
        }, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"Wrote {len(people_list)} {label} people and {len(families_list)} families to {path}")

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

        people[husband]["marriages"].append({
            "spouse": wife,
            "date": family["marriage_date"],
            "place": family["marriage_place"]
        })

        people[wife]["marriages"].append({
            "spouse": husband,
            "date": family["marriage_date"],
            "place": family["marriage_place"]
        })

    for child in children:
        if child not in people:
            continue

        for parent in parents:
            people[child]["parents"].add(parent)
            people[parent]["children"].add(child)

        for sibling in children:
            if sibling != child and sibling in people:
                people[child]["siblings"].add(sibling)

def is_public_living(person):
    birth_year = int(person["birth_year"]) if person["birth_year"].isdigit() else None
    living = person["living"]

    # Safety rule: very old people without death records should not display as living.
    if birth_year and birth_year < 1915:
        living = False

    # Safety rule for older sparse records, while preserving the current known living/root IDs.
    if not birth_year and not person["death_date"] and person["id"] not in {"I0000", "I0001", "I0002"}:
        living = False

    return living

def public_person_record(person):
    living = is_public_living(person)

    if living:
        display_birth = person["birth_year"] or person["birth_date"]
        display_death = ""
        display_place = person["birth_place"]
    else:
        display_birth = person["birth_year"] or person["birth_date"] or "?"
        display_death = person["death_year"] or person["death_date"] or "?"
        display_place = person["death_place"] or person["birth_place"]

    return {
        "id": person["id"],
        "name": person["name"],
        "living": living,
        "birth": display_birth,
        "death": display_death,
        "place": display_place,
        "birth_place": person["birth_place"],
        "death_place": person["death_place"],
        "parents": sorted_list(person["parents"]),
        "spouses": sorted_list(person["spouses"]),
        "children": sorted_list(person["children"]),
        "siblings": sorted_list(person["siblings"]),
        "marriages": person["marriages"],
    }

def private_person_record(person):
    # Private version keeps fuller date strings for local/family use.
    return {
        "id": person["id"],
        "name": person["name"],
        "living": person["living"],
        "birth": person["birth_date"] or person["birth_year"] or "?",
        "death": person["death_date"] or person["death_year"] or "",
        "place": person["death_place"] or person["birth_place"],
        "birth_date": person["birth_date"],
        "birth_year": person["birth_year"],
        "birth_place": person["birth_place"],
        "death_date": person["death_date"],
        "death_year": person["death_year"],
        "death_place": person["death_place"],
        "parents": sorted_list(person["parents"]),
        "spouses": sorted_list(person["spouses"]),
        "children": sorted_list(person["children"]),
        "siblings": sorted_list(person["siblings"]),
        "families_as_spouse": sorted_list(person["families_as_spouse"]),
        "families_as_child": sorted_list(person["families_as_child"]),
        "marriages": person["marriages"],
    }

public_people = [public_person_record(person) for person in people.values()]
private_people = [private_person_record(person) for person in people.values()]
families_list = list(families.values())

if single_out_path:
    write_json(single_out_path, public_people, families_list, "public-safe")
else:
    write_json(public_out_path, public_people, families_list, "public-safe")
    write_json(private_out_path, private_people, families_list, "private")
