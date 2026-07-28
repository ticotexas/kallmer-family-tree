# The Kallmer Family Archive Constitution

## 1. Purpose

The Kallmer Family Archive preserves and presents the history of a family through people, relationships, photographs, documents, stories, and places.

Genealogy is the archive’s organizational framework. It is not the archive’s full purpose.

The project exists to help a visitor answer two questions:

1. **Who is this person in the family?**
2. **What can I discover about this person’s life?**

The family tree answers the first question. The archival profile answers the second.

## 2. Character of the Archive

The archive should feel calm, factual, respectful, and durable.

It should avoid:

- melodramatic genealogy prose;
- sentimental excess;
- decorative historical pastiche;
- modern dashboard aesthetics;
- dense database presentation;
- novelty that competes with the records themselves.

Its visual and written language should resemble a carefully curated local-history archive or museum collection.

### Established

- Archival restraint is preferred over spectacle.
- Readability is preferred over genealogical complexity.
- Historical people are presented as people, not as data points.
- Uncertainty is stated rather than concealed.
- Research findings and family memory are distinguished when appropriate.

## 3. Information Hierarchy

The site has three principal levels.

### 3.1 The Homepage: Museum Lobby

The homepage welcomes the visitor and explains what the archive is.

It should:

- establish tone;
- present a small number of meaningful entry points;
- feature people, photographs, or themes without overwhelming the visitor;
- lead naturally into the archive.

It should not attempt to display the whole archive at once.

### 3.2 The Tree: Orientation and Navigation

The interactive tree shows family structure in a visually intelligible form.

It should:

- establish kinship at a glance;
- make chronology and family groupings visible;
- allow the visitor to move between people;
- remain visually quiet enough that relationships are easier to read than interface controls.

The tree is not a complete genealogical report.

### 3.3 The Profile: Archival Exhibit

The person profile is where a life is presented.

It may contain:

- life dates and places;
- parents, spouses, children, and siblings;
- marriages, divorces, widowhood, and remarriage;
- photographs and captions;
- biographies and stories;
- historical documents;
- research notes or source context;
- direct links suitable for sharing.

## 4. Family Tree Layout Constitution

### Mission

Design a relationship diagram that is immediately understandable without requiring a legend.

### Established Principles

1. One person, one card.
2. One union or partnership, one family unit.
3. Children belong to a union, never to an individual.
4. Chronology should be visible before dates are read.
5. Every connector has exactly one meaning.
6. Crossings never imply connection.
7. Crossing lines should visually break or gap where necessary.
8. Secondary unions route around, never through, another family’s descendant area.
9. Whitespace is structural information.
10. Comprehension is more important than compactness.
11. Real genealogical edge cases are the preferred tests.
12. A union midpoint may be used as an internal layout anchor without requiring a visible marriage symbol.

### Tree Card Language

Tree cards remain minimal.

They may show:

- name;
- life years;
- a restrained gender or neutral accent;
- a profile link on the selected person.

They should not routinely show:

- internal GEDCOM identifiers;
- relationship-role labels;
- ages;
- complete event details;
- biographies;
- decorative genealogy symbols.

Unknown parents or spouses should use faded archival placeholders with restrained dashed borders when needed. Avoid labels such as “Spouse Unknown” when a quieter visual placeholder communicates the absence more naturally.

## 5. Visual Language

### Established Palette

The archive uses a restrained historical palette centered around:

- ledger ink;
- prairie wheat;
- homestead clay;
- prairie sage;
- muted brass;
- muted slate blue;
- dusty rose;
- neutral parchment tones.

Color should organize and guide. It should not decorate for its own sake.

### Typography

Typography should feel literary, archival, and highly readable.

Display type may carry historical warmth. Body and interface text must remain clear at ordinary screen sizes.

### Cards and Connectors

Cards should feel like archival labels or catalog objects, not app widgets.

Connectors should:

- remain lighter than card borders;
- use curves selectively;
- preserve straight spouse links where possible;
- avoid unnecessary jogs and ornamental S-curves;
- favor consistent, legible geometry.

## 6. Historical and Editorial Integrity

The archive must distinguish among:

- confirmed records;
- inferred relationships;
- family recollection;
- provisional readings;
- unresolved questions.

The site should never create certainty merely for visual neatness.

Biographical writing should be:

- specific;
- restrained;
- evidence-led;
- human;
- free of exaggerated claims.

When a source is incomplete, the wording should preserve that uncertainty.

## 7. Privacy

The public archive protects living people.

Public output should remain intentionally reduced. Private source data may contain fuller information, but the public site must follow the current privacy rules encoded in the data pipeline.

Privacy is an architectural responsibility, not an editorial afterthought.

## 8. Engineering Values

### Established

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

## 9. Decision Discipline

A foundational decision should be changed only when:

1. a real project need exposes a weakness;
2. the proposed replacement is clearer;
3. the effect on existing behavior is understood;
4. the decision is recorded in the Journal;
5. the relevant permanent document is updated.

The archive should evolve deliberately, not by accumulating exceptions.

## 10. Long-Term Direction

The archive may grow to include:

- featured ancestors;
- featured historical photographs;
- richer document exhibits;
- timeline views;
- adoption and relationship overrides;
- improved mobile tree navigation;
- first-class routing nodes;
- subtree expansion or collapse;
- keyboard navigation.

These features are subordinate to the archive’s permanent purpose: helping visitors understand the family and encounter the lives within it.
