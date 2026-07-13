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

def simplify_place(place):
    if not place:
        return ""

    parts = [p.strip() for p in place.split(",")]

    if len(parts) >= 3:
        return f"{parts[0]}, {parts[-1]}"

    return place

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
                "marriage_place": "",
                "divorced": False,
                "divorce_date": "",
                "divorce_place": ""
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

            if tag == "DIV":
                family["divorced"] = True

            if tag == "HUSB":
                family["husband"] = clean_xref(value)

            elif tag == "WIFE":
                family["wife"] = clean_xref(value)

            elif tag == "CHIL":
                family["children"].append(clean_xref(value))

            continue

        if level == "2":
            if current_event == "MARR":
                if tag == "DATE":
                    family["marriage_date"] = value
                elif tag == "PLAC":
                    family["marriage_place"] = value

            elif current_event == "DIV":
                if tag == "DATE":
                    family["divorce_date"] = value
                elif tag == "PLAC":
                    family["divorce_place"] = value
                    
for family in families.values():
    husband = family["husband"]
    wife = family["wife"]
    children = family["children"]

    parents = [p for p in [husband, wife] if p in people]

    if husband in people and wife in people:
        people[husband]["spouses"].add(wife)
        people[wife]["spouses"].add(husband)

        people[husband]["marriages"].append({
            "family": family["id"],
            "spouse": wife,
            "children": list(children),
            "marriage_date": family["marriage_date"],
            "marriage_place": family["marriage_place"],
            "divorced": family["divorced"],
            "divorce_date": family["divorce_date"],
            "divorce_place": family["divorce_place"]
        })

        people[wife]["marriages"].append({
            "family": family["id"],
            "spouse": husband,
            "children": list(children),
            "marriage_date": family["marriage_date"],
            "marriage_place": family["marriage_place"],
            "divorced": family["divorced"],
            "divorce_date": family["divorce_date"],
            "divorce_place": family["divorce_place"]
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

def public_marriage_record(person, marriage):
    spouse = people.get(marriage.get("spouse", ""))
    has_living_spouse = (
        is_public_living(person)
        or (spouse and is_public_living(spouse))
    )

    public_marriage = {
        "family": marriage.get("family", ""),
        "spouse": marriage.get("spouse", ""),
        "children": marriage.get("children", []),
        "marriage_date": marriage.get("marriage_date", ""),
        "marriage_place": marriage.get("marriage_place", ""),
        "divorced": marriage.get("divorced", False),
        "divorce_date": marriage.get("divorce_date", ""),
        "divorce_place": marriage.get("divorce_place", "")
    }

    if has_living_spouse:
        public_marriage["marriage_date"] = year_from_date(
            marriage.get("marriage_date", "")
        )
        public_marriage["marriage_place"] = simplify_place(
            marriage.get("marriage_place", "")
        )
        public_marriage["divorce_date"] = year_from_date(
            marriage.get("divorce_date", "")
        )
        public_marriage["divorce_place"] = simplify_place(
            marriage.get("divorce_place", "")
        )

    return public_marriage

def public_family_record(family):
    husband = people.get(family.get("husband", ""))
    wife = people.get(family.get("wife", ""))
    has_living_spouse = (
        (husband and is_public_living(husband))
        or
        (wife and is_public_living(wife))
    )
        
    public_family = dict(family)

    # The families array is also in the public JSON, so sanitize it too.
    if has_living_spouse:
        public_family["marriage_date"] = year_from_date(
            family.get("marriage_date", "")
        )
        public_family["marriage_place"] = simplify_place(
            family.get("marriage_place", "")
        )
        public_family["divorce_date"] = year_from_date(
            family.get("divorce_date", "")
        )
        public_family["divorce_place"] = simplify_place(
            family.get("divorce_place", "")
        )

    return public_family

def public_person_record(person):
    living = is_public_living(person)

    if living:
        # For living people: keep names, relationships, birth year, and place; hide exact birth date.
        display_birth = person["birth_year"]
        display_death = ""
        display_place = simplify_place(person["birth_place"])
        display_birth_place = person["birth_place"]
        display_death_place = ""
    else:
        # For deceased people: keep fuller public details.
        display_birth = person["birth_date"] or person["birth_year"] or "?"
        display_death = person["death_date"] or person["death_year"] or "?"
        display_place = person["death_place"] or person["birth_place"]
        display_birth_place = person["birth_place"]
        display_death_place = person["death_place"]

    return {
        "id": person["id"],
        "name": person["name"],
        "living": living,
        "birth": display_birth,
        "death": display_death,
        "place": display_place,
        "birth_place": display_birth_place,
        "death_place": display_death_place,
        "parents": sorted_list(person["parents"]),
        "spouses": sorted_list(person["spouses"]),
        "children": sorted_list(person["children"]),
        "siblings": sorted_list(person["siblings"]),
        "marriages": [public_marriage_record(person, marriage) for marriage in person["marriages"]],
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
public_families_list = [public_family_record(family) for family in families.values()]
private_families_list = list(families.values())

if single_out_path:
    write_json(single_out_path, public_people, public_families_list, "public-safe")
else:
    write_json(public_out_path, public_people, public_families_list, "public-safe")
    write_json(private_out_path, private_people, private_families_list, "private")
