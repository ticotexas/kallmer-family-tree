# The Kallmer Family Archive Architecture

---

# 1. System Overview

The Kallmer Family Archive is a static digital family archive generated from genealogical source data and enriched with curated historical content.

Its architecture intentionally separates genealogy, data transformation, editorial content, presentation, and interaction into distinct responsibilities. This separation allows each layer to evolve independently while preserving long-term maintainability.

The principal architectural layers are:

1. Source genealogy
2. Conversion and privacy pipeline
3. Public structured data
4. Curated media and narrative content
5. Static web presentation
6. Interactive family navigation

---

# 2. Architecture Philosophy

The architecture exists to separate long-lived responsibilities.

Each major layer should have one clear purpose and one primary owner.

Whenever practical:

- genealogy editing belongs in genealogy tools;
- data transformation belongs in converter scripts;
- historical curation belongs in archival content;
- presentation belongs in the browser;
- visual appearance belongs in CSS.

Each component should know only what it must know to fulfill its own responsibility.

This separation minimizes coupling, improves maintainability, and allows individual layers to evolve independently without forcing unnecessary changes throughout the system.

---

# 3. Repository Structure

The exact repository should always be verified before work begins. The current local repository is authoritative.

The established project organization is:

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
    ├── 05-Visual-Language.md
    ├── 06-Version-2-Roadmap.md
    └── 99-Current-Status.md
```

Individual filenames may change over time, but the architectural responsibilities of these areas should remain stable.

---

# 4. Data Pipeline

## 4.1 Source of Truth

Gramps is the project's genealogy authoring environment.

GEDCOM serves as the interchange format between genealogy editing and the archive.

GEDCOM does not preserve every genealogical nuance required by the archive. Certain relationship semantics may require project-owned interpretation or supplemental metadata.

Genealogical editing belongs in Gramps rather than browser code.

---

## 4.2 Converter

`tools/gedcom_to_json.py` converts genealogy data into browser-ready JSON.

The converter owns:

- people;
- families;
- parent relationships;
- spouse relationships;
- children;
- siblings;
- preferred display names;
- birth and death information;
- marriage records;
- divorce events;
- family identifiers;
- public privacy reduction;
- private full-data generation.

Privacy decisions belong in the converter rather than in browser code.

The converter should compile successfully before regenerated data is trusted.

---

## 4.3 Public and Private Output

Two independent outputs are generated.

**Public**

`public-data/family.json`

contains information suitable for public presentation.

**Private**

`data/family-private.json`

may preserve fuller historical information.

The browser should consume already-prepared data rather than performing privacy decisions during rendering.

---

# 5. Media Architecture

## 5.1 Photographs

Photographs are organized by person.

Each person may contain a dedicated folder together with a generated index.

Typical structure:

```text
photos/
└── I0013--Floyd-Frederick-Kallmer/
    ├── portrait.png
    ├── football-uniform.png
    └── index.json
```

Photo indexes allow multiple images together with captions and optional metadata.

The portrait remains the distinguished representative image whenever appropriate.

---

## 5.2 Stories

Stories remain independent of genealogy records.

Narrative content is stored separately and connected through person identifiers.

This separation allows biographies and historical writing to evolve without increasing the complexity of genealogy data.

---

## 5.3 Historical Documents

Historical documents represent their own archival layer.

Documents are treated as exhibits rather than ordinary images.

Metadata may include:

- title;
- document type;
- date;
- location;
- people;
- source;
- transcription;
- notes.

---

# 6. Presentation Architecture

## Homepage

`index.html` serves as the museum lobby.

It introduces the archive, establishes tone, and provides the primary entry points.

---

## Profile Experience

`tree.html` provides the canonical archival profile.

The filename is a Version 1 legacy name. The page functions as the Person Detail view; renaming it to `details.html` is a Version 2 candidate, not a current architectural change.

The profile is the archive's principal destination and presents the historical life of one individual together with family relationships and supporting archival material.

Stable direct URLs remain an important architectural contract.

```
tree.html?person=Ixxxx
```

---

## Interactive Tree

`family-tree.html`

`js/family-tree.js`

`css/family-tree.css`

together provide the interactive family tree.

The tree consumes prepared JSON, constructs presentation models, calculates layout, routes relationships, and renders SVG.

---

## Presentation Layers

The presentation architecture separates shared visual language from page-specific composition.

Shared visual tokens belong in shared stylesheets.

Page composition belongs in page-specific stylesheets.

This separation minimizes duplication while preserving independence among the archive's major experiences.

---

# 7. Interactive Tree Pipeline

The established layout pipeline is:

```text
buildFamilyViewModel()
        ↓
