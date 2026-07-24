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
  const birthYear = yearFromText(person.birth);
  const deathYear = yearFromText(person.death);

  if (person.living || !person.death) {
    return `${birthYear} –`;
  }

  return `${birthYear} – ${deathYear}`;
}

function splitNameIntoLines(name) {
  const words = String(name || "").trim().split(/\s+/).filter(Boolean);

  if (words.length < 2) {
    return [name];
  }

  return [
    words.slice(0, -1).join(" "),
    words.at(-1),
  ];
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

function drawPersonCard(person, x, y, options = {}) {
  if (!person) {
    return;
  }

  const { width = 240, height = 92, selected = false } = options;
  const nameLines = splitNameIntoLines(person.name);
  const hasProfileLink = selected;
  const nameStartY = nameLines.length > 1
    ? (hasProfileLink ? 27 : 22)
    : (hasProfileLink ? 34 : 28);
  const dateY = nameLines.length > 1
    ? (hasProfileLink ? 64 : 59)
    : (hasProfileLink ? 58 : 53);

  const group = createSvgElement("g", {
    class: "person-card-group",
    transform: `translate(${x} ${y})`,
    tabindex: "0",
    role: "button",
    "aria-label": selected
      ? `${person.name}, selected. Recenter tree.`
      : `${person.name}. Recenter tree around this person.`,
  });

  const card = createSvgElement("rect", {
    class: selected ? "person-card selected-person-card" : "person-card",
    width,
    height,
    rx: 7,
    ry: 7,
  });

  const accent = createSvgElement("rect", {
    class: selected
      ? "person-card-accent selected-person-accent"
      : "person-card-accent",
    width: selected ? 7 : 5,
    height,
    rx: 3,
    ry: 3,
  });

  group.append(card, accent);

  const name = createSvgElement("text", {
    class: person.name.length > 25
      ? "person-name long-person-name"
      : "person-name",
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
    class: "person-dates",
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

  const recenter = () => selectPerson(person.id);

  group.addEventListener("click", recenter);
  group.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      recenter();
    }
  });

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

function buildFamilyViewModel(person) {
  const parentFamily = findParentFamily(person.id);

  const father = parentFamily?.husband
    ? peopleById.get(parentFamily.husband)
    : null;

  const mother = parentFamily?.wife ? peopleById.get(parentFamily.wife) : null;

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

  return {
    selected: person,
    parents: {
      father,
      mother,
    },
    unions,
  };
}

function birthSortValue(person) {
  const match = String(person?.birth || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return match ? Number(match[1]) : Number.POSITIVE_INFINITY;
}

function buildLayout(model) {
  const person = model.selected;
  const father = model.parents.father;
  const mother = model.parents.mother;

  const secondaryHeight = 82;
  const parentWidth = 220;
  const parentHeight = secondaryHeight;
  const selectedWidth = 250;
  const selectedHeight = 112;
  const spouseWidth = 220;
  const spouseHeight = secondaryHeight;
  const childWidth = 190;
  const childHeight = secondaryHeight;
  const childGap = 16;
  const childrenPerRow = 3;
  const childrenTopGap = 44;
  const unionGap = 50;
  const unionStartY = 205;

  const unionLayouts = [];
  let nextUnionY = unionStartY;

  model.unions.forEach((union, unionIndex) => {
    const children = [...union.children].sort((a, b) => {
      const dateDifference = birthSortValue(a) - birthSortValue(b);
      return dateDifference || a.name.localeCompare(b.name);
    });

    const childRows = Math.ceil(children.length / childrenPerRow);
    const childrenHeight = childRows > 0
      ? childRows * childHeight + (childRows - 1) * childGap
      : 0;

    const blockHeight = spouseHeight +
      (childRows > 0 ? childrenTopGap + childrenHeight : 0);

    const spouseCard = {
      key: `spouse-${unionIndex}`,
      person: union.spouse,
      union,
      selected: false,
      x: 730,
      y: nextUnionY,
      width: spouseWidth,
      height: spouseHeight,
    };

    const childCards = children.map((child, childIndex) => {
      const column = childIndex % childrenPerRow;
      const row = Math.floor(childIndex / childrenPerRow);

      return {
        key: `union-${unionIndex}-child-${childIndex}`,
        person: child,
        union,
        selected: false,
        x: 720 + column * (childWidth + childGap),
        y: nextUnionY + spouseHeight + childrenTopGap +
          row * (childHeight + childGap),
        width: childWidth,
        height: childHeight,
      };
    });

    unionLayouts.push({
      unionIndex,
      spouseCard,
      childCards,
      blockHeight,
    });

    nextUnionY += blockHeight + unionGap;
  });

  const unionStackHeight = unionLayouts.length > 0
    ? nextUnionY - unionStartY - unionGap
    : 0;

  const primarySpouseCard = unionLayouts[0]?.spouseCard || null;

  const selectedCard = {
    key: "selected",
    person,
    selected: true,
    x: 440,
    // Keep the focused person and the primary spouse on the same
    // horizontal relationship line. Because the selected card is taller,
    // align their vertical centers rather than their top edges.
    y: primarySpouseCard
      ? primarySpouseCard.y + spouseHeight / 2 - selectedHeight / 2
      : 250,
    width: selectedWidth,
    height: selectedHeight,
  };

  const cards = [
    {
      key: "father",
      person: father,
      selected: false,
      x: 350,
      y: 60,
      width: parentWidth,
      height: parentHeight,
    },
    {
      key: "mother",
      person: mother,
      selected: false,
      x: 630,
      y: 60,
      width: parentWidth,
      height: parentHeight,
    },
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

  unionLayouts.forEach(({ spouseCard, childCards }) => {
    relationships.push({
      type: "spouse-union",
      from: "selected",
      to: spouseCard.key,
      children: childCards.map((card) => card.key),
    });
  });

  const visibleCards = cards.filter((card) => card.person);
  const lowestCardBottom = visibleCards.reduce(
    (lowest, card) => Math.max(lowest, card.y + card.height),
    selectedCard.y + selectedCard.height,
  );
  const rightmostCardEdge = visibleCards.reduce(
    (rightmost, card) => Math.max(rightmost, card.x + card.width),
    1200,
  );

  return {
    cards,
    relationships,
    viewBox: {
      x: 0,
      y: 0,
      width: Math.max(1200, rightmostCardEdge + 90),
      height: Math.max(700, lowestCardBottom + 110),
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

function drawRelationshipLines(cards, relationships) {
  const cardMap = Object.fromEntries(cards.map((card) => [card.key, card]));
  const edgeOverlap = 1.5;

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
      const unionMidpointX = (fromBox.right + toBox.left) / 2;
      const descentY = childBox.top - 30;

      drawRelationshipSegments([
        `M ${fromBox.right - edgeOverlap} ${fromBox.centerY} H ${toBox.left + edgeOverlap}`,
        `M ${unionMidpointX} ${fromBox.centerY} V ${descentY} H ${childBox.centerX} V ${childBox.top + edgeOverlap}`,
      ]);
    }

    if (relationship.type === "spouse-union") {
      const fromCard = cardMap[relationship.from];
      const toCard = cardMap[relationship.to];

      if (!(fromCard && toCard)) {
        continue;
      }

      const fromBox = getCardGeometry(fromCard);
      const toBox = getCardGeometry(toCard);
      const elbowX = fromBox.right + 24;
      const unionAnchorX = (elbowX + toBox.left) / 2;
      const segments = [
        `M ${fromBox.right - edgeOverlap} ${fromBox.centerY} H ${elbowX} V ${toBox.centerY} H ${toBox.left + edgeOverlap}`,
      ];

      const childCards = (relationship.children || [])
        .map((key) => cardMap[key])
        .filter(Boolean);

      if (childCards.length > 0) {
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
            busY: rowCards[0].y - 18,
          }));

        segments.push(`M ${unionAnchorX} ${toBox.centerY} V ${rows.at(-1).busY}`);

        rows.forEach(({ cards: rowCards, busY }) => {
          const rowBoxes = rowCards.map(getCardGeometry);
          const firstCenterX = rowBoxes[0].centerX;
          const lastCenterX = rowBoxes.at(-1).centerX;

          segments.push(
            `M ${Math.min(unionAnchorX, firstCenterX)} ${busY} H ${Math.max(unionAnchorX, lastCenterX)}`,
          );

          rowBoxes.forEach((box) => {
            segments.push(`M ${box.centerX} ${busY} V ${box.top + edgeOverlap}`);
          });
        });
      }

      drawRelationshipSegments(segments);
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

window.addEventListener("popstate", () => {
  const personId = getRequestedPersonId();
  selectPerson(personId, { updateHistory: false });
});

loadFamilyArchive();
