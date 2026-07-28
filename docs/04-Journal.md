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

---

## Shared Archive Search Completion

### July 27, 2026

The archive completed its first extraction of a reusable application component.

Until this milestone, each page owned its own search implementation, including text normalization, alternate-name indexing, search indexing, and query behavior. Although the implementations remained visually consistent, they duplicated logic and would have become increasingly difficult to evolve together.

The search system was extracted incrementally through five independently verified architectural commits:

1. Shared archive-search foundation.
2. Shared search indexing.
3. Shared search query engine.
4. Alternate-name indexing.
5. Family Tree migration to the shared implementation.

Every step preserved browser functionality and intentionally avoided visible behavior changes. Each commit completed one architectural responsibility before introducing the next.

The resulting ownership became much clearer:

```
archive-search.js
    • normalization
    • alternate-name collection
    • search indexing
    • search queries
    • person lookup

family-tree.js
    • search UI
    • rendering
    • navigation
```

This session also validated the project's Canonical Edit Cycle.

Every implementation followed the same sequence:

- capture the current local source;
- perform one guarded replacement;
- verify with `node --check`;
- inspect `git --no-pager diff`;
- verify in the browser;
- commit one meaningful architectural change.

Rather than serving only as a safety procedure, this workflow has become part of the project's architecture. Small, independently verifiable commits now define how major refactoring should proceed.

This milestone marks the archive's transition from extracting one shared component to establishing a repeatable method for future shared infrastructure.

---

## 2026-07-27 — Relationship Metadata Refinement

### Summary

Continued refinement of the Interactive Family Tree with a focus on family-unit ownership and archival presentation rather than new layout capabilities.

### Completed

- Simplified marriage end labels by removing the redundant "· widowed" suffix.
  - Marriage labels now display:
    - `m. 1941–2004`
    - `m. 1941–1957 · divorced`
    - `m. 1982–present`
    - `m. 1941–?`

- Refactored relationship metadata ownership.
  - Marriage information is no longer attached to spouse cards.
  - The selected individual now owns all relationship labels for their family units.
  - Multiple marriages are rendered as a relationship block beneath the selected person's life dates.

- Simplified spouse cards.
  - Secondary spouse cards once again contain only:
    - name
    - life years
  - This restores the minimal archival card design established earlier in the project.

- Refined typography and spacing for the selected card.
  - Added additional vertical spacing between life dates, relationship lines, and the "View Profile" link.
  - Increased selected-card height only when relationship labels are present.
  - The relationship block now reads as its own visual section rather than appearing crowded.

### Architectural Notes

This change intentionally separates _family relationship metadata_ from _individual cards_. The selected individual now serves as the single presentation point for marriage history, while spouse cards remain focused solely on representing individuals.

This provides a cleaner foundation for future relationship rendering, including chronological marriage lanes and family-unit routing improvements.

### Next Planned Work

- Sort family units chronologically by marriage date.
- Introduce independent marriage spines for each family unit.
- Prevent later marriage connectors from visually joining earlier child buses.
- Preserve the existing archival visual language while improving readability for multiple marriages.

## 2026-07-27 — Independent Marriage Lanes

Completed a major refinement of multi-marriage rendering.

### Architectural changes

- Family units are now sorted chronologically by marriage year.
- Each marriage renders as its own independent `family-unit` relationship rather than participating in a shared marriage bus.
- Marriage order is preserved throughout the layout pipeline and exposed to the renderer.

### Rendering improvements

- Each marriage now exits the selected person's card independently.
- Relationship routing was separated conceptually into:
  - exit geometry (where a relationship leaves the owner card), and
  - routing geometry (how connectors travel toward spouses).
- This separation eliminated coupling between chronological ordering and connector routing.

### Noncrossing lane refinement

Initial testing with a temporary third spouse revealed that independent exits alone could still produce connector crossings.

Rather than changing spouse order or reintroducing a shared bus, the routing algorithm was refined by reversing only the vertical corridor stacking order while preserving chronological spouse order and exit positions.

This produces nested, noncrossing relationship corridors while maintaining completely independent family units.

### Validation

Verified visually with:

- one marriage
- two marriages
- temporary three-marriage stress test

The same renderer handled all cases without additional branching logic.

## 2026-07-27 — Homepage Featured Archive Exhibit Polish

The homepage was refined from a simple archive entry page into a curated archival introduction.

Completed:

- Added a "From the Archive" featured person exhibit area.
- Featured people now display only from the existing photo archive.
- Featured portrait loads from the person's photo index.
- Featured photo captions are displayed from photo metadata.
- Added featured person lifespan display:
  - birth year
  - death year
  - calculated lifespan in years.
- Added direct "View Profile" entry point using existing person URL routing.
- Styled the featured profile action using the established homestead clay button language.
- Reduced homepage top padding to improve title-page composition.
- Refined "From the Archive" as a quieter archival label using prairie sage.
- Added museum-style caption treatment for featured photographs.
- Added spacing between the featured exhibit and archive statistics.

Design decisions preserved:

- Homepage remains restrained and archival.
- No cards, shadows, borders, or modern dashboard styling were introduced.
- The photograph remains the visual artifact.
- Orange/clay remains reserved for actions.
- Sage remains reserved for metadata and archival labels.

The homepage now establishes a clear visitor path:

