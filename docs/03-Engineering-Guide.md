# The Kallmer Family Archive Engineering Guide

---

# 1. Purpose

This guide defines the engineering practices used to develop the Kallmer Family Archive safely, predictably, and incrementally.

It is not a generic programming guide. It records the working methods that have proven reliable for this repository and this collaboration.

The Engineering Guide explains **how changes are made**.

The Constitution explains **why**.

The Architecture explains **where responsibilities belong**.

---

# 2. Engineering Principles

Every engineering decision should preserve the archive's long-term stability.

Established principles:

- Always work from the user's current local repository.
- Preserve stable visitor behavior whenever practical.
- Make one meaningful change per commit.
- Prefer small, reversible improvements.
- Verify every change before continuing.
- Separate architectural work from visual polish whenever possible.
- Preserve institutional knowledge through documentation.

Engineering should improve maintainability without unnecessarily changing the visitor experience.

---

# 3. Primary Rule

**Always work from the user's current local files.**

Uploaded files, previous conversations, remembered code, and documentation examples may all be stale.

Before modifying code, inspect the exact current implementation from the user's repository.

Example:

```bash
sed -n '/function buildLayout/,/function drawCards/p' js/family-tree.js
```

The printed local source is authoritative.

---

# 4. Change Scope

Each commit should implement one meaningful idea.

Examples include:

- extracting one responsibility;
- improving one layout behavior;
- adding one data field;
- correcting one rendering rule;
- improving one coherent visual system.

Avoid combining unrelated work such as:

- architecture;
- photographs;
- regenerated data;
- unrelated styling;
- speculative cleanup.

Focused commits improve review, diagnosis, reversal, and project history.

---

# 5. Canonical Development Workflow

Every implementation follows the same engineering cycle.

---

## Step 1 — Capture Current Source

Never edit from memory.

Capture the current local implementation.

Preferred workflow:

```bash
id="descriptive-operation"

{
  sed -n '/START_PATTERN/,/END_PATTERN/p' path/to/file
} | tee /tmp/${id}.txt | xclip -selection clipboard
```

For numbered excerpts:

```bash
id="descriptive-operation"

{
  nl -ba path/to/file | sed -n '420,620p'
} | tee /tmp/${id}.txt | xclip -selection clipboard
```

This workflow guarantees that:

- ChatGPT reviews the exact current implementation;
- `/tmp` preserves an identical snapshot;
- the clipboard contains the same text for immediate pasting.

---

## Step 2 — Guarded Replacement

Generate guarded Python replacements using `pathlib`.

Every replacement should:

- read the current file;
- match the captured source exactly;
- stop if the expected block is absent;
- replace only once;
- write the updated file.

Example:

```python
from pathlib import Path

path = Path("js/family-tree.js")
text = path.read_text()

old = """CURRENT BLOCK"""
new = """REPLACEMENT BLOCK"""

if old not in text:
    raise SystemExit("Stopped: expected block not found.")

text = text.replace(old, new, 1)
path.write_text(text)
```

Guarded replacements are preferred because they fail safely.

---

## Step 3 — Verify

After every JavaScript edit:

```bash
node --check js/family-tree.js
```

Then inspect only the intended changes:

```bash
git --no-pager diff -- js/family-tree.js
```

Review before opening the browser.

---

## Step 4 — Browser Review

For visible changes:

1. Hard refresh.
2. Verify the requested behavior.
3. Verify unrelated behavior remains unchanged.
4. Test direct URLs when appropriate.
5. Test at least one difficult real family example.
6. Test desktop and mobile when layout changes.

Review one category at a time:

- geometry;
- typography;
- connectors;
- interaction;
- data;
- privacy.

---

## Step 5 — Commit

Before staging:

```bash
git status --short
git --no-pager diff
```

Stage only intended files.

Prefer:

```bash
git add specific-file
```

rather than:

```bash
git add .
```

unless every modified file belongs in the commit.

Each commit should describe one complete, reviewable idea.

Examples:

- Extract family-unit measurement from layout
- Improve mobile tree fit
- Group children by marriage
- Add unknown-parent placeholders

Avoid vague commit messages.

---

# 6. Architectural Refactoring

During architectural work:

- preserve visual behavior unless intentional;
- avoid pixel tuning while responsibilities move;
- extract one responsibility at a time;
- keep the browser working after every step;
- stop extracting once ownership is clear.

Extract helpers because they establish responsibility—not simply because functions become shorter.

---

# 7. Visual Development

The archive's established visual contract includes:

- restrained archival appearance;
- parchment backgrounds;
- calm typography;
- minimal person cards;
- muted gender or neutral accents;
- light relationship lines;
- direct profile navigation.

When modifying visuals:

- identify one clear objective;
- change the smallest responsible rule;
- compare against the current successful presentation;
- preserve the archive's visual language.

Interactive tree styling belongs in `css/family-tree.css`.

---

# 8. Data and Media

## Converter Work

When modifying the converter:

1. inspect the current source;
2. make one schema or privacy change;
3. verify compilation;
4. regenerate intentionally;
5. inspect representative records;
6. confirm public privacy;
7. review generated diffs.

Generated JSON should not be hand-edited except as part of an intentionally designed override system.

---

## Media

Photographs, stories, and historical documents should be committed in coherent groups.

Verify:

- folder naming;
- person identifiers;
- index ordering;
- captions;
- portrait selection;
- public suitability.

Avoid combining media work with layout-engine development.

---

## Research

Research should become archival content only after distinguishing:

- documented facts;
- inference;
- family recollection;
- unresolved questions.

Choose the appropriate destination:

- genealogy;
- story;
- document exhibit;
- photograph metadata;
- research notes.

---

# 9. Debugging

When pages fail:

1. verify syntax;
2. inspect browser console;
3. verify the server;
4. verify filenames;
5. confirm the edited file matches the served file;
6. isolate the most recent change.

When layout fails:

1. determine whether the issue belongs to data, measurement, placement, routing, or rendering;
2. inspect one real family example;
3. avoid coordinate adjustments before identifying responsibility.

Debug the smallest responsible layer.

---

# 10. Documentation Responsibilities

At the conclusion of a milestone:

- update **99-Current-Status.md** for operational state;
- update **04-Journal.md** for historical milestones.

Update permanent documents only when permanent knowledge changes:

- **01-Constitution.md** — enduring principles.
- **02-Architecture.md** — system responsibilities.
- **03-Engineering-Guide.md** — proven workflow improvements.
- **05-Visual-Language.md** — established visual language.
- **06-Version-2-Roadmap.md** — long-term direction.

---

# 11. Definition of Done

A change is complete only when:

- the intended source file changed;
- syntax or compilation succeeds;
- the diff contains only intended work;
- browser behavior is verified;
- privacy remains correct;
- unrelated behavior is preserved;
- the commit represents one coherent idea;
- repository status is understood;
- documentation has been updated when appropriate.

Completion means the repository is safer, clearer, and easier to maintain than before the work began.

---

# 12. Workflow Enforcement

Before proposing implementation changes, this Engineering Guide should be followed.

Implementation work is incomplete if it skips the established engineering process:

1. capture the current local implementation;
2. use guarded replacements whenever practical;
3. verify syntax;
4. review the diff;
5. verify browser behavior;
6. produce a focused commit.

The purpose of this workflow is not bureaucracy.

It exists to ensure that every implementation is based on the user's current repository, minimizes accidental edits, produces reproducible verification, and creates a clear, reviewable project history.
