# The Kallmer Family Archive Journal

## Purpose

This Journal records the project’s evolution: what changed, why it changed, what was learned, and which decisions became durable.

It is not required reading for routine code work. It is the historical record to consult when a decision needs context.

---

## Era I — Establishing Feasibility

### Early July 2026

The project began as an effort to transform a Gramps family tree into a useful public website.

Foundational work included:

- establishing Gramps and GEDCOM as the genealogy workflow;
- building a GEDCOM-to-JSON converter;
- separating public and private output;
- defining living-person privacy rules;
- creating a static family-tree site;
- adding person search;
- adding direct person URLs;
- establishing the initial archival palette and typography.

The central question was whether a private genealogy database could produce a coherent, safe, public family site.

**Lesson:** privacy and conversion belong in the data pipeline, not as improvised browser logic.

---

## Era II — From Tree to Archive

### Mid-July 2026

The project expanded beyond genealogical facts.

Major additions included:

- portrait photographs;
- multiple-photo support;
- person-specific photo indexes;
- full-size photo viewing;
- Markdown stories and biographies;
- story indexes;
- relationship-history display;
- multiple marriages;
- divorce dates and places;
- children grouped by the correct marriage or family union;
- chronological sorting of children and siblings.

During this period, the homepage concept matured into the **museum lobby**.

The project’s identity changed from “a genealogy website” to “a digital family archive organized through genealogy.”

**Established decision:** the profile page is the archival exhibit; the tree is navigation.

**Lesson:** stories, photographs, and documents should remain separate curated layers rather than being forced into genealogy JSON.

---

## Relationship History Milestone

### July 13, 2026

The converter and profile presentation were expanded to support:

- divorce status;
- divorce dates and places;
- family IDs attached to marriages;
- children attached to the correct family union;
- multiple marriages and remarriages.

Real examples, including Floyd Kallmer and Paul Huffey, confirmed that relationship history could be presented without reducing people to database records.

Adoption remained unresolved because the GEDCOM export did not preserve the relationship distinction entered in Gramps.

**Deferred decision:** investigate a better export path or create `relationship-overrides.json`.

---

## Media Architecture Milestone

### Mid-July 2026

Person folders were renamed to include both IDs and readable names. Photo and story indexes were generated.

The archive gained a more durable media convention:

```text
photos/Ixxxx--Full-Name/
stories/Ixxxx--Full-Name/
```

Multiple-photo galleries, captions, consistent photo areas, and full-size overlays were added.

Optional date and location fields beneath photo captions were identified as a future archival improvement.

**Lesson:** curated metadata is part of the exhibit, not merely file organization.

---

## Era III — Interactive Family Navigation

### July 22–24, 2026

A second family-navigation experience was introduced alongside the pedigree/profile page: a zoomable interactive SVG family tree.

Initial work established:

- `family-tree.html`;
- `js/family-tree.js`;
- `css/family-tree.css`;
- selected-person URL handling;
- card drawing;
- connector drawing;
- zoom and pan;
- click-to-center behavior;
- return navigation to the archive.

Early iterations exposed the limitations of positioning relatives around one selected person with hard-coded geometry.

---

## Interactive Tree Visual Stabilization

### Phase 4 — July 24, 2026

The tree’s visual language was refined into a calmer archival composition.

Completed work included:

- a clearer page header;
- archive statistics moved out of the canvas;
- consolidated styling in `css/family-tree.css`;
- minimal person cards;
- removal of visible GEDCOM IDs and role labels;
- restrained selected-card styling;
- muted male, female, and neutral accents;
- lighter connectors;
- straight spouse connectors;
- selective rounded child branches;
- centered parent, couple, and child-row composition;
- reduced spacing and improved generational rhythm.

The William Kallmer family view became the visual reference state.

**Established decisions:**

- cards remain minimal;
- ages do not belong on tree cards;
- the tree is for orientation;
- unknown ancestors should eventually use faded placeholders;
- pixel tuning should stop until the layout architecture is improved.

