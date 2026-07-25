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
