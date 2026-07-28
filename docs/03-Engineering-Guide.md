# The Kallmer Family Archive Engineering Guide

## 1. Purpose

This guide defines the working method for changing the Kallmer Family Archive safely and coherently.

It is not a generic style guide. It records the development process that has proven reliable for this repository and this collaboration.

## 2. Primary Rule

**Always work from the user’s current local files.**

Uploaded files, prior chat excerpts, documentation examples, and remembered code may be stale.

Before directing a structural edit, inspect the exact current local block.

Example:

```bash
sed -n '/function buildLayout/,/function drawCards/p' js/family-tree.js
```

The printed local code is authoritative for that edit.

## 3. Change Size

Make one meaningful change at a time.

A meaningful change may be:

- extracting one responsibility;
- changing one layout behavior;
- adding one data field;
- correcting one rendering rule;
- adjusting one coherent visual system.

Do not combine:

- architecture work;
- unrelated photograph additions;
- regenerated data;
- broad styling changes;
- speculative cleanup.

Small changes improve diagnosis, review, reversal, and Git history.

## 4. Guarded Edit Pattern

For exact JavaScript or text replacements, use a guarded Python script.

```bash
python3 - <<'PY'
from pathlib import Path

path = Path("js/family-tree.js")
text = path.read_text()

old = '''EXACT CURRENT BLOCK'''
new = '''EXACT REPLACEMENT BLOCK'''

if old not in text:
    raise SystemExit("Stopped: expected block did not match.")

text = text.replace(old, new, 1)
path.write_text(text)

print("Completed requested edit.")
PY
```

This pattern is preferred because it:

- works from a visible, verified block;
- stops safely when the local code differs;
- replaces only once;
- avoids imprecise manual editing;
- creates a reviewable diff.

Do not use an unguarded broad replacement when an exact block can be used.

## 5. JavaScript Verification Cycle

After every JavaScript edit:

```bash
node --check js/family-tree.js
```

Silent output means the syntax is valid.

Then inspect the exact diff:

```bash
git --no-pager diff -- js/family-tree.js
```

`--no-pager` prints the diff directly into the terminal instead of opening Git’s pager. This avoids the `q` exit step and leaves the output in terminal scrollback for copying.

Equivalent alternatives include:

```bash
GIT_PAGER=cat git diff -- js/family-tree.js
git --no-pager diff --stat
```

Only after syntax and diff review should the browser be tested.

## 6. Browser Verification

For visual or interaction changes:

1. Keep the local server running in a dedicated terminal.
2. Hard-refresh with `Ctrl+Shift+R`.
3. Test the intended family or person.
4. Verify the requested change.
5. Verify that unrelated appearance and behavior remain unchanged.
6. Test direct URL behavior when relevant.
7. Test at least one difficult real family example.
8. Check desktop and mobile when the change affects layout or fit.

Review one category at a time:

- geometry;
- typography;
- color;
- connectors;
- interaction;
- data;
- privacy.

Avoid diagnosing every category simultaneously.

## 7. Git Discipline

Before staging:

```bash
git status --short
git --no-pager diff
```

Stage only intended files.

Example:

```bash
git add js/family-tree.js
```

Do not use:

```bash
git add .
```

unless the entire working tree has been deliberately reviewed and is intended for one commit. The default project rule is not to use it.

After committing and pushing:

```bash
git status --short
```

A code commit should not accidentally include:

- new photographs;
- photo index changes;
- generated family data;
- unrelated HTML or CSS;
- editor artifacts.

## 8. Commit Design

Each commit should describe one completed, testable idea.

Good examples:

- `Extract family-unit measurement from layout`
- `Group children by marriage in profile view`
- `Add faded unknown-parent placeholders`
- `Improve initial mobile tree fit`

Avoid commits that merely say:

- `updates`
- `fixes`
- `more work`
- `phase changes`

The commit message should remain useful when read months later.

## 9. Architectural Refactoring

During a refactor:

- preserve visual behavior unless a visible change is explicitly part of the task;
- do not tune pixels while responsibilities are moving;
- move one responsibility at a time;
- keep the browser working after every step;
- stop extracting when ownership is clear;
- do not create helpers solely to shorten functions.

A compact coordinator is desirable only when the extracted components have real responsibilities.

## 10. Visual Work

The archive’s established visual contract includes:

- parchment background;
- restrained archival palette;
- minimal person cards;
- muted gender or neutral accents;
- selected-card emphasis without visual loudness;
- light relationship lines;
- direct profile navigation;
- calm typography.

When changing architecture, preserve this contract.

When changing visuals:

- identify the exact visual objective;
- modify the smallest responsible CSS or drawing rule;
- compare against the current successful view;
- avoid phase-specific override stylesheets as a permanent solution;
- keep interactive-tree styling consolidated in `css/family-tree.css`.

## 11. Data Pipeline Work

When changing the converter:

1. Inspect the exact current converter code.
2. Make one schema or privacy change at a time.
3. Compile the script.
4. Regenerate output intentionally.
5. Inspect representative public and private records.
6. Confirm living-person privacy.
7. Review the generated diff.
8. Keep regenerated data in the same commit only when it is the direct result of the converter change.

Do not hand-edit generated JSON as a substitute for fixing the pipeline, except for a deliberately designed override system.

## 12. Media Work

Photograph, story, and document changes should be grouped logically.

