# Install Finished Stories

Use this workflow to install finished genealogy stories from the canonical
Genealogy Media Inbox into the Kallmer Family Archive website.

Stories are separate from catalog-native archival media. They do not receive
M-numbers.

## Mental Model

**stories-inbox = install finished stories**

The workflow follows:

**PERCEIVE → PLAN → PROCEED**

Dry-run is the default. Review the plan before using `--apply`.

## Prepare the Inbox

Place finished Markdown stories inside a human-readable person directory:

    Genealogy_Media/
    └── 00-Inbox/
        └── To_Process/
            └── William Kallmer/
                ├── 01-growing-up-in-storm-lake.md
                └── 02-school-basketball-and-ladon.md

You do not need to know the person's `I####` identifier.

The directory name is resolved against genealogy data in
`public-data/family.json`.

Person ownership is never guessed silently. If the name cannot be resolved
uniquely, the tool blocks the entire apply and shows the problem.

## Story Files

Supported extensions:

- `.md`
- `.markdown`

Embedded story Markdown should begin directly with the story text.

Do not include an H1 title such as:

    # Growing Up in Storm Lake

The website derives the display title from the filename.

## Plan

From the project root:

    python3 tools/stories_inbox.py

Review:

- source person directory;
- matched person and `I####`;
- destination story directory;
- existing story count;
- incoming story count;
- filename collisions;
- Markdown validation;
- blocking errors.

Nothing is changed during the default dry-run.

## Apply

After reviewing a clean plan:

    python3 tools/stories_inbox.py --apply

The tool:

1. preflights the complete batch;
2. refuses unresolved or ambiguous person ownership;
3. refuses unsupported Inbox entries;
4. refuses destination filename collisions;
5. refuses incoming stories beginning with an H1;
6. moves the stories into the person's website story directory;
7. rebuilds story indexes;
8. verifies installed files and index membership;
9. removes emptied person Inbox directories.

If installation or verification fails after files begin moving, the tool
attempts to restore the stories to their original Inbox locations and rebuild
the story indexes.

## Safety Rules

Do not bypass a reported person-name ambiguity by guessing.

Do not manually overwrite an existing website story.

Resolve the cause of a blocking error, then run the dry-run again.

For normal operation:

**dry-run → review → `--apply`**
