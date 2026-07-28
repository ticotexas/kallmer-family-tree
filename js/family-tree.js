"use strict";

const DEFAULT_PERSON_ID = "I0000";
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

const svg = document.getElementById("family-tree");
const stage = document.getElementById("tree-stage");
const statusElement = document.getElementById("tree-status");
const pedigreeLink = document.querySelector(".pedigree-link");
const searchInput = document.getElementById("person-search");
const searchResults = document.getElementById("search-results");
const archiveData = new ArchiveData();
const archiveRelationships = new ArchiveRelationships(archiveData);
const archiveDates = new ArchiveDates();
const archiveSearch = new ArchiveSearch();

let peopleById = new Map();
let familiesById = new Map();

function createSvgElement(tagName, attributes = {}) {
  const element = document.createElementNS(SVG_NAMESPACE, tagName);

  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, value);
  }

  return element;
}

function getRequestedPersonId() {
  const parameters = new URLSearchParams(window.location.search);
  return parameters.get("person") || DEFAULT_PERSON_ID;
}

function formatLifeYears(person) {
  if (person.placeholder) {
    return person.placeholderSubtitle || "Research continuing";
  }

  const birthYear = archiveDates.extractYear(person.birth) ?? "?";
  const deathYear = archiveDates.extractYear(person.death) ?? "?";

  if (person.living || !person.death) {
    return `${birthYear} –`;
  }

  return `${birthYear} – ${deathYear}`;
}


function hideSearchResults() {
  searchResults.style.display = "none";
  searchResults.replaceChildren();
}

function renderSearchResults(matches) {
  searchResults.replaceChildren();

  if (!matches.length) {
    const empty = document.createElement("div");
    empty.className = "search-empty";
    empty.textContent = "No matching people found";
    searchResults.append(empty);
    searchResults.style.display = "block";
    return;
  }

  matches.forEach((person) => {
    const button = document.createElement("button");
    button.className = "search-result";
    button.type = "button";

    const name = document.createElement("span");
    name.className = "search-result-name";
    name.textContent = person.name;

    const dates = document.createElement("span");
    dates.className = "search-result-dates";
    dates.textContent = formatLifeYears(person);

    button.append(name, dates);

    button.addEventListener("click", () => {
      selectPerson(person.id);
      searchInput.value = person.name;
      hideSearchResults();
    });

    searchResults.append(button);
  });

  searchResults.style.display = "block";
}

function setupSearch() {
  searchInput.addEventListener("focus", () => {
    window.setTimeout(() => searchInput.select(), 0);
  });

  searchInput.addEventListener("click", () => {
    searchInput.select();
  });

  searchInput.addEventListener("input", () => {
    const query = archiveSearch.normalizeText(searchInput.value.trim());

    if (query.length < 2) {
      hideSearchResults();
      return;
    }

    renderSearchResults(archiveSearch.search(query));
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      hideSearchResults();
      searchInput.blur();
    }
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest("#search-area")) {
      hideSearchResults();
    }
  });
}

