# Current Status

**Updated:** 2026-07-25

## Repository

`https://github.com/ticotexas/kallmer-family-tree`

## Current Branch

`feature/family-unit-layout`

Confirm the local branch before editing:

```bash
git branch --show-current
git status --short
```

## Current Milestone

**Interactive Tree — Relationship Grammar and Visible Capability**

The family-unit architectural refactor is complete and was browser-tested, committed, and pushed.

The next work should improve one visible limitation using the existing architecture rather than beginning another broad refactor.

## Current Architecture

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

`buildLayout(model)` is now a compact coordinator.

## Stable Visual Contract

Preserve unless the active task explicitly changes it:

- parchment background;
- archive header;
- minimal person cards;
- muted male, female, and neutral accents;
- restrained selected-card styling;
- selected-card profile link;
- light relationship connectors;
- straight spouse links;
- selective rounded descendant branches;
- click-to-center;
- direct person query URLs;
- browser-history behavior.

## Recommended Next Action

Inspect the current local interactive tree with one or two difficult real families.

Good test cases include:

- a person with multiple marriages;
- a family with many children;
- a person with an unknown parent or spouse;
- the Andrew Christ Kallmer family, where minor connector irregularities were observed.

Choose one concrete visible limitation and change the smallest responsible helper.

Strong candidates:

1. faded unknown-parent or spouse placeholders;
2. improved multiple-union layout;
3. better initial mobile fit;
4. wider descendant placement for large child groups.

## Planned Experience Backlog

These items remain part of the intended archive and should not be lost, although they are not all part of the next coding change.

### Interactive Tree

- faded, dashed unknown-parent and unknown-spouse placeholders;
- improved multiple-union placement;
- wider descendant layouts for large families;
- better initial mobile fit and touch behavior;
- restrained card movement and recenter animation after geometry stabilizes;
- `prefers-reduced-motion` support;
- later connector-routing polish;
- possible keyboard navigation;
- possible subtree expansion or collapse.

### Homepage

- rotating Featured Person or Featured Ancestor;
- a “From the Archive” feature for a historical photograph, document, or story;
- homepage search or another direct discovery entry point;
- preserve the homepage as the museum lobby rather than a data dashboard.

### Person Profile

- continue evolving the profile into the archive’s centerpiece;
- retain support for existing `tree.html?person=Ixxxx` links while that design evolves;
- integrate historical documents as exhibits;
- consider a person-centered timeline;
- display optional photo date and location metadata beneath captions.

### Site Architecture

- incrementally extract shared visual tokens and common components from inline page styles;
- prefer a shared `css/archive.css` plus focused page stylesheets rather than one all-purpose master file;
- preserve `css/family-tree.css` as the interactive-tree stylesheet;
- eventually support a fuller private archive alongside the public privacy-reduced site.

## Deferred Work

### Connector Polish

Do not enter a broad connector-polish pass until layout behavior is stable.

Observed issues include:

- union asymmetry;
- S-shaped bends;
- inconsistent elbow radii;
- unnecessary descendant jogs.

Proposed future architecture:

- one Family Routing Node per family unit;
- cards determine positions;
- routing nodes determine path geometry;
- rendering draws completed paths.

### Adoption

Adoption entered in Gramps is not reliably preserved through the current GEDCOM path.

Potential future solutions:

- improved export;
- `relationship-overrides.json`.

## Required Work Process

1. Print the exact current local function or block with `sed`.
2. Use one guarded edit.
3. Run:

```bash
node --check js/family-tree.js
```

4. Inspect:

```bash
git --no-pager diff -- js/family-tree.js
```

5. Hard-refresh and verify the browser.
6. Confirm unrelated visual behavior remains unchanged.
7. Stage only intended files.
8. Commit one meaningful change.
9. Push.
10. Confirm `git status --short`.

Do not use `git add .`.

## Documentation Action

Add the six Version 1 documents to `docs/` in one documentation-only commit.

Suggested commit message:

```text
Add project constitution and engineering documentation
```

Before committing, inspect:

```bash
git status --short
git --no-pager diff -- docs/
```

Then stage only:

```bash
git add docs/
```

## Stopping Point

The documentation set is ready to become the canonical project guide.

The implementation is ready for the next visible interactive-tree capability after the documentation commit is complete.

# Current Status

**Updated:** 2026-07-26

## Repository

`https://github.com/ticotexas/kallmer-family-tree`

## Current Branch

`feature/family-unit-layout`

Confirm the local branch before editing:

```bash
git branch --show-current
git status --short
```

## Current Milestone

**Unified Archive Navigation**

The Family Unit architecture is complete and stable.

The archive now presents two reciprocal views of the same data:

- **Family Tree** — relationship-oriented navigation.
- **Person Details** — the archival exhibit.

Completed this milestone:

- reciprocal navigation between Tree and Details;
- matching archive headers;
- synchronized archive statistics;
- archive search in the Family Tree;
- preserved selected person while switching views;
- synchronized browser history and person URLs;
- synchronized search field with the selected person;
- destination-colored navigation buttons;
- consistent header spacing, typography, and geometry.

