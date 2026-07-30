# The Kallmer Family Archive Visual Language

## 1. Purpose

This document defines the stable visual semantics of the Kallmer Family
Archive.

It records what recurring visual elements mean across the site,
especially in the interactive family tree. It does not prescribe
implementation details such as CSS selectors, pixel measurements, exact
font sizes, or temporary layout adjustments.

This document should change only when the meaning of a visual element
changes or when a new permanent visual convention is established.

## 2. Relationship to the Permanent Documents

The project documents have distinct responsibilities:

- `00-Project-Guide.md` explains how the project is organized.
- `01-Constitution.md` defines the archive's purpose, character, and
  governing principles.
- `02-Architecture.md` defines system structure, data flow, component
  responsibilities, and rendering boundaries.
- `03-Engineering-Guide.md` defines the working method.
- `04-Journal.md` records decisions and development history.
- `05-Visual-Language.md` defines the meaning of stable visual forms.
- `99-Current-Status.md` records the present implementation state and
  next work.

This document must not duplicate the architecture, engineering workflow,
or development journal.

## 3. Governing Principle

Every recurring visual form should have one clear meaning.

The interface should be understandable without requiring a separate
legend whenever practical.

A visual treatment must not suggest a genealogical fact that the data
does not support.

Unknown or unresolved information should be represented explicitly and
quietly rather than hidden, guessed, or dramatized.

## 3.1 Museum Design Philosophy

The archive is conceived as a museum rather than a dashboard.

Each major area of the site serves a distinct role:

- the homepage is the museum lobby;
- person profiles are archival exhibits;
- the Family Tree is a finding aid that explains family structure;
- future Places & Migration views function as a historical atlas.

The visual language should reinforce these roles through consistency,
restraint, and historical authenticity rather than novelty or
decoration.

## 4. Overall Character

The archive should feel:

- calm;
- factual;
- archival;
- restrained;
- durable;
- respectful of the people and records it presents.

The interface should resemble a carefully curated family or
local-history archive rather than a modern dashboard, decorative
scrapbook, or novelty genealogy product.

Visual interest should come from the records, photographs,
relationships, and stories themselves.

Historical records---not interface elements---are the primary visual
focus.

Photographs, documents, stories, family relationships, and historical
context should always command more attention than controls, decorative
graphics, or interface chrome.

Visual design exists to frame the archival material rather than compete
with it.

## 5. Color Language

The established palette is centered around:

- ledger ink;
- prairie wheat;
- homestead clay;
- prairie sage;
- muted brass;
- muted slate blue;
- dusty rose;
- neutral parchment tones.

Color is used to organize, distinguish, and guide.

Color should not:

- overpower names or dates;
- become the sole carrier of meaning;
- imply certainty where the record is uncertain;
- decorate without informational purpose.

Gender-associated accents may be used sparingly where the available data
supports them. Neutral styling must remain available when the data does
not support a gendered treatment or when a placeholder is being shown.

## 6. Typography

Typography should feel literary, archival, and highly readable.

Display typography may provide historical warmth. Body, label, date, and
interface typography must remain clear at ordinary screen sizes.

Typography establishes hierarchy through restraint:

- names receive primary emphasis;
- life dates receive secondary emphasis;
- relationship annotations receive tertiary emphasis;
- controls and technical interface text remain subordinate to the
  family record.

Internal identifiers, implementation labels, and debugging text are not
part of the public visual language.

## 7. Person Cards

### 7.1 Standard Person Card

A standard card represents an identified person.

Its essential content is:

1.  the person's display name;
2.  life years or the privacy-appropriate equivalent;
3.  an optional relationship annotation when needed.

The card represents the person, not the person's role in the current
view. Labels such as "Father," "Spouse," or "Child" should not routinely
appear inside cards when the layout already communicates that
relationship.

### 7.2 Selected Person Card

The selected person is the current subject of the view.

The selected card may receive restrained emphasis and may expose the
profile action. It must remain visually consistent with other person
cards and must not resemble a separate application panel.

The selected person appears once in the Family Tree layout.

### 7.3 Placeholder Person Card

A placeholder card represents a genealogically necessary but
unidentified person.

Examples include:

- unknown spouse;
- unknown father;
- unknown mother;
- unknown parent where sex is not established.

Its visual treatment is:

- muted;
- faded relative to identified people;
- outlined with a restrained dashed border;
- structurally equal in size and placement behavior to a standard
  card.

A placeholder communicates incomplete knowledge, not an absent layout
object.

Unknown people must not be omitted when omission would distort the
family structure.