function splitNameIntoLines(name) {
  const words = String(name || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (words.length < 2) {
    return [name];
  }

  return [words.slice(0, -1).join(" "), words.at(-1)];
}

function getGenderAccentClass(person) {
  if (person?.placeholder) {
    return person.placeholderAccentClass || "unknown-person-accent";
  }

  const recordedGender = String(person?.gender ?? person?.sex ?? "")
    .trim()
    .toLowerCase();

  if (recordedGender === "m" || recordedGender === "male") {
    return "male-person-accent";
  }

  if (recordedGender === "f" || recordedGender === "female") {
    return "female-person-accent";
  }

  const appearsAsHusband = [...familiesById.values()].some(
    (family) => family.husband === person.id,
  );

  if (appearsAsHusband) {
    return "male-person-accent";
  }

  const appearsAsWife = [...familiesById.values()].some(
    (family) => family.wife === person.id,
  );

  if (appearsAsWife) {
    return "female-person-accent";
  }

  return "neutral-person-accent";
}

function drawPersonCard(person, x, y, options = {}) {
  if (!person) {
    return;
  }

  const {
    width = 240,
    height = 92,
    selected = false,
    relationshipLabels = [],
  } = options;
  const isPlaceholder = Boolean(person.placeholder);
  const nameLines = splitNameIntoLines(person.name);
  const hasProfileLink = selected;
  const nameStartY =
    nameLines.length > 1
      ? hasProfileLink
        ? 27
        : 30
      : hasProfileLink
        ? 34
        : 36;
  const dateY =
    nameLines.length > 1
      ? hasProfileLink
        ? 64
        : 67
      : hasProfileLink
        ? 58
        : 61;

  const group = createSvgElement("g", {
    class: isPlaceholder
      ? "person-card-group placeholder-card-group"
      : "person-card-group",
    transform: `translate(${x} ${y})`,
    ...(isPlaceholder || selected
      ? {}
      : {
          tabindex: "0",
          role: "button",
          "aria-label": `${person.name}. Recenter tree around this person.`,
        }),
  });

  const card = createSvgElement("rect", {
    class: isPlaceholder
      ? "person-card unknown-person-card"
      : selected
        ? "person-card selected-person-card"
        : "person-card",
    width,
    height,
    rx: 7,
    ry: 7,
  });

  const genderAccentClass = getGenderAccentClass(person);

  const accent = createSvgElement("rect", {
    class: [
      "person-card-accent",
      genderAccentClass,
      selected ? "selected-person-accent" : "",
    ]
      .filter(Boolean)
      .join(" "),
    width: selected ? 8 : 6,
    height,
    rx: 3,
    ry: 3,
  });

  group.append(card, accent);

  const name = createSvgElement("text", {
    class: `${
      person.name.length > 25 ? "person-name long-person-name" : "person-name"
    }${isPlaceholder ? " unknown-person-name" : ""}`,
    x: width / 2,
    y: nameStartY,
  });

  nameLines.forEach((line, index) => {
    const tspan = createSvgElement("tspan", {
      x: width / 2,
      dy: index === 0 ? 0 : 20,
    });

    tspan.textContent = line;
    name.append(tspan);
  });

  const dates = createSvgElement("text", {
    class: isPlaceholder ? "person-dates unknown-person-dates" : "person-dates",
    x: width / 2,
    y: dateY,
  });

  dates.textContent = formatLifeYears(person);

  group.append(name, dates);

  const relationshipStartY = dateY + 24;
  const relationshipLineGap = 18;

  relationshipLabels.forEach((relationshipLabel, index) => {
    const relationship = createSvgElement("text", {
      class: "person-relationship",
      x: width / 2,
      y: relationshipStartY + index * relationshipLineGap,
    });

    relationship.textContent = relationshipLabel;
    group.append(relationship);
  });

  if (selected) {
    const profileLink = createSvgElement("a", {
      class: "profile-link",
      href: `tree.html?person=${encodeURIComponent(person.id)}`,
      "aria-label": `View profile for ${person.name}`,
    });

    const profileHitbox = createSvgElement("rect", {
      class: "profile-link-hitbox",
      x: width / 2 - 54,
      y: height - 29,
      width: 108,
      height: 24,
      rx: 3,
      ry: 3,
    });

    const profileText = createSvgElement("text", {
      class: "profile-link-text",
      x: width / 2,
      y: height - 10,
    });

    profileText.textContent = "View Profile";
    profileLink.append(profileHitbox, profileText);
    profileLink.addEventListener("click", (event) => event.stopPropagation());
    group.append(profileLink);
  }

  if (!isPlaceholder && !selected) {
    const recenter = () => selectPerson(person.id);

    group.addEventListener("click", recenter);
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        recenter();
      }
    });
  }

  stage.append(group);
}

function drawRelationshipPath(
  pathData,
  className = "relationship-line",
) {
  const path = createSvgElement("path", {
    class: className,
    d: pathData,
  });

  stage.append(path);
}

function drawRelationshipSegments(segments) {
  drawRelationshipPath(segments.filter(Boolean).join(" "));
}
function getCardGeometry(card) {
  return {
    left: card.x,
    right: card.x + card.width,
    top: card.y,
    bottom: card.y + card.height,
    centerX: card.x + card.width / 2,
    centerY: card.y + card.height / 2,
  };
}

function createUnknownAncestor(side) {
  return {
    id: `unknown-${side}`,
    name: "Unknown Ancestor",
    birth: "",
    death: "",
    living: false,
    placeholder: true,
  };
}

function createUnknownSpouse(familyId) {
  return {
    id: `unknown-spouse-${familyId}`,
    name: "Unknown",
    birth: "",
    death: "",
    living: false,
    placeholder: true,
    placeholderSubtitle: "not yet identified",
  };
}