**Architectural conclusion:** the primary layout object is not an isolated selected person. It is a family unit.

---

## Family-Unit Architecture

### Phase 5 — July 24, 2026

The tree layout was refactored without intentionally changing its visible result.

The new pipeline introduced:

- `buildFamilyUnits`;
- `measureFamilyUnit`;
- `measureFamilyUnits`;
- `layoutPrimaryFamily`;
- `layoutFamilyUnit`;
- `layoutFamilyUnits`;
- `buildCardModel`;
- `buildRelationshipModel`;
- `calculateLayoutBounds`.

`buildLayout` became a coordinator.

Family units now explicitly contain:

```text
id
union
primaryPerson
spouse
children
isPrimary
measurements
```

**Major lesson:** successful refactoring came from moving one responsibility at a time while preserving a working browser state.

The development workflow matured during this milestone:

- print the exact current block with `sed`;
- edit with guarded Python replacement;
- run `node --check`;
- inspect the diff;
- hard-refresh;
- verify no unintended visual change;
- stage only intended files;
- commit one architectural idea at a time.

This workflow became part of the project’s permanent engineering culture.

---

## Connector Routing Observation

### End of Phase 5

Testing the Andrew Christ Kallmer family exposed small connector irregularities:

- asymmetry around union connectors;
- occasional S-shaped bends;
- inconsistent elbow radii;
- unnecessary sideways jogs in some descendant lines.

These were classified as routing-polish issues rather than evidence that the family-unit layout was wrong.

**Deferred decision:** do not polish connector geometry until visible behavior and multiple-union layout stabilize.

**Proposed architecture:** introduce one Family Routing Node per family unit to own union centers, junctions, trunks, elbows, and connector paths.

---

## Era IV — Relationship Grammar

### Phase 6 Planning — July 24, 2026

The project moved from structural refactoring toward defining the visual grammar of relationships.

The Family Tree Layout Constitution was written with these principles:

- one person, one card;
- one union, one family unit;
- children belong to unions;
- chronology should be visible;
- every connector has one meaning;
- crossings do not imply connection;
- secondary unions route around descendant areas;
- whitespace carries structure;
- comprehension outranks compactness;
- real edge cases are the test.

Strong next capabilities were identified:

- faded unknown-parent or spouse placeholders;
- improved multiple-marriage layout;
- cleaner routing for large child groups;
- better mobile fit and initial zoom;
- wider descendant layouts;
- later connector and animation polish.

The recommended next step was to inspect difficult real families and choose one visible limitation rather than beginning another abstract refactor.

---

## Documentation Milestone

### July 25, 2026

The accumulated journals and handoffs had become repetitive and increasingly difficult to use as current guidance.

The project adopted a new documentation architecture:

```text
docs/
├── 00-Project-Guide.md
├── 01-Constitution.md
├── 02-Architecture.md
├── 03-Engineering-Guide.md
├── 04-Journal.md
└── 99-Current-Status.md
```

The goals were:

- one short required orientation file;
- stable principles separated from software structure;
- working method separated from historical narrative;
- one concise current-state file;
- removal of completed roadmap items from active handoffs;
- preservation of project reasoning without requiring every old handoff.

**Established decision:** documentation should optimize retrieval, not merely completeness.

**Established decision:** these are repository documents, not chat artifacts.

---

## Completed Milestones

The following are established capabilities and should not remain listed as “future work”:

- GEDCOM conversion;
- public and private JSON output;
- living-person privacy;
- person search;
- normalized diacritic search;
- direct person URLs;
- pedigree view;
- portraits;
- multiple-photo galleries;
- photo indexes and captions;
- story and biography support;
- story indexes;
- relationship history;
- multiple marriages;
- divorce display;
- children grouped by union;
- chronological child and sibling sorting;
- interactive SVG family tree;
- zoom and pan;
- click-to-center;
- archival tree-card language;
- family-unit layout architecture.

---

## Open Long-Term Threads

These remain legitimate future work:

