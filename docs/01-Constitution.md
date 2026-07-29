# The Kallmer Family Archive Constitution

This Constitution records the enduring principles that define the Kallmer Family Archive.

Unlike architecture, engineering practices, release status, or future planning, these principles are intended to remain stable over many years. They guide decisions whenever new features, visual designs, editorial policies, or implementation approaches are considered.

When another project document conflicts with this Constitution, the Constitution takes precedence.

---

# 1. Purpose

The Kallmer Family Archive preserves and presents the history of a family through people, relationships, photographs, documents, stories, and places.

Genealogy is the archive's organizational framework. It is not the archive's full purpose.

The project exists to help every visitor answer three questions:

1. **Who is this person in the family?**
2. **What can I discover about this person's life?**
3. **How did this family become what it is?**

The family tree primarily answers the first question.

The archival profile answers the second.

The archive as a whole—including its stories, places, documents, relationships, and historical context—answers the third.

---

# 2. Enduring Perspective

The archive presents family history through four complementary lenses:

- People
- Relationships
- Places
- Time

Every major feature should strengthen one or more of these perspectives.

No single perspective should dominate the archive to the exclusion of the others.

Together they provide historical understanding that extends beyond genealogy alone.

---

# 3. Character of the Archive

The archive should feel calm, factual, respectful, and durable.

It should avoid:

- melodramatic genealogy prose;
- sentimental excess;
- decorative historical pastiche;
- modern dashboard aesthetics;
- dense database presentation;
- novelty that competes with the historical record itself.

Its visual and written language should resemble a carefully curated local-history museum or archival collection.

## Established

- Archival restraint is preferred over spectacle.
- Readability is preferred over genealogical complexity.
- Historical people are presented as people, not as data points.
- Uncertainty is stated rather than concealed.
- Research findings and family memory are distinguished whenever appropriate.
- Historical authenticity is preferred over visual novelty.

---

# 4. Information Hierarchy

The archive has three principal levels.

## 4.1 The Homepage — Museum Lobby

The homepage welcomes the visitor and explains what the archive is.

It should:

- establish tone;
- present a small number of meaningful entry points;
- feature people, photographs, or themes without overwhelming the visitor;
- lead naturally into the archive.

It should never attempt to display the entire archive at once.

---

## 4.2 The Tree — Orientation and Navigation

The interactive tree explains family structure in a visually intelligible form.

It should:

- establish kinship at a glance;
- make chronology and family groupings visible;
- allow visitors to move naturally between people;
- remain visually quiet enough that relationships are easier to read than interface controls.

The tree is an orientation tool, not a complete genealogical report.

---

## 4.3 The Profile — Archival Exhibit

The person profile is where an individual life is presented.

It may contain:

- life dates and places;
- parents, spouses, children, and siblings;
- marriages, divorces, widowhood, and remarriage;
- photographs and captions;
- biographies and stories;
- historical documents;
- research notes and source context;
- direct links suitable for sharing.

---

# 5. Family Tree Layout Constitution

## Mission

Design a relationship diagram that is immediately understandable without requiring a legend.

## Established Principles

1. One person has one card.
2. One union or partnership forms one family unit.
3. Children belong to a union, never to an individual.
4. Chronology should become visible before dates are read.
5. Every connector has exactly one meaning.
6. Crossings never imply connection.
7. Crossing lines should visually break where necessary.
8. Secondary unions route around—not through—another family's descendant area.
9. Whitespace is structural information.
10. Comprehension is more important than compactness.
11. Real genealogical edge cases are the preferred tests.
12. A union midpoint may be used internally as a layout anchor without requiring a visible marriage symbol.

## Tree Card Language

Tree cards remain intentionally minimal.

They may show:

- name;
- life years;
- restrained gender or neutral accents;
- a profile link on the selected person.

They should not routinely display:

- GEDCOM identifiers;
- relationship-role labels;
- ages;
- complete event details;
- biographies;
- decorative genealogy symbols.

Unknown parents or spouses should use restrained archival placeholders rather than visually demanding labels whenever possible.

---

# 6. Visual Language

## Established Palette

The archive uses a restrained historical palette centered around:

- ledger ink;
- prairie wheat;
- homestead clay;
- prairie sage;
- muted brass;
- muted slate blue;
- dusty rose;
- neutral parchment tones.

Color should organize and guide.

It should never decorate for its own sake.

## Typography

Typography should feel literary, archival, and highly readable.

Display type may provide historical warmth.

Body and interface typography must remain clear under ordinary reading conditions.

## Cards and Connectors

Cards should resemble archival labels or catalog objects rather than application widgets.

Connectors should:

- remain lighter than card borders;
- use curves only where they improve readability;
- preserve straight spouse links whenever practical;
- avoid ornamental routing;
- favor consistent and legible geometry.

---

# 7. Historical and Editorial Integrity

The archive distinguishes among:

- confirmed records;
- inferred relationships;
- family recollection;
- provisional readings;
- unresolved questions.

The archive should never create certainty merely for visual neatness.

Historical context should be preserved whenever it meaningfully improves understanding, even when that context extends beyond immediate genealogical facts.

Biographical writing should remain:

- specific;
- restrained;
- evidence-led;
- human;
- free of exaggerated claims.

When evidence is incomplete, the wording should preserve that uncertainty.

---

# 8. Privacy

The public archive protects living people.

Public output remains intentionally limited.

Private source data may contain fuller information, but every public presentation must follow the archive's established privacy model.

Privacy is an architectural responsibility rather than an editorial afterthought.

Privacy protections should fail safely.

When uncertainty exists, the public archive should reveal less rather than more.

---

# 9. Engineering Values

## Established

- Preserve working behavior before improving internals.
- Prefer small, reversible changes.
- Make one meaningful architectural change per commit.
- Validate syntax before browser review.
- Review the diff before staging.
- Stage only intended files.
- Do not hide architectural uncertainty beneath pixel-level tuning.
- Stabilize behavior before entering a polish phase.
- Extract helpers because they establish responsibility, not merely because a function is long.
- Let the smallest responsible component own a change.
- Preserve institutional knowledge by documenting permanent decisions.

---

# 10. Decision Discipline

A foundational decision should change only when:

1. a genuine project need exposes a weakness;
2. the proposed replacement is demonstrably clearer;
3. the effect on existing behavior is understood;
4. the decision is recorded in the Journal;
5. the relevant permanent documentation is updated.

The archive should evolve deliberately rather than accumulate exceptions.

Every permanent decision should make the archive easier to understand, easier to maintain, and more faithful to the historical record.