function buildFamilyUnits(person, unions) {
  return unions
    .map((union, originalIndex) => ({
      union,
      originalIndex,
      marriageYear:
        archiveDates.extractYear(union.family?.marriage_date) ??
        Number.POSITIVE_INFINITY,
    }))
    .sort(
      (a, b) =>
        a.marriageYear - b.marriageYear ||
        a.originalIndex - b.originalIndex,
    )
    .map(({ union }, unionIndex) => ({
      id: union.family.id,
      union,
      primaryPerson: person,
      spouse: union.spouse,
      children: union.children,
      isPrimary: unionIndex === 0,
      marriageOrder: unionIndex,
    }));
}

function buildFamilyViewModel(person) {
  const parentFamily = archiveRelationships.findParentFamily(person.id);

  let father = parentFamily?.husband
    ? peopleById.get(parentFamily.husband)
    : null;

  let mother = parentFamily?.wife ? peopleById.get(parentFamily.wife) : null;

  // Show a quiet archival placeholder only when a known parent union is
  // missing one person. Do not invent an entire pair when no parent family
  // has yet been documented.
  if (parentFamily && father && !mother) {
    mother = createUnknownAncestor("mother");
  }

  if (parentFamily && mother && !father) {
    father = createUnknownAncestor("father");
  }

  const unions = archiveRelationships
    .findSpouseFamilies(person.id)
    .map((family) => {
      const spouseId = archiveRelationships.getOtherSpouseId(
        family,
        person.id,
      );

      return {
        family,
        spouse:
          (spouseId ? peopleById.get(spouseId) : null) ??
          createUnknownSpouse(family.id),
        children: (family.children ?? [])
          .map((childId) => peopleById.get(childId))
          .filter(Boolean),
      };
    });

  const familyUnits = buildFamilyUnits(person, unions);

  return {
    selected: person,
    parents: {
      father,
      mother,
    },
    unions,
    familyUnits,
  };
}

function formatFamilyUnitRelationship(family, primaryPerson, spouse) {
  const marriageYear = archiveDates.extractYear(family?.marriage_date);

  if (!marriageYear) {
    return "";
  }

  if (family?.divorced) {
    const divorceYear = archiveDates.extractYear(family.divorce_date);
    return `m. ${marriageYear}–${divorceYear ?? "?"} · divorced`;
  }

  const primaryDeathYear = archiveDates.extractYear(primaryPerson?.death);
  const spouseDeathYear = archiveDates.extractYear(spouse?.death);
  const deathYears = [primaryDeathYear, spouseDeathYear].filter(
    (year) => year !== null,
  );

  if (deathYears.length > 0) {
    return `m. ${marriageYear}–${Math.min(...deathYears)}`;
  }

  if (primaryPerson?.living || spouse?.living) {
    return `m. ${marriageYear}–present`;
  }

  return `m. ${marriageYear}–?`;
}

function getParentRelationshipLabel(person, familyId) {
  const relationship = person.parent_relationships?.find(
    (entry) => entry.family === familyId,
  );

  switch (relationship?.type) {
    case "adopted":
      return "Adopted";
    default:
      return "";
  }
}

function measureFamilyUnit(unit) {
  const selectedWidth = unit?.isPrimary ? 238 : 214;
  const selectedHeight = unit?.isPrimary ? 106 : 78;
  const spouseWidth = 214;
  const spouseHeight = 96;

  const childWidth = 190;
  const childHeight = 78;
  const childGapX = 30;
  const childGapY = 54;
  const childrenTopGap = 62;
  const childrenPerRow = 4;
  const siblingBusGutter = 64;

  const familyUnitGap = 88;
  const divorcedUnionSeparation = 24;

  const childCount = unit?.children?.length ?? 0;
  const widestChildRowCount = Math.min(childrenPerRow, childCount);

  const widestChildRowWidth = widestChildRowCount
    ? widestChildRowCount * childWidth +
      (widestChildRowCount - 1) * childGapX
    : 0;

  const unitWidth = Math.max(
    spouseWidth,
    siblingBusGutter + widestChildRowWidth,
  );

  return {
    selectedWidth,
    selectedHeight,
    spouseWidth,
    spouseHeight,
    childWidth,
    childHeight,
    childGapX,
    childGapY,
    childrenTopGap,
    childrenPerRow,
    siblingBusGutter,
    familyUnitGap,
    divorcedUnionSeparation,
    unitWidth,
  };
}