Archive identity →
featured ancestor →
portrait artifact →
profile →
archive exploration

The homepage polish phase is considered complete.

Next focus:
Interactive family tree visual polish.

## 2026-07-27 — Divorce and Adoption Relationship Presentation

Completed the final relationship-presentation work for the current Interactive Family Tree phase.

### Divorce presentation

- Carried divorce state from family data into the relationship model.
- Refined divorced-family connector geometry.
- Added a restrained break marker to distinguish a dissolved marriage without changing the archival connector language.
- Preserved independent family-unit lanes and chronological marriage ordering.

### Adoption data model

Investigated the source GEDCOM and confirmed that adoption is represented as family-specific parent-child metadata:

```gedcom
1 FAMC @F0022@
2 PEDI adopted
```

## 2026-07-28 — Relationship Presentation & Browser History Polish

### Summary

Focused on release-readiness refinement rather than new capabilities. Two user-facing inconsistencies were identified and corrected.

### Relationship Presentation

Implemented consistent presentation of exceptional parent-child relationships throughout the archive.

Changes:

- Children lists now display family-specific relationship labels (Adopted, Foster, Step) where applicable.
- Current Family cards in the pedigree now display exceptional parent relationships for the selected individual.
- Person Details now displays exceptional parent relationships beneath the Parents section.
- Relationship labels use restrained archival styling (italic IBM Plex Mono, muted sage) so they remain informative without competing with primary genealogical information.

Result:

Relationship metadata is now presented consistently across:

- Interactive Tree
- Pedigree Current Family
- Person Details
- Children lists

### Browser History

Restored proper browser history behavior for Person Details.

Implemented three navigation modes:

- push — user navigation
- replace — initial page load
- none — browser Back/Forward restoration

Added:

- URL-based person resolver
- popstate handler
- correct pushState/replaceState separation

Result:

- Back/Forward navigation now mirrors Interactive Tree behavior.
- Direct URLs continue to work.
- Reload preserves the current individual.
- Navigation no longer rewrites a single history entry.

### Notes

These changes continue the Release Readiness phase by improving consistency, correctness, and expected browser behavior without changing the underlying archive architecture.

## 2026-07-28 — Release Readiness: Accessibility and Interaction Consistency

Continued Release Readiness with two focused usability improvements.

### Keyboard Accessibility

Improved keyboard navigation within the Interactive Tree.

Changes:

- Removed the currently selected person card from the keyboard tab order.
- Preserved keyboard navigation for all non-selected person cards.
- Kept the selected card's "View Profile" action as the primary keyboard target.
- Added a visible focus indicator to the Details View button while preserving existing hover behavior.

This eliminates a redundant keyboard stop and produces a clearer, more logical navigation sequence.

### Interaction Consistency

Unified person-selection transitions between the Interactive Tree and Details View.

Implemented:

- Matching 170 ms fade transition.
- Shared reduced-motion behavior using `prefers-reduced-motion`.
- Protection against interrupted rapid transitions.
- Initial page load remains immediate without animation.

The archive now presents a consistent interaction language when navigating between people across both primary views.

No architectural changes were made.

## 2026-07-28 — Mobile Interactive Tree Readiness

Continued release-readiness work on the interactive tree with a focus on mobile usability.

### Investigation

Performed responsive testing at approximately 390 px viewport width. The existing SVG correctly displayed the entire family unit but reduced the tree enough that person names and dates became difficult to read. An initial attempt to solve this by computing a reduced "primary family" viewBox improved framing but did not materially improve readability and was discarded rather than committed.

### Final Implementation

Adopted a readability-first mobile strategy instead of a fit-everything strategy.

Implemented:

- Mobile-only readable SVG rendering scale.
- Automatic centering of the selected person after rendering.
- Scrollable mobile tree viewport.
- Pointer drag panning for mouse and touch devices.
- Drag threshold to avoid accidental person selection while panning.
- Preservation of ordinary click behavior when not dragging.
- Additional bottom scroll space to ensure the lowest generation remains reachable.

Desktop behavior, layout, and presentation remain unchanged.

### Validation

Verified:

- JavaScript syntax (`node --check`).
- Mobile rendering at phone-sized viewport.
- Readable card typography.
- Horizontal and vertical panning.
- Automatic recentering after selecting another individual.
- View Profile links remain functional.
- Browser history behavior preserved.
- Desktop presentation unchanged.

Committed:

43d8905 Improve mobile family tree navigation

This substantially improves usability for phones without altering the established desktop presentation.

## 2026-07-28 — Release Candidate Age Accuracy and Privacy

Completed the final release-candidate correction discovered during public-site QA.

### Issue

The Person Details view calculated ages by subtracting birth year from death year or the current year.

This produced incorrect results when the person had not yet reached their birthday during the relevant year.

Examples discovered during QA:

- Dorcas McPherrin displayed as age 100 rather than 99.
- Timothy Kallmer displayed as age 57 rather than 56 before his October birthday.

The public archive intentionally exposes only birth years for living people, so the browser did not have enough information to calculate exact living ages.

### Exporter Solution

Updated `tools/gedcom_to_json.py` to calculate exact ages for living people while the full private birth date is still available during conversion.

The public record now includes a privacy-safe numeric field such as:

```json
"birth": "1969",
"age": 56
```