Before committing media:

- verify folder naming;
- verify person ID;
- verify index order;
- verify captions;
- verify portrait selection;
- verify public appropriateness;
- check for duplicate or accidental files.

Do not mix large media additions with layout-engine changes.

## 13. Research-to-Archive Boundary

Research notes are not automatically publication-ready.

Before research becomes site content:

- distinguish record from inference;
- verify names and dates;
- preserve uncertainty;
- choose a restrained editorial form;
- decide whether the content belongs in genealogy data, a story, a document exhibit, photo metadata, or research notes.

Do not force narrative findings into the genealogy schema when a story or exhibit is the better home.

## 14. Debugging Principles

When a page is blank or broken:

1. check JavaScript syntax;
2. inspect the browser console;
3. confirm the server is serving the expected file;
4. verify paths and filenames;
5. confirm the current editor tab matches the served file;
6. reduce to the most recent change.

When layout is wrong:

1. identify whether the problem is in data, measurement, placement, routing, or rendering;
2. inspect one real family example;
3. avoid coordinate nudges until responsibility is clear;
4. correct the smallest responsible layer.

## 15. Session Handoff

At the end of a milestone, update:

- `99-Current-Status.md` with current branch, status, next action, and risks;
- `04-Journal.md` with what changed and why.

Update permanent documents only when necessary:

- Constitution: foundational values or settled design decisions;
- Architecture: system responsibilities or stable pipelines;
- Engineering Guide: proven improvements to the working method.

## 16. Definition of Done

A change is complete when:

- the intended local file was changed;
- syntax or compilation checks pass;
- the diff contains only intended work;
- browser behavior is verified;
- privacy remains correct;
- unrelated behavior is preserved;
- the commit is focused;
- the working tree status is understood;
- current status documentation is updated when the milestone warrants it.

## ChatGPT Development Workflow

This project follows a disciplined ChatGPT collaboration workflow to reduce context drift and make each change auditable.

### Capture the current implementation

Before modifying any function, ask the user to print the current implementation from their local working copy rather than relying on reconstructed examples.

Preferred pattern:

```bash
id="abcd1234"

{
  sed -n '/function buildLayout/,/function drawCards/p' js/family-tree.js
} | tee /tmp/buildLayout-${id}.txt | xclip -selection clipboard
```

For numbered excerpts:

```bash
id="abcd1234"

{
  nl -ba js/family-tree.js | sed -n '420,620p'
} | tee /tmp/layout-${id}.txt | xclip -selection clipboard
```

Why this pattern:

- `tee` preserves an exact snapshot under `/tmp` for reference.
- `xclip` places the same output on the clipboard for immediate pasting into ChatGPT.
- The snapshot and clipboard always contain identical content.

### Development discipline

1. Work from the user's current local files.
2. Make one meaningful architectural change per commit.
3. Run `node --check js/family-tree.js` after every JavaScript edit.
4. Review the `git diff`.
5. Hard-refresh the browser.
6. Verify there are no unintended visual regressions.
7. Commit only the intended files.

## 16. Canonical Edit Cycle (Required)

All implementation work follows the Canonical Edit Cycle. This workflow is mandatory for every coding session and supersedes generic editing habits.

### Step 1 — Capture the Current Local Source

Never edit from memory, uploaded files, or previous chat history.

Request the exact current local block from the user using the project's clipboard workflow.

Example:

```bash
id="descriptive-operation-name"

{
  sed -n '/START_PATTERN/,/END_PATTERN/p' path/to/file
} | tee /tmp/${id}.txt | xclip -selection clipboard
```

The clipboard output becomes the authoritative source for the next edit.

### Step 2 — Perform a Guarded Replacement

Do not ask the user to edit manually.

Generate a guarded Python replacement using `pathlib` that:

- reads the current file;
- matches the exact captured text;
- aborts if the expected block is not found;
- replaces only the intended block;
- writes the updated file.

Every guarded replacement must fail safely rather than risking unintended edits.

### Step 3 — Verify

After every JavaScript change:

```bash
node --check path/to/file.js
```

Then inspect only the intended changes:

```bash
git --no-pager diff -- path/to/file.js
```

### Step 4 — Capture Verification

Verification should also use the clipboard workflow.

Example:

```bash
id="descriptive-verification-name"

{
  echo "NODE CHECK"
  echo "=========="
  node --check path/to/file.js

  echo
  echo "DIFF"
  echo "===="
  git --no-pager diff -- path/to/file.js
} | tee /tmp/${id}.txt | xclip -selection clipboard
```

The clipboard output becomes the review artifact for the next discussion.

### Step 5 — Continue Incrementally

Only after verification should the next implementation step begin.

Each cycle should accomplish one meaningful architectural or behavioral improvement.

Avoid combining unrelated work into a single edit.

## 17. Workflow Enforcement

Before proposing any code modification, ChatGPT must first read this Engineering Guide and follow the Canonical Edit Cycle.

If ChatGPT proposes code edits without:

1. capturing the current local source,
2. using a guarded replacement,
3. verifying with `node --check`,
4. reviewing with `git --no-pager diff`, and
5. capturing verification output,

then the proposal should be considered invalid and restarted using this workflow.

The Canonical Edit Cycle exists to ensure that every implementation is based on the user's current local files, minimizes accidental edits, produces reproducible verification, and keeps every commit focused and reviewable.