function prepareFamilyUnitLayouts(units) {
  return units.map((unit) => ({
    ...unit,
    ownerKey: "selected",
    measurements: measureFamilyUnit(unit),
  }));
}

function layoutFamilyUnit(
  unit,
  unitIndex,
  selectedCard,
  unitLeft,
  spouseY,
) {
  const union = unit.union;
  const measurements = unit.measurements;
  const children = [...unit.children].sort((a, b) => {
    const dateDifference =
      archiveDates.birthYearSortValue(a) -
      archiveDates.birthYearSortValue(b);

    return dateDifference || a.name.localeCompare(b.name);
  });

  const unitCenterX = unitLeft + measurements.unitWidth / 2;
  const spouseSeparation = union.family?.divorced
    ? measurements.divorcedUnionSeparation
    : 0;

  const spouseCard = {
    key: `spouse-${unitIndex}`,
    person: union.spouse,
    union,
    selected: false,
    x: unitCenterX - measurements.spouseWidth / 2,
    y: spouseY + spouseSeparation,
    width: measurements.spouseWidth,
    height: measurements.spouseHeight,
  };

  const firstChildY =
    spouseCard.y +
    spouseCard.height +
    measurements.childrenTopGap;

  const childCards = children.map((child, childIndex) => {
    const row = Math.floor(childIndex / measurements.childrenPerRow);
    const column = childIndex % measurements.childrenPerRow;
    const rowStart = row * measurements.childrenPerRow;

    const rowCount = Math.min(
      measurements.childrenPerRow,
      children.length - rowStart,
    );

    const rowWidth =
      rowCount * measurements.childWidth +
      (rowCount - 1) * measurements.childGapX;

    const rowLeft =
      unitLeft + measurements.siblingBusGutter;

    const relationshipLabels = [
      getParentRelationshipLabel(child, union.family.id),
    ].filter(Boolean);

    return {
      key: `union-${unitIndex}-child-${childIndex}`,
      person: child,
      union,
      selected: false,
      relationshipLabels,
      x:
        rowLeft +
        column * (measurements.childWidth + measurements.childGapX),
      y:
        firstChildY +
        row * (measurements.childHeight + measurements.childGapY),
      width: measurements.childWidth,
      height:
        measurements.childHeight +
        relationshipLabels.length * 18 +
        (relationshipLabels.length > 0 ? 12 : 0),
    };
  });

  return {
    id: unit.id,
    ownerKey: unit.ownerKey,
    left: unitLeft,
    width: measurements.unitWidth,
    centerX: unitCenterX,
    siblingBusX:
      unitLeft + measurements.siblingBusGutter / 2,
    spouseCard,
    childCards,
    anchor: {
      x: unitCenterX,
      y: spouseCard.y,
    },
    spouseAnchor: {
      x: unitCenterX,
      y: spouseCard.y,
    },
    childAnchor: {
      x: unitCenterX,
      y: spouseCard.y + spouseCard.height,
    },
    unionCenterX: unitCenterX,
    isPrimary: unit.isPrimary,
  };
}

function layoutPrimaryFamily(model) {
  const person = model.selected;
  const father = model.parents.father;
  const mother = model.parents.mother;

  const parentY = 20;
  const selectedY = 214;

  const parentWidth = 214;
  const parentHeight = 78;
  const parentGap = 54;

  const familyCenterX = 600;
  const fallbackUnit = {
    primaryPerson: person,
    spouse: null,
    children: [],
    isPrimary: true,
  };

  const preparedUnits = prepareFamilyUnitLayouts(
    model.familyUnits.length ? model.familyUnits : [fallbackUnit],
  );

  const primaryUnit = preparedUnits[0];
  const measurements = primaryUnit.measurements;
  const layoutUnits = model.familyUnits.length ? preparedUnits : [];

  const relationshipLabels = layoutUnits
    .map((unit) =>
      formatFamilyUnitRelationship(
        unit.union.family,
        unit.primaryPerson ?? person,
        unit.union.spouse,
      ),
    )
    .filter(Boolean);

  const selectedX = familyCenterX - measurements.selectedWidth / 2;

  const selectedCard = {
    key: "selected",
    person,
    selected: true,
    relationshipLabels,
    x: selectedX,
    y: selectedY,
    width: measurements.selectedWidth,
    height:
      measurements.selectedHeight +
      relationshipLabels.length * 18 +
      (relationshipLabels.length > 0 ? 12 : 0),
  };

  const selectedCenterX = selectedCard.x + selectedCard.width / 2;
  const parentPairWidth = parentWidth * 2 + parentGap;
  const parentPairLeft = selectedCenterX - parentPairWidth / 2;

  const fatherCard = {
    key: "father",
    person: father,
    selected: false,
    x: parentPairLeft,
    y: parentY,
    width: parentWidth,
    height: parentHeight,
  };

  const motherCard = {
    key: "mother",
    person: mother,
    selected: false,
    x: parentPairLeft + parentWidth + parentGap,
    y: parentY,
    width: parentWidth,
    height: parentHeight,
  };

  return {
    father,
    mother,
    selectedY,
    selectedCard,
    fatherCard,
    motherCard,
    layoutUnits,
  };
}