buildFamilyUnits()
        ↓
measureFamilyUnit()
        ↓
prepareFamilyUnitLayouts()
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

---

## View Model

The view model gathers family information required for presentation without making layout decisions.

---

## Family Units

Family units organize one partnership together with its children.

Family units are the fundamental layout objects.

### Family Unit Order

The chronological order of multiple Family Units is authoritative data,
not a rendering heuristic.

The archive preserves the explicit family order maintained in Gramps
through every stage of the pipeline:

```text
Gramps
    ↓
Ordered FAMS references
    ↓
GEDCOM
    ↓
gedcom_to_json.py
    ↓
family.json
    ↓
archive-data.js
    ↓
Relationship layer
    ↓
Family Tree renderer
```

The exporter preserves the ordered `FAMS` references exactly as written
by Gramps. The relationship layer and renderer consume those ordered
references directly when constructing Family Units.

No chronological inference is performed from:

- Family record identifiers;
- marriage dates;
- creation order; or
- other heuristics.

Historical corrections should therefore be made in Gramps by adjusting
the person's Family order. Once exported, the archive reproduces that
order faithfully without additional interpretation.

This separation of responsibilities is intentional:

- Gramps owns genealogy.
- The exporter preserves genealogy.
- The renderer presents genealogy.

---

## Measurement

Measurement determines required space.

Measurement never determines placement.

---

## Placement

Placement determines card positions while respecting family structure.

---

## Output Models

Card models describe positioned people.

Relationship models describe semantic relationships independently of rendering.

---

## Rendering

Rendering consumes completed geometry.

Rendering should never perform layout decisions.

---

# 8. Relationship Routing

Relationship routing communicates family structure.

Its purpose is understanding rather than geometric efficiency.

Established principles:

- connectors communicate relationship semantics;
- parent, spouse, and child relationships remain visually distinct;
- children descend from a union anchor;
- multiple unions never create ambiguous routing;
- connector crossings never imply relationships;
- relationship routing exists to communicate family structure rather than minimize line length.

Rendering draws paths already determined by the routing layer.

---

# 9. Unknown Relationships

Missing historical information is represented through explicit placeholder records.

Placeholder records participate fully in layout calculations even when they intentionally represent absent historical information.

Placeholders should remain:

- visually restrained;
- structurally meaningful;
- clearly distinguished from real people;
- consistent throughout the archive.

---

# 10. URL and Interaction Contract

The archive preserves stable direct URLs through person query parameters.

Expected behavior includes:

- initial selection from `?person=`;
- browser history integration;
- direct sharing of person URLs;
- graceful fallback for invalid identifiers.

Stable visitor behavior should be preserved during architectural refactoring whenever practical.

---

# 11. Architectural Boundaries

Each architectural layer owns a distinct responsibility.

- **Gramps** owns genealogy editing.
- **Converter scripts** own translation and privacy.
- **JSON** owns browser-consumable structured data.
- **Media indexes** own curated media organization.
- **View models** own presentation context.
- **Family units** own layout grouping.
- **Measurement** owns required space.
- **Layout** owns positioning.
- **Routing** owns connector geometry.
- **Rendering** owns SVG and DOM generation.
- **CSS** owns visual presentation.
- **Documentation** owns institutional knowledge.

Whenever a change crosses multiple responsibilities, it should be divided into smaller independently verifiable changes.

---

# 12. Architectural Principles

The architecture favors:

- explicit responsibilities;
- predictable data flow;
- small composable components;
- separation of genealogy from editorial content;
- separation of layout from rendering;
- backward-compatible public URLs whenever practical;
- evolutionary refactoring rather than wholesale replacement.

Architectural improvements should preserve stable visitor behavior whenever possible.

---

# 13. Architecture Change Policy

Update this document only when:

- a major architectural layer is introduced;
- responsibility moves between components;
- a stable data schema changes materially;
- an established pipeline changes;
- a new architectural responsibility becomes permanent.

Do not update this document for:

- routine bug fixes;
- styling adjustments;
- temporary implementation details;
- release status;
- future feature planning.

Those belong in the Journal, Current Status, or Version 2 Roadmap, as appropriate.
