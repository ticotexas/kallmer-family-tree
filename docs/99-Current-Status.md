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