function buildRelationshipModel(father, mother, unionLayouts) {
  const relationships = [];

  if (father && mother) {
    relationships.push({
      type: "parent-union",
      from: "father",
      to: "mother",
      axisOwner: "selected",
    });
  }

  unionLayouts.forEach(
    (
      {
        ownerKey,
        spouseCard,
        childCards,
        anchor,
        spouseAnchor,
        childAnchor,
        siblingBusX,
        isPrimary,
      },
      marriageOrder,
    ) => {
      relationships.push({
        type: "family-unit",
        from: ownerKey,
        spouse: spouseCard.key,
        children: childCards.map((card) => card.key),
        anchorX: anchor.x,
        spouseAnchor,
        childAnchor,
        siblingBusX,
        isPrimary,
        marriageOrder,
        marriageCount: unionLayouts.length,
        divorced: Boolean(spouseCard.union?.family?.divorced),
      });
    },
  );

  return relationships;
}

function buildCardModel(
  fatherCard,
  motherCard,
  selectedCard,
  unionLayouts,
) {
  return [
    fatherCard,
    motherCard,
    selectedCard,
    ...unionLayouts.flatMap(({ spouseCard, childCards }) => [
      spouseCard,
      ...childCards,
    ]),
  ];
}

function calculateLayoutBounds(cards, selectedCard) {
  const visibleCards = cards.filter((card) => card.person);

  const leftmostCardEdge = visibleCards.reduce(
    (leftmost, card) => Math.min(leftmost, card.x),
    selectedCard.x,
  );

  const rightmostCardEdge = visibleCards.reduce(
    (rightmost, card) => Math.max(rightmost, card.x + card.width),
    selectedCard.x + selectedCard.width,
  );

  const lowestCardBottom = visibleCards.reduce(
    (lowest, card) => Math.max(lowest, card.y + card.height),
    selectedCard.y + selectedCard.height,
  );

  const horizontalPadding = 92;
  const topPadding = 18;

  return {
    x: leftmostCardEdge - horizontalPadding,
    y: topPadding,
    width: Math.max(
      900,
      rightmostCardEdge - leftmostCardEdge + horizontalPadding * 2,
    ),
    height: Math.max(630, lowestCardBottom + 82 - topPadding),
  };
}

function layoutFamilyUnits(
  layoutUnits,
  selectedCard,
  selectedY,
) {
  if (layoutUnits.length === 0) {
    return [];
  }

  const familyUnitGap = layoutUnits[0].measurements.familyUnitGap;
  const singleMarriageTopGap = 46;
  const additionalMarriageClearance = 16;
  const familyUnitsTopGap =
    singleMarriageTopGap +
    Math.max(0, layoutUnits.length - 1) *
      additionalMarriageClearance;

  const familyUnitsWidth =
    layoutUnits.reduce(
      (total, unit) => total + unit.measurements.unitWidth,
      0,
    ) +
    familyUnitGap * (layoutUnits.length - 1);

  const selectedCenterX =
    selectedCard.x + selectedCard.width / 2;

  let nextUnitLeft =
    selectedCenterX - familyUnitsWidth / 2;

  const spouseY =
    selectedY +
    selectedCard.height +
    familyUnitsTopGap;

  return layoutUnits.map((unit, unitIndex) => {
    const layout = layoutFamilyUnit(
      unit,
      unitIndex,
      selectedCard,
      nextUnitLeft,
      spouseY,
    );

    nextUnitLeft +=
      unit.measurements.unitWidth +
      unit.measurements.familyUnitGap;

    return layout;
  });
}

