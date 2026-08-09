# 99 — Current Status

**Updated:** August 3, 2026

---

# Purpose

This document provides the project's current operational status.

It answers:

- What has been released?
- What is stable?
- What work should begin next?
- Where should additional information be found?

Historical decisions, implementation milestones, and architectural evolution belong in **04-Journal.md**.

---

# Release

**Current Release:** Version 1.0

The public edition of the Kallmer Family Archive has been released and is considered feature complete.

The Version 1 architecture is stable. Future work should favor refinement, curation, and long-term evolution over major redesign.

---

# Current State

The archive now provides:

- Public genealogy archive generated from Gramps.
- Privacy-aware handling of living individuals.
- Interactive Family Tree.
- Pedigree view.
- Person profiles.
- Integrated archive search.
- Historical stories and biographies.
- Photo galleries.
- Relationship history, including multiple marriages, divorce, and adoption presentation.
- Responsive layouts for desktop and mobile.
- Direct person URLs and browser-history support.

No known architectural issues currently block continued development.

---

# Stable Architecture

The following architectural decisions should be considered established unless a future milestone intentionally replaces them.

- Family-unit layout architecture.
- Shared archive search component.
- Privacy-aware data pipeline.
- Museum-inspired archive organization.
- Reciprocal Tree and Person Detail views.
- Shared visual language across the archive.
- Static-site deployment using generated public data.
- Catalog-native media architecture with permanent `M######` identities.
- Separation of the canonical media vault from website publication.
- Independent media classification, person association, and publication state.
- Category-aware person exhibits for Photos, Documents & Records, Gravestones, Artifacts, and Places.

Implementation details are documented in **02-Architecture.md**.

---

# Engineering Workflow

Development follows the project's Canonical Edit Cycle.

Every implementation should:

1. Work from the current local repository.
2. Make one meaningful change at a time.
3. Use guarded edits.
4. Verify syntax and behavior.
5. Review the diff.
6. Commit only the intended files.
7. Update documentation when enduring decisions are made.

Media work additionally follows a plan-before-apply workflow. New media enter through the catalog-native inbox process, receive permanent identity in the canonical vault, and are published to the website intentionally rather than being manually copied into person folders.

Detailed procedures are maintained in **03-Engineering-Guide.md**.

---

# Documentation Map

The project documentation has distinct responsibilities.

- **00-Project-Guide.md** — orientation
- **01-Constitution.md** — enduring principles
- **02-Architecture.md** — software architecture
- **03-Engineering-Guide.md** — development workflow
- **04-Journal.md** — historical record
- **05-Visual-Language.md** — museum design language
- **06-Version-2-Roadmap.md** — long-term vision
- **99-Current-Status.md** — operational status

Each document should retain its specific purpose rather than duplicating material found elsewhere.

---

# Version 2 Direction

Version 2 shifts the archive's emphasis from feature development toward richer historical interpretation.

Major long-term themes include:

- Places and Migration as a historical atlas.
- Richer person exhibits.
- Historical documents.
- Expanded storytelling.
- Timeline-based exploration.
- Continued refinement of the museum-inspired presentation.
- Additional shared infrastructure where it meaningfully reduces complexity.

Future work should continue to prioritize historical understanding over feature accumulation.

---

# Immediate Priorities

Current work focuses on:

1. Using the new catalog-native workflow for incoming genealogy media.
2. Continuing migration and cleanup of legacy media as needed without unnecessary filename churn.
3. Expanding person exhibits with documents, gravestones, places, artifacts, and photographs through catalog metadata.
4. Refining the archive's editorial quality and historical storytelling.
5. Continuing Version 2 development using the established roadmap while preserving the architectural and design principles established during Version 1.

---

# Guiding Principle

Version 1 established the archive.

Version 2 will deepen it.

The project should continue to favor thoughtful curation, historical authenticity, restrained visual design, and maintainable architecture over rapid feature growth.

---

# References

For historical context:

- **04-Journal.md**

For implementation:

- **02-Architecture.md**
- **03-Engineering-Guide.md**

For future direction:

- **05-Visual-Language.md**
- **06-Version-2-Roadmap.md**