Placeholder wording should remain quiet and factual. Prefer concise
labels such as:

- Unknown spouse
- Unknown father
- Unknown mother
- Unknown parent

Avoid decorative question marks, silhouettes, dramatic mystery language,
or invented identifying detail.

## 8. Family Units

A Family Unit is one relationship between the selected person and one
partner, together with the children belonging to that relationship.

Visually, a Family Unit contains:

- one spouse or placeholder spouse;
- the relationship branch;
- relationship history associated with that union;
- the children belonging to that union.

Family Units are ordered chronologically from left to right when
chronology is known.

The selected person remains a single card. Multiple relationships do not
produce duplicate selected-person cards.

Children belong only to their own Family Unit and must not be visually
reassigned to the selected person in general or to another spouse.

## 9. Family Unit Bus

The Family Unit Bus is the horizontal organizing line beneath the
selected person from which individual Family Unit branches descend.

Its meaning is structural:

- it gathers the selected person's relationships;
- it preserves the selected person as a single card;
- it provides independent attachment points for each Family Unit;
- it makes chronological sequence legible.

The bus does not represent a marriage, household, or spouse-to-spouse
connection.

No connector should make one spouse appear connected to another spouse.

## 9.1 Family Unit Anchoring

Chronological ordering and visual emphasis are intentionally separate concepts.

Family Units always appear in the chronological order recorded by Gramps.

When determining horizontal placement beneath the selected person, the
renderer follows these canonical rules:

1. If one or more Family Units contain descendants, the first
   chronological Family Unit containing children is centered beneath the
   selected person.
2. If no Family Unit contains descendants, the final chronological
   Family Unit is centered.
3. Earlier Family Units extend to the left.
4. Later Family Units extend to the right.
5. All spouse cards remain on a common generation row regardless of
   divorce, widowhood, or other relationship outcomes.

This convention emphasizes the continuation of the family while
preserving the historical order of relationships.

The centered Family Unit is a presentation decision only. It does not
designate a "primary marriage" within the underlying genealogy.

## 10. Connector Language

Connectors represent genealogical structure.

They remain solid.

A connector may represent:

- parent to child;
- selected person to Family Unit structure;
- Family Unit to spouse;
- Family Unit to children.

Connector style must not independently encode:

- divorce;
- widowhood;
- uncertainty;
- adoption;
- family conflict;
- emotional closeness.

Those meanings belong to explicit annotations or markers.

Crossings must not imply connection. Where a route crosses behind an
unrelated card or line, spacing, interruption, or routing should
preserve the distinction.

Connector geometry should remain subordinate to the cards. It should
clarify relationships rather than become a decorative feature.

## 11. Relationship History on Spouse Cards

The third line of a spouse card may communicate the duration and outcome
of that Family Unit.

Established form:

```text
m. 1935–1957 · widowed
```

Other valid forms may include:

```text
m. 1960–1982 · divorced
m. 1991–
m. 1948 · status unknown
```

The annotation describes the relationship represented by that Family
Unit. It does not redefine the spouse's identity.

Use the available data honestly. Do not imply a start year, end year, or
outcome that the source data does not establish.

The exact wording may be refined for readability, but the information
order should remain stable:

1.  relationship type or marriage marker;
2.  known span;
3.  known outcome.

## 12. Divorce Marker

Divorce is represented by a small `X` placed on the affected Family Unit
branch.

The branch itself remains solid.

The `X` means that the union ended in divorce. It does not mean death,
estrangement, annulment, uncertainty, or a broken parent-child
relationship.

The marker should be visually restrained and should not dominate the
Family Unit.

Do not use dashed relationship connectors to represent divorce.

## 13. Widowhood and Other Union Outcomes

Widowhood is communicated through the spouse-card relationship
annotation.

It is not represented by a broken connector, faded spouse, or special
branch style.

Other outcomes, when supported by the data, should likewise be stated in
text rather than encoded through new connector styles.

This preserves one stable rule:

> Connectors show genealogy; annotations show relationship history.

## 14. Parent--Child Relationship Annotations

When the parent-child relationship differs from the default biological
relationship, the child card may use its third line to state the
relationship type.

Established labels include:

- Adopted
- Foster
- Step

These labels describe the child's relationship within the displayed
Family Unit.

They should appear beneath the life dates and remain visually
subordinate to the name and dates.

The absence of a label means only that no special relationship
annotation is being displayed. It must not be treated as proof beyond
the available data.

Do not encode adoption or other parent-child relationship types through
dashed connectors, altered branch colors, or decorative symbols.

## 15. Unknown and Uncertain Information

