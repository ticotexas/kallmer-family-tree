"use strict";

const DEFAULT_PERSON_ID = "I0000";
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

const svg = document.getElementById("family-tree");
const stage = document.getElementById("tree-stage");
const statusElement = document.getElementById("tree-status");

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

function yearFromText(value) {
  const match = String(value || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return match ? match[1] : "?";
}

function formatLifeYears(person) {
  if (person.placeholder) {
    return "Research continuing";
  }

  const birthYear = yearFromText(person.birth);
  const deathYear = yearFromText(person.death);

  if (person.living || !person.death) {
    return `${birthYear} –`;
  }

  return `${birthYear} – ${deathYear}`;
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

function findParentFamily(personId) {
  return [...familiesById.values()].find(
    (family) =>
      Array.isArray(family.children) && family.children.includes(personId),
  );
}

function findSpouseFamilies(personId) {
  return [...familiesById.values()].filter(
    (family) => family.husband === personId || family.wife === personId,
  );
}

function getOtherSpouseId(family, personId) {
  if (family.husband === personId) {
    return family.wife;
  }

  if (family.wife === personId) {
    return family.husband;
  }

  return null;
}

function getGenderAccentClass(person) {
  if (person?.placeholder) {
    return "unknown-person-accent";
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

  const { width = 240, height = 92, selected = false } = options;
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
    ...(isPlaceholder
      ? {}
      : {
          tabindex: "0",
          role: "button",
          "aria-label": selected
            ? `${person.name}, selected. Recenter tree.`
            : `${person.name}. Recenter tree around this person.`,
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
      y: height - 12,
    });

    profileText.textContent = "View Profile";
    profileLink.append(profileHitbox, profileText);
    profileLink.addEventListener("click", (event) => event.stopPropagation());
    group.append(profileLink);
  }

  if (!isPlaceholder) {
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

function drawRelationshipPath(pathData) {
  const path = createSvgElement("path", {
    class: "relationship-line",
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

function buildFamilyUnits(person, unions) {
  return unions.map((union, unionIndex) => ({
    id: union.family.id,
    union,
    primaryPerson: person,
    spouse: union.spouse,
    children: union.children,
    isPrimary: unionIndex === 0,
  }));
}

function buildFamilyViewModel(person) {
  const parentFamily = findParentFamily(person.id);

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

  const unions = findSpouseFamilies(person.id)
    .map((family) => {
      const spouseId = getOtherSpouseId(family, person.id);

      return {
        family,
        spouse: spouseId ? peopleById.get(spouseId) : null,
        children: (family.children ?? [])
          .map((childId) => peopleById.get(childId))
          .filter(Boolean),
      };
    })
    .filter((union) => union.spouse);

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

function birthSortValue(person) {
  const match = String(person?.birth || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY;
}

function measureFamilyUnit(unit) {
  const selectedWidth = unit?.isPrimary ? 238 : 214;
  const selectedHeight = unit?.isPrimary ? 106 : 78;
  const spouseWidth = 214;
  const spouseHeight = 78;
  const spouseGap = 62;

  const childWidth = 190;
  const childHeight = 78;
  const childGapX = 30;
  const childGapY = 22;
  const childrenTopGap = 62;
  const childrenPerRow = 3;
  const unitBlockGap = 72;

  const coupleWidth = unit?.spouse
    ? selectedWidth + spouseGap + spouseWidth
    : selectedWidth;

  return {
    selectedWidth,
    selectedHeight,
    spouseWidth,
    spouseHeight,
    spouseGap,
    childWidth,
    childHeight,
    childGapX,
    childGapY,
    childrenTopGap,
    childrenPerRow,
    unitBlockGap,
    coupleWidth,
  };
}

function measureFamilyUnits(units) {
  return units.map((unit) => ({
    ...unit,
    measurements: measureFamilyUnit(unit),
  }));
}

function buildLayout(model) {
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

  const measuredUnits = measureFamilyUnits(
    model.familyUnits.length ? model.familyUnits : [fallbackUnit],
  );

  const primaryUnit = measuredUnits[0];
  const measurements = primaryUnit.measurements;
  const layoutUnits = model.familyUnits.length ? measuredUnits : [];

  const selectedX = familyCenterX - measurements.coupleWidth / 2;

  const selectedCard = {
    key: "selected",
    person,
    selected: true,
    x: selectedX,
    y: selectedY,
    width: measurements.selectedWidth,
    height: measurements.selectedHeight,
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

  const unionLayouts = [];
  let nextUnionTop = selectedY;

  layoutUnits.forEach((unit, unitIndex) => {
    const union = unit.union;
    const unitMeasurements = unit.measurements;
    const children = [...unit.children].sort((a, b) => {
      const dateDifference = birthSortValue(a) - birthSortValue(b);

      return dateDifference || a.name.localeCompare(b.name);
    });

    const isPrimary = unit.isPrimary;

    const spouseCard = {
      key: `spouse-${unitIndex}`,
      person: union.spouse,
      union,
      selected: false,
      x: selectedCard.x + selectedCard.width + unitMeasurements.spouseGap,
      y: isPrimary
        ? selectedY +
          (unitMeasurements.selectedHeight - unitMeasurements.spouseHeight) / 2
        : nextUnionTop,
      width: unitMeasurements.spouseWidth,
      height: unitMeasurements.spouseHeight,
    };

    const unionCenterX =
      (selectedCard.x + selectedCard.width + spouseCard.x) / 2;

    const firstChildY =
      Math.max(
        selectedCard.y + selectedCard.height,
        spouseCard.y + spouseCard.height,
      ) + unitMeasurements.childrenTopGap;

    const childCards = children.map((child, childIndex) => {
      const row = Math.floor(childIndex / unitMeasurements.childrenPerRow);

      const column = childIndex % unitMeasurements.childrenPerRow;

      const rowStart = row * unitMeasurements.childrenPerRow;

      const rowCount = Math.min(unitMeasurements.childrenPerRow, children.length - rowStart);

      const rowWidth = rowCount * unitMeasurements.childWidth +
        (rowCount - 1) * unitMeasurements.childGapX;

      const rowLeft = unionCenterX - rowWidth / 2;

      return {
        key: `union-${unitIndex}-child-${childIndex}`,
        person: child,
        union,
        selected: false,
        x: rowLeft +
          column * (unitMeasurements.childWidth + unitMeasurements.childGapX),
        y: firstChildY +
          row * (unitMeasurements.childHeight + unitMeasurements.childGapY),
        width: unitMeasurements.childWidth,
        height: unitMeasurements.childHeight,
      };
    });

    const childrenBottom = childCards.length
      ? Math.max(...childCards.map((card) => card.y + card.height))
      : spouseCard.y + spouseCard.height;

    unionLayouts.push({
      spouseCard,
      childCards,
      unionCenterX,
      isPrimary,
    });

    nextUnionTop = childrenBottom + unitMeasurements.unitBlockGap;
  });

  const cards = [
    fatherCard,
    motherCard,
    selectedCard,
    ...unionLayouts.flatMap(({ spouseCard, childCards }) => [
      spouseCard,
      ...childCards,
    ]),
  ];

  const relationships = [];

  if (father && mother) {
    relationships.push({
      type: "parent-union",
      from: "father",
      to: "mother",
      child: "selected",
    });
  }

  unionLayouts.forEach(
    ({ spouseCard, childCards, unionCenterX, isPrimary }) => {
      relationships.push({
        type: "spouse-union",
        from: "selected",
        to: spouseCard.key,
        children: childCards.map((card) => card.key),
        unionCenterX,
        isPrimary,
      });
    },
  );

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
    cards,
    relationships,
    viewBox: {
      x: leftmostCardEdge - horizontalPadding,
      y: topPadding,
      width: Math.max(
        900,
        rightmostCardEdge - leftmostCardEdge + horizontalPadding * 2,
      ),
      height: Math.max(630, lowestCardBottom + 82 - topPadding),
    },
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

function drawRoundedRelationship(points, radius = 42) {
  drawRelationshipPath(roundedOrthogonalPath(points, radius));
}

function drawRelationshipLines(cards, relationships) {
  const cardMap = Object.fromEntries(cards.map((card) => [card.key, card]));
  const edgeOverlap = 1.5;
  const cornerRadius = 46;

  for (const relationship of relationships) {
    if (relationship.type === "parent-union") {
      const fromCard = cardMap[relationship.from];
      const toCard = cardMap[relationship.to];
      const childCard = cardMap[relationship.child];

      if (!(fromCard && toCard && childCard)) {
        continue;
      }

      const fromBox = getCardGeometry(fromCard);
      const toBox = getCardGeometry(toCard);
      const childBox = getCardGeometry(childCard);
      const parentUnionX = (fromBox.right + toBox.left) / 2;
      const descentY = childBox.top - 34;

      drawRoundedRelationship([
        { x: fromBox.right - edgeOverlap, y: fromBox.centerY },
        { x: toBox.left + edgeOverlap, y: toBox.centerY },
      ]);

      drawRoundedRelationship(
        [
          { x: parentUnionX, y: fromBox.centerY },
          { x: parentUnionX, y: descentY },
          { x: childBox.centerX, y: descentY },
          { x: childBox.centerX, y: childBox.top + edgeOverlap },
        ],
        cornerRadius,
      );
    }

    if (relationship.type === "spouse-union") {
      const fromCard = cardMap[relationship.from];
      const toCard = cardMap[relationship.to];

      if (!(fromCard && toCard)) {
        continue;
      }

      const fromBox = getCardGeometry(fromCard);
      const toBox = getCardGeometry(toCard);
      const childCards = (relationship.children || [])
        .map((key) => cardMap[key])
        .filter(Boolean);

      if (relationship.isPrimary) {
        drawRoundedRelationship([
          { x: fromBox.right - edgeOverlap, y: fromBox.centerY },
          { x: toBox.left + edgeOverlap, y: toBox.centerY },
        ]);
      } else {
        const elbowX = fromBox.right + 34;
        drawRoundedRelationship(
          [
            { x: fromBox.right - edgeOverlap, y: fromBox.centerY },
            { x: elbowX, y: fromBox.centerY },
            { x: elbowX, y: toBox.centerY },
            { x: toBox.left + edgeOverlap, y: toBox.centerY },
          ],
          cornerRadius,
        );
      }

      if (childCards.length === 0) {
        continue;
      }

      const unionAnchorX =
        relationship.unionCenterX ?? (fromBox.right + toBox.left) / 2;
      const rowGroups = new Map();

      childCards.forEach((card) => {
        const row = rowGroups.get(card.y) || [];
        row.push(card);
        rowGroups.set(card.y, row);
      });

      const rows = [...rowGroups.values()]
        .sort((a, b) => a[0].y - b[0].y)
        .map((rowCards) => ({
          cards: rowCards.sort((a, b) => a.x - b.x),
          busY: rowCards[0].y - 24,
        }));

      const firstBusY = rows[0].busY;
      const lastBusY = rows.at(-1).busY;

      const branchRadius = 22;

      rows.forEach(({ cards: rowCards, busY }, rowIndex) => {
        const rowBoxes = rowCards.map(getCardGeometry);
        const firstCenterX = rowBoxes[0].centerX;
        const lastCenterX = rowBoxes.at(-1).centerX;
        const trunkStartY =
          rowIndex === 0 ? fromBox.centerY : rows[rowIndex - 1].busY;

        if (firstCenterX < unionAnchorX) {
          drawRelationshipPath(
            [
              `M ${unionAnchorX} ${trunkStartY}`,
              `V ${busY - branchRadius}`,
              `Q ${unionAnchorX} ${busY} ${unionAnchorX - branchRadius} ${busY}`,
              `H ${firstCenterX}`,
            ].join(" "),
          );
        } else {
          drawRelationshipPath(`M ${unionAnchorX} ${trunkStartY} V ${busY}`);
        }

        if (lastCenterX > unionAnchorX) {
          drawRelationshipPath(
            [
              `M ${unionAnchorX} ${busY - branchRadius}`,
              `Q ${unionAnchorX} ${busY} ${unionAnchorX + branchRadius} ${busY}`,
              `H ${lastCenterX}`,
            ].join(" "),
          );
        }

        rowBoxes.forEach((box) => {
          drawRelationshipPath(
            `M ${box.centerX} ${busY} V ${box.top + edgeOverlap}`,
          );
        });
      });
    }
  }
}

function renderFamilyView(person) {
  stage.replaceChildren();

  const model = buildFamilyViewModel(person);
  const layout = buildLayout(model);

  svg.setAttribute(
    "viewBox",
    `${layout.viewBox.x} ${layout.viewBox.y} ${layout.viewBox.width} ${layout.viewBox.height}`,
  );

  drawRelationshipLines(layout.cards, layout.relationships);
  drawCards(layout.cards);
}

function selectPerson(personId, options = {}) {
  const { updateHistory = true } = options;
  const person = peopleById.get(personId);

  if (!person) {
    return;
  }

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

    if (!Array.isArray(data.people) || !Array.isArray(data.families)) {
      throw new Error("Family data has an unexpected structure.");
    }

    peopleById = new Map(data.people.map((person) => [person.id, person]));

    familiesById = new Map(data.families.map((family) => [family.id, family]));

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

    statusElement.textContent = `${peopleById.size} individuals • ${familiesById.size} families`;
  } catch (error) {
    console.error("Unable to load family archive:", error);

    statusElement.textContent = "Unable to load family archive";
    renderError("The family tree could not be loaded.");
  }
}

placeStatusUnderHeading();

window.addEventListener("popstate", () => {
  const personId = getRequestedPersonId();
  selectPerson(personId, { updateHistory: false });
});

loadFamilyArchive();
