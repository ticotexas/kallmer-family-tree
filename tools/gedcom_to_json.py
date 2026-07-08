#!/usr/bin/env python3
import json
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

people = {}
current_id = None
current_tag = None

for raw in ged_path.read_text(encoding="utf-8", errors="replace").splitlines():
    parts = raw.split(" ", 2)
    if len(parts) < 2:
        continue

    level = parts[0]
    tag = parts[1]
    value = parts[2] if len(parts) > 2 else ""

    if level == "0" and tag.startswith("@") and value == "INDI":
        current_id = tag.strip("@")
        people[current_id] = {
            "id": current_id,
            "name": "",
            "birth": "",
            "death": "",
            "places": []
        }
        current_tag = None
        continue

    if current_id is None:
        continue

    if level == "1":
        current_tag = tag
        if tag == "NAME":
            people[current_id]["name"] = value.replace("/", "")
        continue

    if level == "2":
        if current_tag == "BIRT" and tag == "DATE":
            people[current_id]["birth"] = value
        elif current_tag == "DEAT" and tag == "DATE":
            people[current_id]["death"] = value
        elif tag == "PLAC":
            people[current_id]["places"].append(value)

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(
    json.dumps({"people": list(people.values())}, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wrote {len(people)} people to {out_path}")