The project is now transitioning from feature development toward shared infrastructure.

The next architectural objective is to extract the duplicated archive-search implementation into one shared component used by the homepage, Family Tree, and Person Details.

## Current Architecture

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

`buildLayout(model)` remains a compact coordinator.

## Stable Visual Contract

Preserve unless the active task explicitly changes it:

- parchment background;
- archive header;
- consistent archive typography;
- matching Tree and Detail page headers;
- minimal person cards;
- muted male, female, and neutral accents;
- restrained selected-card styling;
- selected-card profile link;
- light relationship connectors;
- straight spouse links;
- selective rounded descendant branches;
- click-to-center;
- synchronized search behavior;
- direct person query URLs;
- browser-history behavior;
- destination-colored navigation:
  - Tree View = muted blue;
  - Detail View = homestead clay.

## Recommended Next Action

Extract the duplicated archive-search implementation into a shared component.

One search implementation should serve:

- homepage;
- Family Tree;
- Person Details.

After search is shared:

1. Add a deterministic Featured Person panel to the homepage.
2. Continue treating the homepage as the museum lobby rather than a dashboard.
3. Rename `tree.html` to `detail.html` in a dedicated refactoring commit while preserving existing URLs.

Each architectural change should remain isolated to one commit.

## Planned Experience Backlog

These items remain part of the intended archive and should not be lost, although they are not all part of the next coding change.

### Interactive Tree

- faded, dashed unknown-parent and unknown-spouse placeholders;
- improved multiple-union placement;
- wider descendant layouts for large families;
- better initial mobile fit and touch behavior;
- restrained card movement and recenter animation after geometry stabilizes;
- `prefers-reduced-motion` support;
- later connector-routing polish;
- possible keyboard navigation;
- possible subtree expansion or collapse.

### Homepage

- shared archive search;
- deterministic Featured Person panel;
- "From the Archive" feature for a historical photograph, document, or story;
- preserve the homepage as the museum lobby rather than a data dashboard.

### Person Profile

- continue evolving the profile into the archive's centerpiece;
- retain support for existing `tree.html?person=Ixxxx` links while that design evolves;
- integrate historical documents as exhibits;
- consider a person-centered timeline;
- display optional photo date and location metadata beneath captions.

### Site Architecture

- extract shared archive search;
- incrementally extract shared visual tokens and reusable UI components;
- prefer shared components rather than duplicated page implementations;
- preserve `css/family-tree.css` as the interactive-tree stylesheet;
- eventually support a fuller private archive alongside the public privacy-reduced site;
- later rename `tree.html` to `detail.html`.

## Deferred Work

### Connector Polish

Do not enter a broad connector-polish pass until layout behavior is stable.

Observed issues include:

- union asymmetry;
- S-shaped bends;
- inconsistent elbow radii;
- unnecessary descendant jogs.

Proposed future architecture:

- one Family Routing Node per family unit;
- cards determine positions;
- routing nodes determine path geometry;
- rendering draws completed paths.

### Adoption

Adoption entered in Gramps is not reliably preserved through the current GEDCOM path.

Potential future solutions:

- improved export;
- `relationship-overrides.json`.

## Required Work Process

1. Print the exact current local function or block with `sed`.
2. Use one guarded edit.
3. Run:

```bash
node --check js/family-tree.js
```

4. Inspect:

```bash
git --no-pager diff -- js/family-tree.js
```

5. Hard-refresh and verify the browser.
6. Confirm unrelated visual behavior remains unchanged.
7. Stage only intended files.
8. Commit one meaningful architectural change.
9. Push.
10. Confirm `git status --short`.

Do not use `git add .`.

## Documentation Action

The six project documents now form the canonical project documentation.

Update them intentionally as architecture evolves rather than creating new handoff files.

Documentation should explain:

- enduring principles;
- current architecture;
- engineering workflow;
- historical decisions;
- present project status.

Avoid allowing completed roadmap items to accumulate in `99-Current-Status.md`.

## Stopping Point

The Family Tree and Person Details views now function as reciprocal interfaces into the same archive.

The next milestone is to build shared archive infrastructure, beginning with a reusable search component that serves the homepage, Family Tree, and Person Details.

## Planned Visual Polish

Visual refinement is intentionally deferred until the shared archive-search component has been fully extracted.

Rather than making isolated cosmetic adjustments, the archive should receive one dedicated visual-polish pass after the shared infrastructure is complete.

Objectives include:

- establish a unified interaction language across the archive;
- evaluate archival color inversion in place of modern lift/shadow hover effects where appropriate;
- standardize transitions and animation timing;
- standardize keyboard focus states;
- review buttons, links, search controls, and navigation together;
- postpone connector-routing polish until layout behavior has stabilized.

Avoid piecemeal visual tweaks before the infrastructure phase is complete.

---

# Current Status

**Updated:** 2026-07-27

## Current Milestone

**Shared Archive Infrastructure — Phase 1 Complete**

The archive's first reusable application component has been completed.

Finished this milestone:

- shared `archive-search.css`;
- shared `archive-search.js`;
- shared text normalization;
- shared alternate-name indexing;
- shared search index;
- shared search query engine;
- Family Tree migrated to the shared implementation;
- Canonical Edit Cycle adopted as the required engineering workflow.

The search system now has a single owner and future search improvements can be implemented once rather than separately on each page.

## Current Architectural Direction

The project is now moving from shared search toward a shared archive data layer.

The next reusable component should centralize archive data access, including:

- `peopleById`;
- `familiesById`;
- parent lookup;
- spouse-family lookup;
- relationship helpers;
- sibling lookup.

The long-term objective is for page-specific code to concentrate on presentation while shared infrastructure owns archive behavior.

## Recommended Next Action

Begin designing an `ArchiveData` component that becomes the common data layer for:

- homepage;
- Family Tree;
- Person Details.

As with the search extraction, migration should occur one responsibility at a time with independently verifiable commits.

## Stable Engineering Process

The Canonical Edit Cycle is now considered part of the project's permanent engineering practice.

Every implementation should:

1. capture the exact current local source;
2. perform one guarded replacement;
3. verify with `node --check`;
4. inspect `git --no-pager diff`;
5. verify in the browser;
6. commit one meaningful architectural change.

This workflow should be followed for all future implementation sessions.

### Relationship Presentation (2026-07-27)

The relationship presentation model has been simplified and centralized.

Current behavior:

- Marriage labels are owned by the selected individual rather than spouse cards.
- Multiple marriages are displayed as a stacked relationship block beneath the selected person's life dates.
- Spouse cards remain intentionally minimal, showing only identity information (name and life years).
- Marriage labels now omit the redundant "widowed" suffix while continuing to distinguish divorce and ongoing marriages.
- Selected-card spacing has been refined so relationship information forms its own visual section without crowding the profile link.

This architecture better reflects the underlying family-unit model and establishes a clean foundation for future connector improvements.

#### Next Milestone

Chronological family-unit routing:

1. Sort family units by marriage date.
2. Give each marriage its own independent visual descent.
3. Prevent later marriage connectors from appearing connected to earlier family child buses.
4. Preserve all existing visual language and interaction behavior.

## Marriage Lane Architecture

Current family-unit rendering uses independent relationship objects.

Chronological ordering determines:

- spouse ordering
- marriage labels
- exit positions from the selected person

Connector routing is handled independently.

The renderer now stacks routing corridors independently of chronological order, allowing longer routes to occupy outer lanes and preventing connector crossings without introducing a shared marriage bus.

This architecture successfully supports one, two, and three marriages using the same rendering code.

### Current priorities

The family-unit architecture is considered stable.

Future work should focus on visual polish rather than structural redesign:

- connector refinement
- typography and card composition
- large-family stress testing
- overall composition and spacing
- subtle animation after layout stabilization

## Current Status — 2026-07-27

### Homepage Polish Complete

The homepage has been refined into a museum-style archive entrance.

Completed:

- Featured archive person presentation.
- Portrait loading from existing photo indexes.
- Photo caption display.
- Featured person lifespan calculation.
- Direct profile navigation.
- Featured profile button styling.
- Improved homepage vertical composition.
- Refined exhibit heading hierarchy.
- Improved spacing between featured person and archive statistics.

Current homepage behavior:

- Landing page introduces the archive.
- Featured person demonstrates that the archive contains real lives and photographs.
- Visitors can immediately enter an individual's profile.
- Visitors can continue into the interactive tree.

Visual language preserved:

- parchment background
- ledger ink primary text
- prairie sage archival metadata
- homestead clay actions
- restrained typography
- no dashboard/card aesthetic

---

## Next Phase: Interactive Tree Visual Polish

Architecture remains stable.

Do not redesign:

- family-unit model
- relationship objects
- layout pipeline
- routing/history behavior

Next work should focus on presentation only:

Priority candidates:

1. Connector geometry refinement.
   - smoother paths
   - consistent shoulders
   - cleaner marriage/child routing

2. Large family stress testing.
   - 6+ children
   - 10+ children
   - multiple marriage cases
   - crowded branches

3. Card and spacing refinement.
   - visual rhythm
   - alignment
   - typography balance

4. Subtle animation.
   - transitions only
   - preserve archival restraint

Continue canonical Engineering Guide workflow:

- inspect current local code
- use xclip capture workflow
- guarded replacements
- node --check
- git --no-pager diff
- browser verification
- one meaningful change per commit

---

## Current Status — Interactive Family Tree Complete

The current Interactive Family Tree development phase is complete.

### Stable capabilities

- measured family-unit layout;
- chronological multiple-marriage ordering;
- independent noncrossing marriage lanes;
- correct child association by family;
- multi-row large-family layout;
- divorce metadata and visual presentation;
- unknown spouse and missing-parent placeholders;
- direct person URLs;
- browser back/forward support;
- click-to-recenter behavior;
- selected-card profile navigation;
- family-specific adopted-parent relationships;
- restrained `Adopted` annotations on applicable child cards.

### Adoption architecture

Exceptional parent-child relationships are exported as family-specific metadata:

```json
{
  "family": "F0022",
  "type": "adopted"
}
```

```

```