function buildLayout(model) {
  const {
    father,
    mother,
    selectedY,
    selectedCard,
    fatherCard,
    motherCard,
    layoutUnits,
  } = layoutPrimaryFamily(model);

  const unionLayouts = layoutFamilyUnits(
    layoutUnits,
    selectedCard,
    selectedY,
  );

  const cards = buildCardModel(
    fatherCard,
    motherCard,
    selectedCard,
    unionLayouts,
  );

  const relationships = buildRelationshipModel(
    father,
    mother,
    unionLayouts,
  );

  return {
    cards,
    relationships,
    viewBox: calculateLayoutBounds(cards, selectedCard),
  };
}

function drawCards(cards) {
  for (const card of cards) {
    if (!card.person) {
      continue;
    }

    drawPersonCard(card.person, card.x, card.y, {
      width: card.width,
      height: card.height,
      selected: card.selected,
      relationshipLabels: card.relationshipLabels,
    });
  }
}

function roundedOrthogonalPath(points, radius = 42) {
  if (points.length < 2) {
    return "";
  }

  const commands = [`M ${points[0].x} ${points[0].y}`];

  for (let index = 1; index < points.length - 1; index += 1) {
    const previous = points[index - 1];
    const current = points[index];
    const next = points[index + 1];

    const incomingDistance = Math.hypot(
      current.x - previous.x,
      current.y - previous.y,
    );
    const outgoingDistance = Math.hypot(next.x - current.x, next.y - current.y);
    const cornerRadius = Math.min(
      radius,
      incomingDistance / 2,
      outgoingDistance / 2,
    );

    const incomingPoint = {
      x: current.x - Math.sign(current.x - previous.x) * cornerRadius,
      y: current.y - Math.sign(current.y - previous.y) * cornerRadius,
    };
    const outgoingPoint = {
      x: current.x + Math.sign(next.x - current.x) * cornerRadius,
      y: current.y + Math.sign(next.y - current.y) * cornerRadius,
    };

    commands.push(`L ${incomingPoint.x} ${incomingPoint.y}`);
    commands.push(
      `Q ${current.x} ${current.y} ${outgoingPoint.x} ${outgoingPoint.y}`,
    );
  }

  const finalPoint = points.at(-1);
  commands.push(`L ${finalPoint.x} ${finalPoint.y}`);

  return commands.join(" ");
}

function drawRoundedRelationship(
  points,
  radius = 42,
  className = "relationship-line",
) {
  drawRelationshipPath(
    roundedOrthogonalPath(points, radius),
    className,
  );
}

function drawDivorceMarker(x, y) {
  const halfWidth = 4.5;
  const markerGap = 3.5;
  const markerRise = 4;
  const marker = createSvgElement("g", {
    class: "divorce-marker",
    "aria-hidden": "true",
  });

  const upperBreak = createSvgElement("line", {
    x1: x - halfWidth,
    y1: y - markerGap - markerRise,
    x2: x + halfWidth,
    y2: y - markerGap + markerRise,
  });

  const lowerBreak = createSvgElement("line", {
    x1: x - halfWidth,
    y1: y + markerGap - markerRise,
    x2: x + halfWidth,
    y2: y + markerGap + markerRise,
  });

  marker.append(upperBreak, lowerBreak);
  stage.append(marker);
}