- historical document exhibits;
- optional date and location photo metadata;
- featured ancestor and historical photograph homepage modules;
- timeline view;
- adoption and relationship override support;
- stronger multiple-union layout;
- unknown relationship placeholders;
- mobile tree behavior;
- routing nodes and connector polish;
- keyboard navigation;
- optional subtree expansion or collapse.

The order should continue to be determined by real archive needs and visible limitations rather than by feature accumulation.

---

## Unified Archive Navigation

### July 26, 2026

The project crossed an important threshold during this session. The Interactive Family Tree and the Person Details page ceased to behave like separate applications and instead became two complementary views into the same archive.

The work focused less on adding new features and more on reducing friction between existing ones.

Completed work included:

- reciprocal navigation between Family Tree and Person Details;
- preservation of the selected person while switching views;
- matching archive headers;
- synchronized archive statistics;
- archive search integrated into the Family Tree;
- search synchronized with the currently selected person;
- destination-colored navigation buttons;
- consistent header spacing, typography, and geometry across both pages.

Several visual refinements were made before considering the work complete. Rather than accepting two similar pages, the goal became making them feel like different perspectives on the same archival collection.

A small but intentional visual language emerged:

- **Tree View** uses a muted blue identity, emphasizing navigation and relationships.
- **Person Details** uses the established homestead clay identity, emphasizing the archival exhibit.

This distinction allows visitors to understand where they are without changing the overall visual character of the archive.

### Architectural Direction

This milestone also represents a change in the project's priorities.

Earlier work concentrated on building visible capabilities:

- genealogy conversion;
- photographs;
- stories;
- relationship history;
- the interactive tree;
- family-unit layout.

The next phase shifts toward **shared infrastructure**.

Rather than adding another independent feature, the archive will begin extracting reusable components shared across the entire site.

The first of these will be a common archive-search component serving:

- homepage;
- Family Tree;
- Person Details.

Future shared components will likely include:

- common page headers;
- Featured Person panels;
- archive navigation elements;
- shared visual tokens.

### Lessons Learned

Several ideas became reinforced during this milestone.

**The archive is one application.**

Switching between Tree and Details should feel like changing viewpoints rather than navigating between different pages.

**Consistency reduces complexity.**

Matching headers, spacing, navigation, and search behavior simplify the user experience without introducing new features.

**Architecture should follow stability.**

The project is now mature enough that effort can increasingly shift from creating pages toward extracting reusable components.

### Established Decisions

The following decisions should now be considered part of the project's stable direction:

- Tree and Person Details remain reciprocal views of the same archive.
- Tree View retains its muted blue visual identity.
- Person Details retains its homestead clay identity.
- Search behavior should become a shared archive capability rather than page-specific code.
- Future refactoring should favor shared components over duplicated implementations.
- Major architectural changes continue to follow the established workflow:
  - inspect current local code;
  - one guarded edit;
  - `node --check`;
  - inspect the diff;
  - browser verification;
  - one meaningful commit.

This milestone marks the beginning of the archive's transition from feature development toward long-term architectural refinement.

---

## Shared Archive Infrastructure

### July 27, 2026

The project reached another architectural milestone by beginning the extraction of shared infrastructure from page-specific implementations.

Completed work included:

- creation of a shared `archive-search.css`;
- creation of a shared `archive-search.js` scaffold;
- migration of the Family Tree to the shared search stylesheet;
- migration of the Person Details page to the shared search stylesheet;
- three small, independently verified architectural commits with no intentional visual change.

Rather than adding another visible capability, this work reduced duplication and established the foundation for reusable archive components.

### Established Direction

This session also clarified an important development principle.

Architecture and visual language should now evolve independently.

Shared infrastructure should continue to be completed before beginning a dedicated visual-polish phase. This keeps commits focused on one concern, reduces regression risk, and allows visual decisions to be evaluated across the archive rather than page by page.

This milestone represents the archive's transition from primarily adding features toward strengthening long-term maintainability.