The visual language distinguishes between an unknown person and an
uncertain fact.

An unknown person is represented by a placeholder card.

An uncertain date, place, relationship status, or interpretation should
be stated through careful wording in the appropriate content area. It
should not cause the person to be omitted or the connector grammar to
change arbitrarily.

The archive must never create certainty for visual neatness.

## 16. Chronology

Chronology is a structural visual cue.

Where the data supports it:

- Family Units appear in chronological order;
- relationship spans reinforce that order;
- children remain grouped beneath the correct Family Unit.

Where chronology is unknown, the layout should use a stable
deterministic order without pretending that the order is historically
established.

## 17. Whitespace and Grouping

Whitespace is structural information.

It should help the visitor distinguish:

- the ancestry axis;
- the selected person;
- separate Family Units;
- spouse cards;
- child groups;
- unrelated branches.

Compactness must not come at the cost of false grouping or ambiguous
relationships.

Family Unit spacing should communicate separation without making related
people appear disconnected from the selected person.

Whitespace should function much like the spacing between exhibits in a
museum gallery: separating distinct subjects while preserving their
relationships within the larger collection.

## 18. Profile and Tree Relationship

The Family Tree is an orientation and navigation view.

It should show enough information to understand family structure and
choose a person, but it should not become a complete genealogical
report.

The person profile is the archival exhibit and may contain fuller dates,
places, photographs, documents, biographies, and source context.

The selected card's profile action bridges these two levels.

## 19. Motion and Interaction

Motion, when used, should aid orientation.

Appropriate uses include:

- restrained recentering;
- smooth movement after selecting a person;
- subtle transitions after a deliberate layout change.

Motion must not:

- make the archive feel playful or theatrical;
- obscure where a person moved;
- delay access to information;
- disregard `prefers-reduced-motion`.

Interaction controls should remain visually secondary to people and
relationships.

## 20. Responsive Behavior

Responsive design should preserve meaning rather than merely shrink the
desktop composition.

On smaller screens:

- cards must remain readable;
- Family Unit ownership must remain clear;
- connectors must retain their meanings;
- touch targets must remain usable;
- the selected person must remain easy to locate.

A mobile adaptation may change viewport behavior, spacing, or navigation
mechanics, but it must not change the visual semantics defined here.

## 21. Prohibited Visual Conventions

Do not introduce the following without an explicit reconsideration of
this document:

- duplicate cards for the selected person;
- spouse-to-spouse connectors;
- dashed connectors for divorce;
- connector colors that independently encode relationship outcomes;
- omission of an unknown spouse or parent when a placeholder is
  structurally required;
- children visually attached to the wrong Family Unit;
- decorative marriage symbols that compete with the genealogy;
- role labels that clutter otherwise self-explanatory cards;
- internal person IDs in the normal public card design;
- dramatic mystery styling for unknown people;
- ornamental curves or routing that make relationships harder to read.

## Design Evaluation

When considering a new permanent visual convention, ask:

- Does it improve historical understanding?
- Does it reinforce the museum character of the archive?
- Does it introduce a new visual meaning that will remain
  understandable over time?
- Will it still feel appropriate decades from now?
- Does it emphasize the historical record rather than the interface?

## 22. Change Rule

Update this document only when one of the following occurs:

- a permanent visual element gains a new meaning;
- an established visual meaning is changed;
- a new stable relationship convention is adopted;
- an existing convention is explicitly rejected;
- a site-wide visual principle becomes permanent.

Do not update this document for:

- pixel adjustments;
- ordinary spacing refinements;
- font-size changes;
- CSS refactors;
- temporary experiments;
- browser-specific fixes;
- isolated bug fixes;
- implementation helper names.

Those belong in code, the Journal, Current Status, or the Engineering
Guide as appropriate.

## 23. Current Canonical Semantics

The current Family Tree visual grammar is:

---

Visual element Meaning

---

Standard card Identified person

Restrained selected-card emphasis Current subject of the view

Muted dashed card Unidentified but structurally
required person

Vertical ancestry axis Parent-to-child descent into the
selected person

Horizontal Family Unit Bus Organization of the selected
person's relationships

Independent Family Unit branch One relationship and its associated
children

Solid connector Genealogical structure

`X` on a Family Unit branch Divorce

Third line on spouse card Relationship span and outcome

Third line on child card Non-default parent-child
relationship type

Horizontal order of Family Units Known chronology, or stable
fallback order when chronology is
unknown

Whitespace between units Structural separation

---

This table is the canonical reference when evaluating whether a proposed
visual change preserves or alters the Family Tree's meaning.
