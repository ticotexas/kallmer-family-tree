# The Kallmer Family Archive

## Start Here

The Kallmer Family Archive is a digital family archive organized through genealogy.

Genealogy provides the structure. The people—their photographs, documents, stories, places, relationships, and lived experience—are the destination.

This file is required reading at the beginning of every substantial development session. It provides orientation, identifies settled decisions, and directs the reader to the appropriate project document.

## Repository

- Repository: `https://github.com/ticotexas/kallmer-family-tree`
- Canonical project documentation: `docs/`
- Current work: see `99-Current-Status.md`

## Documentation Map

| Task                                                      | Read                      |
| --------------------------------------------------------- | ------------------------- |
| Understand the project's purpose and governing principles | `01-Constitution.md`      |
| Understand the software architecture                      | `02-Architecture.md`      |
| Make or review code changes                               | `03-Engineering-Guide.md` |
| Understand the project's history                          | `04-Journal.md`           |
| Understand the archive's visual philosophy                | `05-Visual-Language.md`   |
| Understand the archive's long-term direction              | `06-Version-2-Roadmap.md` |
| Resume current work                                       | `99-Current-Status.md`    |

Read only the documents required for the task. The Journal serves as historical reference and is not required reading for routine development.

## Core Identity

The archive is not intended to imitate Ancestry, FamilySearch, or Gramps. Those systems are primarily genealogy databases and research tools.

The Kallmer Family Archive is a curated presentation layer for one family’s history.

The archive exists to preserve historical understanding rather than simply genealogical facts.

Genealogy provides the organizational framework, but the archive's purpose is to connect visitors with the people, places, relationships, documents, and stories that give those facts historical meaning.

The site should feel like a quiet, well-organized museum archive:

- restrained rather than theatrical;
- human rather than database-like;
- clear rather than dense;
- historically respectful rather than nostalgic or melodramatic;
- visually coherent rather than feature-heavy.

## Historical Perspective

Version 2 expands the archive through four complementary lenses:

- People
- Relationships
- Places
- Time

Together these perspectives seek to answer not only **who** the family is, but **how the family became what it is**.

## Established Decisions

These decisions should not be casually reopened.

1. **The homepage is the museum lobby.**  
   It welcomes visitors, explains the archive, and offers clear entry points.

2. **The interactive tree is the map, not the destination.**  
   It provides orientation and navigation.

3. **The person profile is the archival exhibit.**  
   Rich detail belongs there: photographs, stories, documents, life events, and relationships.

4. **Tree cards remain minimal.**  
   They identify people and relationships without becoming miniature profile pages.

5. **One person has one card.**

6. **One union or partnership forms one family unit.**

7. **Children belong to a union, not to an individual.**

8. **The archive favors comprehension over compactness.**

9. **Stable visual behavior is preserved during architectural work.**

10. **Changes are small, verified, reversible, and committed separately.**

11. **The archive follows the museum metaphor throughout the visitor experience.**

12. **Historical authenticity is always preferred over visual novelty.**

## Project Quality Standard

A successful change should improve one or more of the following without unnecessarily weakening the others:

- historical fidelity;
- comprehensibility;
- visual restraint;
- accessibility;
- maintainability;
- privacy;
- reversibility;
- consistency with the archive’s established language.

The project prefers straightforward code over clever code, durable structure over temporary patches, and real family examples over idealized test cases.

## Development Session Protocol

At the beginning of a coding session:

1. Read this file.
2. Read `99-Current-Status.md`.
3. Read the relevant sections of the Architecture and Engineering Guide.
4. Work from the user’s current local files, never from an assumed or stale copy.
5. Preserve unrelated work already present in the repository.

At the end of a milestone:

1. Update `99-Current-Status.md`.
2. Add a concise entry to `04-Journal.md`.
3. Update Architecture only when the system itself changed.
4. Update the Constitution only when a foundational principle changed.
5. Update the Engineering Guide only when the working method improved.
6. Update the Visual Language only when permanent visual semantics change.
7. Update the Version 2 Roadmap only when long-term direction changes.

## Document Status Vocabulary

- **Established** — settled and expected to endure.
- **Provisional** — adopted for now but still under evaluation.
- **Proposed** — a serious future direction, not yet implemented.
- **Deferred** — intentionally postponed until a named dependency stabilizes.
- **Historical** — retained only to explain the project’s development.

## Final Orientation

When uncertain, choose the approach that makes the archive easier to understand, maintain, and preserve many years from now.

The project succeeds when visitors naturally move from family structure to individual lives, and from those lives to the photographs, documents, places, relationships, and stories that reveal a family's history.