function drawRelationshipLines(cards, relationships) {
  const cardMap = Object.fromEntries(
    cards.map((card) => [card.key, card]),
  );

  const edgeOverlap = 1.5;
  const cornerRadius = 46;
  const branchRadius = 22;

  for (const relationship of relationships) {
    if (relationship.type === "parent-union") {
      const fromCard = cardMap[relationship.from];
      const toCard = cardMap[relationship.to];
      const axisOwnerCard =
        cardMap[relationship.axisOwner];

      if (!(fromCard && toCard && axisOwnerCard)) {
        continue;
      }

      const fromBox = getCardGeometry(fromCard);
      const toBox = getCardGeometry(toCard);
      const axisOwnerBox =
        getCardGeometry(axisOwnerCard);
      const parentUnionX = (fromBox.right + toBox.left) / 2;
      const descentY = axisOwnerBox.top - 34;

      drawRoundedRelationship([
        {
          x: fromBox.right - edgeOverlap,
          y: fromBox.centerY,
        },
        {
          x: toBox.left + edgeOverlap,
          y: toBox.centerY,
        },
      ]);

      drawRoundedRelationship(
        [
          {
            x: parentUnionX,
            y: fromBox.centerY,
          },
          {
            x: parentUnionX,
            y: descentY,
          },
          {
            x: axisOwnerBox.centerX,
            y: descentY,
          },
          {
            x: axisOwnerBox.centerX,
            y: axisOwnerBox.top + edgeOverlap,
          },
        ],
        cornerRadius,
      );
    }

    if (relationship.type === "family-unit") {
      const ownerCard = cardMap[relationship.from];
      const spouseCard = cardMap[relationship.spouse];

      if (!(ownerCard && spouseCard)) {
        continue;
      }

      const ownerBox = getCardGeometry(ownerCard);
      const spouseBox = getCardGeometry(spouseCard);
      const childCards = (relationship.children || [])
        .map((key) => cardMap[key])
        .filter(Boolean);

      const unitAnchorX =
        relationship.anchorX ?? spouseBox.centerX;

      const marriageOrder = relationship.marriageOrder ?? 0;
      const marriageCount = relationship.marriageCount ?? 1;
      const firstLaneY = ownerBox.bottom + 34;
      const laneGap = 10;
      const laneOrder = marriageOrder;
      const laneY = firstLaneY + laneOrder * laneGap;

      const ownerWidth = ownerBox.right - ownerBox.left;
      const ownerLanePadding = Math.min(44, ownerWidth / 4);
      const ownerLaneWidth =
        ownerWidth - ownerLanePadding * 2;

      const ownerLaneX =
        marriageCount === 1
          ? ownerBox.centerX
          : ownerBox.left +
            ownerLanePadding +
            ownerLaneWidth *
              (marriageOrder / (marriageCount - 1));

      if (relationship.divorced) {
        const divorceMarkerX = unitAnchorX;
        const divorceMarkerY =
          laneY + (spouseBox.top - laneY) * 0.4;
        const divorceGapHalf = 6;

        drawRoundedRelationship(
          [
            {
              x: ownerLaneX,
              y: ownerBox.bottom - edgeOverlap,
            },
            {
              x: ownerLaneX,
              y: laneY,
            },
            {
              x: unitAnchorX,
              y: laneY,
            },
            {
              x: unitAnchorX,
              y: divorceMarkerY - divorceGapHalf,
            },
          ],
          branchRadius,
          "relationship-line marriage-line",
        );

        drawRelationshipPath(
          [
            `M ${unitAnchorX} ${divorceMarkerY + divorceGapHalf}`,
            `V ${spouseBox.top + edgeOverlap}`,
          ].join(" "),
          "relationship-line marriage-line",
        );

        drawDivorceMarker(
          divorceMarkerX,
          divorceMarkerY,
        );
      } else {
        drawRoundedRelationship(
          [
            {
              x: ownerLaneX,
              y: ownerBox.bottom - edgeOverlap,
            },
            {
              x: ownerLaneX,
              y: laneY,
            },
            {
              x: unitAnchorX,
              y: laneY,
            },
            {
              x: unitAnchorX,
              y: spouseBox.top + edgeOverlap,
            },
          ],
          branchRadius,
          "relationship-line marriage-line",
        );
      }

      if (childCards.length === 0) {
        continue;
      }

      const rowGroups = new Map();

      childCards.forEach((card) => {
        const row = rowGroups.get(card.y) || [];
        row.push(card);
        rowGroups.set(card.y, row);
      });

      const rows = [...rowGroups.values()]
        .sort((a, b) => a[0].y - b[0].y)
        .map((rowCards) => ({
          cards: rowCards.sort(
            (a, b) => a.x - b.x,
          ),
          busY: rowCards[0].y - 24,
        }));

      const firstChildBusY = rows[0].busY;
      const lastChildBusY = rows.at(-1).busY;
      const usesWrappedRows = rows.length > 1;
      const siblingBusX = relationship.siblingBusX;

      if (usesWrappedRows) {
        drawRelationshipPath(
          [
            `M ${unitAnchorX} ${spouseBox.bottom - edgeOverlap}`,
            `V ${firstChildBusY - branchRadius}`,
            `Q ${unitAnchorX} ${firstChildBusY} ${unitAnchorX - branchRadius} ${firstChildBusY}`,
            `H ${siblingBusX}`,
            `V ${lastChildBusY}`,
          ].join(" "),
        );
      } else {
        drawRelationshipPath(
          [
            `M ${unitAnchorX} ${spouseBox.bottom - edgeOverlap}`,
            `V ${firstChildBusY}`,
          ].join(" "),
        );
      }

      rows.forEach(
        ({
          cards: rowCards,
          busY: childBusY,
        }) => {
          const rowBoxes = rowCards.map(getCardGeometry);
          const firstCenterX = rowBoxes[0].centerX;
          const lastCenterX = rowBoxes.at(-1).centerX;

          const rowBusStartX = usesWrappedRows
            ? siblingBusX
            : Math.min(firstCenterX, unitAnchorX);

          const rowBusEndX = Math.max(
            lastCenterX,
            usesWrappedRows ? siblingBusX : unitAnchorX,
          );

          drawRelationshipPath(
            `M ${rowBusStartX} ${childBusY} H ${rowBusEndX}`,
          );

          rowBoxes.forEach((box) => {
            drawRelationshipPath(
              [
                `M ${box.centerX} ${childBusY}`,
                `V ${box.top + edgeOverlap}`,
              ].join(" "),
            );
          });
        },
      );
    }
  }
}

