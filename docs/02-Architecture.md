# The Kallmer Family Archive Architecture

## 1. System Overview

The project is a static family archive generated from genealogical source data and enriched with curated media and narrative content.

The principal system layers are:

1. **Source genealogy**
2. **Conversion and privacy pipeline**
3. **Public structured data**
4. **Curated media and stories**
5. **Static web presentation**
6. **Interactive family navigation**

The architecture intentionally separates genealogical data preparation from browser rendering.

## 2. Repository Structure

The exact repository should be inspected before work begins. The established major areas include:

```text
kallmer-family-tree/
├── index.html
├── tree.html
├── family-tree.html
├── css/
│   └── family-tree.css
├── js/
│   └── family-tree.js
├── tools/
│   └── gedcom_to_json.py
├── public-data/
│   └── family.json
├── data/
│   └── family-private.json
├── photos/
├── stories/
└── docs/
    ├── 00-Project-Guide.md
    ├── 01-Constitution.md
    ├── 02-Architecture.md
    ├── 03-Engineering-Guide.md
    ├── 04-Journal.md
    └── 99-Current-Status.md
```

Some file names or locations may evolve. The current local tree remains authoritative.

## 3. Data Pipeline

### 3.1 Source of Truth

Gramps is the primary genealogy authoring environment.

GEDCOM is used as an interchange format, but it may not preserve every relationship nuance needed by the archive.

Known example:

- adoption information entered in Gramps may export through GEDCOM as a birth relationship.

This limitation may eventually require either:

- an improved export path; or
- a project-owned override file.

### 3.2 Converter

`tools/gedcom_to_json.py` converts genealogy data into browser-ready JSON.

The converter is responsible for:

- people;
- families;
- parent relationships;
- spouse relationships;
- children;
- siblings;
- preferred display names;
- birth and death information;
- marriage records;
- divorce status and events;
- family identifiers attached to unions;
- children attached to the correct family union;
- public privacy reduction;
- private full-data output.

The converter should compile successfully before regenerated data is trusted.

### 3.3 Public and Private Output

`public-data/family.json` is safe for public presentation according to the current privacy rules.

`data/family-private.json` may preserve fuller information for private use.

Public privacy rules have included:

- living people receive reduced date detail;
- marriage detail is reduced when living people are involved;
- deceased people may receive fuller dates and places;
- selected geographic detail may be omitted;
- public and private output are generated separately.

The converter, not the browser, should enforce these boundaries.

## 4. Media Architecture

### 4.1 Photographs

Photographs are organized by person.

The project supports person-specific folders and generated indexes. Current folder naming may include both the person ID and a readable name.

Example:

```text
photos/
└── I0013--Floyd-Frederick-Kallmer/
    ├── portrait.png
    ├── Floyd in football uniform.png
    └── index.json
```

Photo indexes support multiple images and captions.

Proposed metadata may include optional:

- date;
- location;
- source;
- notes.

The portrait remains a distinguished image where appropriate, while galleries may contain multiple historical views.

### 4.2 Stories

Stories are stored outside the genealogy JSON and linked by person ID.

Example:

```text
stories/
└── I0013--Floyd-Frederick-Kallmer/
    ├── 01-life-sketch.md
    ├── 02-obituary.md
    └── index.json
```

This separation allows narrative material to grow without overloading genealogy records.

### 4.3 Historical Documents

Historical document support is a planned archival layer.

Documents should be treated as exhibits with metadata rather than as ordinary photographs when their documentary character matters.

Likely metadata includes:

- title;
- document type;
- date;
- location;
- people;
- source;
- transcription;
- notes.

## 5. Web Presentation

### 5.1 Homepage

`index.html` serves as the museum lobby.

It presents the archive’s identity, statistics, and principal entry points.

### 5.2 Profile and Pedigree Experience

`tree.html` is the current canonical person-profile implementation. It provides person-oriented archival detail and pedigree context.

The profile experience is expected to keep evolving into the archive’s centerpiece. A future redesign may change its internal structure or eventually introduce a clearer filename, but the existing `tree.html?person=...` URLs should remain supported unless a deliberate migration and compatibility plan is adopted.

Direct URLs currently use:

```text
tree.html?person=Ixxxx
```

The page supports:

- person search;
- normalized diacritic matching;
- life dates and places;
- portraits and galleries;
- stories;
- parents;
- spouses and marriages;
- children grouped by union;
- siblings;
- relationship history;
- browser history and shareable person links.

### 5.3 Interactive Family Tree

`family-tree.html`, `js/family-tree.js`, and `css/family-tree.css` provide a zoomable SVG family view.

The interactive tree loads `public-data/family.json`, builds a family-centered model, calculates card and relationship geometry, draws the tree, and handles person selection.

### 5.4 Stylesheet Direction

The site should move away from large inline style blocks, but not toward one monolithic stylesheet.

The preferred eventual structure is:

```text
css/
├── archive.css       # shared palette, typography, page shell, header, buttons
├── home.css          # homepage-specific composition
├── profile.css       # person profile and pedigree presentation
└── family-tree.css   # interactive SVG tree
```

