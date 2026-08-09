# Associate and Publish Existing Media

Use this procedure when an existing catalog media object belongs to another person and should also appear in that person's website exhibit.

For example, a shared gravestone may already appear for one spouse but should also appear for the other.

## Key Concepts

Every catalog media object has a permanent `M######` identifier.

Every genealogy person has an `I####` identifier.

**Association** answers:

> Which people does this media object belong to?

**Publication** answers:

> In which people's website exhibits should this media object appear?

Association and publication are separate operations.

## Procedure

### 1. Identify the media M-number

Find the permanent media identifier for the existing object.

Example:

    M000157

### 2. Identify the person's I-number

Find the identifier of the person who should also be associated with the media.

Example:

    I0387

### 3. Preview the association

Run:

    python3 tools/media_associate.py --add-person M000157 I0387

Review the `Before` and `After` sections.

This is a dry run. It does not modify the catalog.

### 4. Apply the association

If the preview is correct:

    python3 tools/media_associate.py --add-person M000157 I0387 --apply

This changes the catalog association only.

It does not publish the media to the website.

### 5. Preview publication

Run:

    python3 tools/media_publish.py --publish M000157

Review the publication plan carefully.

People who already have the media in their website exhibit should be listed as already published.

Only missing website copies should be proposed for creation.

### 6. Apply publication

If the publication plan is correct:

    python3 tools/media_publish.py --publish M000157 --apply

This creates the required website exhibit copy and rebuilds the generated photo indexes.

The canonical vault master remains unchanged.

### 7. Verify in the browser

Refresh the person's profile on the local website.

Confirm that the media appears in the correct category:

- Photos
- Documents & Records
- Gravestones
- Artifacts
- Places

## Four-Command Recipe

Once the correct M-number and I-number are known:

    # Preview association
    python3 tools/media_associate.py --add-person M000157 I0387

    # Apply association
    python3 tools/media_associate.py --add-person M000157 I0387 --apply

    # Preview publication
    python3 tools/media_publish.py --publish M000157

    # Apply publication
    python3 tools/media_publish.py --publish M000157 --apply

Replace `M000157` and `I0387` with the appropriate identifiers.

## Safety Rule

Always run the dry-run command first.

Review the proposed change.

Only then repeat the command with `--apply`.

## Mental Model

**M-number = media object**

**I-number = person**

**Associate = who the media belongs to**

**Publish = whose website exhibit displays it**

The canonical vault master is not changed by website publication.