let renderTransitionId = 0;

function renderFamilyView(person) {
  const transitionId = ++renderTransitionId;
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  const render = () => {
    if (transitionId !== renderTransitionId) {
      return;
    }

    stage.replaceChildren();

    const model = buildFamilyViewModel(person);
    const layout = buildLayout(model);

    svg.setAttribute(
      "viewBox",
      `${layout.viewBox.x} ${layout.viewBox.y} ${layout.viewBox.width} ${layout.viewBox.height}`,
    );

    drawRelationshipLines(layout.cards, layout.relationships);
    drawCards(layout.cards);

    stage.classList.remove("tree-stage-exiting");

    if (!prefersReducedMotion) {
      stage.classList.add("tree-stage-entering");

      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          if (transitionId === renderTransitionId) {
            stage.classList.remove("tree-stage-entering");
          }
        });
      });
    }
  };

  if (prefersReducedMotion || !stage.childElementCount) {
    render();
    return;
  }

  stage.classList.remove("tree-stage-entering");
  stage.classList.add("tree-stage-exiting");
  window.setTimeout(render, 170);
}

function selectPerson(personId, options = {}) {
  const { updateHistory = true } = options;
  const person = peopleById.get(personId);

  if (!person) {
    return;
  }

  pedigreeLink.href = `tree.html?person=${encodeURIComponent(person.id)}`;

  renderFamilyView(person);

  if (updateHistory) {
    const url = new URL(window.location.href);
    url.searchParams.set("person", person.id);
    window.history.pushState({ personId: person.id }, "", url);
  }
}

function renderError(message) {
  stage.replaceChildren();

  svg.setAttribute("viewBox", "0 0 1200 700");

  const text = createSvgElement("text", {
    class: "error-message",
    x: 600,
    y: 350,
  });

  text.textContent = message;
  stage.append(text);
}

function placeStatusUnderHeading() {
  const heading = document.querySelector(".site-header h1");

  if (!heading || !statusElement) {
    return;
  }

  statusElement.classList.add("header-tree-status");
  heading.insertAdjacentElement("afterend", statusElement);
}

async function loadFamilyArchive() {
  try {
    const response = await fetch(`public-data/family.json?v=${Date.now()}`);

    if (!response.ok) {
      throw new Error(
        `Family data request failed with status ${response.status}.`,
      );
    }

    const data = await response.json();

    archiveData.setData(data);
    archiveSearch.setPeople(archiveData.people);

    peopleById = archiveData.peopleById;
    familiesById = archiveData.familiesById;

    console.log(
      `Loaded ${peopleById.size} people and ${familiesById.size} families.`,
    );

    const requestedPersonId = getRequestedPersonId();
    const selectedPerson = peopleById.get(requestedPersonId);

    if (!selectedPerson) {
      throw new Error(
        `Person ${requestedPersonId} was not found in the archive.`,
      );
    }

    selectPerson(selectedPerson.id, { updateHistory: false });
    searchInput.value = selectedPerson.name;

    statusElement.textContent = `${peopleById.size} individuals • ${familiesById.size} families`;
  } catch (error) {
    console.error("Unable to load family archive:", error);

    statusElement.textContent = "Unable to load family archive";
    renderError("The family tree could not be loaded.");
  }
}

placeStatusUnderHeading();
setupSearch();

window.addEventListener("popstate", () => {
  const personId = getRequestedPersonId();
  selectPerson(personId, { updateHistory: false });
});

loadFamilyArchive();