Shared visual tokens and common components belong in `archive.css`. Page-specific layout and behavior remain in focused stylesheets.

This transition should happen incrementally and without visual redesign. The current local HTML must be inspected before each extraction.

## 6. Interactive Tree Pipeline

The established layout pipeline is:

```text
buildFamilyViewModel()
        ↓
buildFamilyUnits()
        ↓
measureFamilyUnits()
        ↓
layoutPrimaryFamily()
        ↓
layoutFamilyUnits()
        ↓
buildCardModel()
        ↓
buildRelationshipModel()
        ↓
calculateLayoutBounds()
        ↓
drawCards()
drawRelationshipLines()
```

### 6.1 View Model

`buildFamilyViewModel(person)` gathers the selected person and the records needed for display, including:

- parents;
- spouse families;
- spouses;
- children;
- supporting family records.

The view model describes the family context without drawing it.

### 6.2 Family Units

`buildFamilyUnits(person, unions)` converts spouse or partnership records into explicit family units.

Established conceptual shape:

```js
{
  id,
  union,
  primaryPerson,
  spouse,
  children,
  isPrimary,
  measurements
}
```

A family unit is the primary layout object for a union and its children.

### 6.3 Measurement

`measureFamilyUnit(unit)` calculates the space required by one unit.

`measureFamilyUnits(units)` applies measurement across all units and stores those measurements with the units.

Measurement should remain separate from placement.

### 6.4 Placement

`layoutPrimaryFamily(model)` places:

- the selected person;
- the selected person’s parents;
- the main ancestry axis;
- measured family units needed for descendant placement.

`layoutFamilyUnit(...)` places one spouse and that union’s children.

`layoutFamilyUnits(...)` orchestrates placement across all units.

### 6.5 Output Models

`buildCardModel(...)` returns the final set of positioned cards.

`buildRelationshipModel(...)` returns relationship definitions independent of rendering.

`calculateLayoutBounds(...)` computes the SVG viewBox from the positioned card model.

`buildLayout(model)` remains a coordinator rather than a geometry monolith.

### 6.6 Rendering

`drawCards(cards)` renders person cards.

`drawRelationshipLines(cards, relationships)` renders relationship paths.

Rendering should consume geometry already decided by the layout and routing layers.

## 7. Relationship Routing

### Established

- Connectors communicate relationship semantics.
- Parent, spouse, and child connections must remain visually distinguishable.
- Children descend from a union anchor.
- Multiple unions must not share ambiguous descendant routing.
- Connector crossings must not imply relationship.

### Deferred: Family Routing Nodes

A future routing architecture may introduce one routing node per family unit.

A routing node would own:

- union center;
- junction point;
- vertical trunk;
- elbow locations;
- final path geometry.

The intended separation is:

```text
Cards determine positions.
Routing nodes determine connector geometry.
Rendering draws supplied paths.
```

This is deferred until layout behavior is stable enough for a dedicated connector-polish milestone.

## 8. Unknown Relationships

Unknown ancestors or spouses should be represented through explicit placeholder records in the presentation model rather than improvised labels in drawing code.

The current code includes an unknown-ancestor creation path. Future work should ensure that placeholders remain:

- visually faded;
- outlined with a restrained dashed border;
- structurally meaningful;
- non-clickable or clearly distinguished where appropriate;
- consistent across parent and spouse roles.

## 9. URL and Interaction Contract

The interactive and profile experiences preserve direct person selection through URL query parameters.

Expected behavior includes:

- initial person selection from `?person=`;
- click-to-center or select;
- browser-history integration;
- shareable direct URLs;
- graceful fallback for invalid or missing person IDs.

This behavior is part of the stable visual and interaction contract during internal refactors.

## 10. Architectural Boundaries

The architecture should preserve these responsibilities:

- **Gramps** owns genealogical editing.
- **Converter scripts** own translation and public privacy.
- **JSON** owns browser-consumable structured data.
- **Media indexes** own curated media order and metadata.
- **View models** own display context.
- **Family units** own layout grouping.
- **Measurement** owns required space.
- **Layout** owns card positions.
- **Routing** owns connector geometry.
- **Rendering** owns SVG and DOM output.
- **CSS** owns presentation.

When a change crosses several boundaries, divide it into staged, independently verifiable changes.

## 11. Known Architectural Risks

- GEDCOM may omit relationship semantics such as adoption.
- Public gender accents currently depend on inferred family roles when sex or gender is absent from public JSON.
- Multiple marriages and large descendant groups stress both placement and routing.
- Mobile fit requires behavior beyond simply shrinking the desktop canvas.
- Historical document metadata still lacks a finalized schema.
- Curated media and generated indexes must remain synchronized with people and folder names.

## 12. Architecture Change Policy

Update this document when:

- a new major layer is introduced;
- responsibility moves between components;
- a data schema changes materially;
- a stable pipeline changes;
- a provisional architecture becomes established or is rejected.

Do not update it for minor styling, ordinary bug fixes, or one-time research findings.
