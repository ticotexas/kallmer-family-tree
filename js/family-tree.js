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

function formatLifeDates(person) {
  const birth = person.birth || "?";
  const death = person.death || "";

  if (person.living || !death) {
    return `${birth}–`;
  }

  return `${birth}–${death}`;
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

  const { width = 280, height = 130, selected = false, role = "" } = options;

  const group = createSvgElement("g", {
    transform: `translate(${x} ${y})`,
  });

  const card = createSvgElement("rect", {
    class: selected ? "person-card selected-person-card" : "person-card",
    width,
    height,
    rx: 8,
    ry: 8,
  });

  const accent = createSvgElement("rect", {
    class: selected
      ? "person-card-accent selected-person-accent"
      : "person-card-accent",
    width: selected ? 9 : 6,
    height,
    rx: 4,
    ry: 4,
  });

  group.append(card, accent);

  if (role) {
    const roleText = createSvgElement("text", {
      class: "person-role",
      x: width / 2,
      y: 25,
    });

    roleText.textContent = role;
    group.append(roleText);
  }

  const name = createSvgElement("text", {
    class:
      person.name.length > 24 ? "person-name long-person-name" : "person-name",
    x: width / 2,
    y: role ? 50 : 40,
  });

  name.textContent = person.name;

  const dates = createSvgElement("text", {
    class: "person-dates",
    x: width / 2,
    y: role ? 73 : 64,
  });

  dates.textContent = formatLifeDates(person);

  const personId = createSvgElement("text", {
    class: "person-id",
    x: width / 2,
    y: role ? 91 : 84,
  });

  personId.textContent = person.id;

  group.append(name, dates, personId);
  stage.append(group);
}

function drawRelationshipPath(pathData) {
  const path = createSvgElement("path", {
    class: "relationship-line",
    d: pathData,
  });

  stage.append(path);
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

function buildLayout(model) {
  const person = model.selected;
  const father = model.parents.father;
  const mother = model.parents.mother;
  const spouse = model.unions[0]?.spouse ?? null;

  const parentWidth = 220;
  const parentHeight = 95;
  const selectedWidth = 250;
  const selectedHeight = 115;

  const layout = {
    father: {
      x: 350,
      y: 80,
      width: parentWidth,
      height: parentHeight,
    },

    mother: {
      x: 630,
      y: 80,
      width: parentWidth,
      height: parentHeight,
    },

    selected: {
      x: 440,
      y: 250,
      width: selectedWidth,
      height: selectedHeight,
    },

    spouse: {
      x: 730,
      y: 260,
      width: parentWidth,
      height: parentHeight,
    },
  };

  const cards = [
    {
      key: "father",
      person: father,
      role: "Father",
      selected: false,
      ...layout.father,
    },
    {
      key: "mother",
      person: mother,
      role: "Mother",
      selected: false,
      ...layout.mother,
    },
    {
      key: "selected",
      person,
      role: "Selected person",
      selected: true,
      ...layout.selected,
    },
    {
      key: "spouse",
      person: spouse,
      union: model.unions[0] ?? null,
      role: "Spouse",
      selected: false,
      ...layout.spouse,
    },
  ];

  const relationships = [];

  if (model.parents.father && model.parents.mother) {
    relationships.push({
      type: "parent-union",
      from: "father",
      to: "mother",
      child: "selected",
    });
  }

  if (model.unions[0]?.spouse) {
    relationships.push({
      type: "spouse-union",
      from: "selected",
      to: "spouse",
    });
  }

  return {
    cards,
    relationships,
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
      role: card.role,
    });
  }
}

function drawRelationshipLines(cards, relationships) {
  const cardMap = Object.fromEntries(cards.map((card) => [card.key, card]));

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
      const descentY = childBox.top - 35;

      drawRelationshipPath(
        `M ${fromBox.right} ${fromBox.centerY} H ${toBox.left}`,
      );

      drawRelationshipPath(
        `M ${unionMidpointX} ${fromBox.centerY} ` +
          `V ${descentY} H ${childBox.centerX} V ${childBox.top}`,
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

      drawRelationshipPath(
        `M ${fromBox.right} ${fromBox.centerY} H ${toBox.left}`,
      );
    }
  }
}

function renderFamilyView(person) {
  const model = buildFamilyViewModel(person);

  const layout = buildLayout(model);

  drawRelationshipLines(layout.cards, layout.relationships);

  drawCards(layout.cards);
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

    renderFamilyView(selectedPerson);

    statusElement.textContent = `${peopleById.size} individuals • ${familiesById.size} families`;
  } catch (error) {
    console.error("Unable to load family archive:", error);

    statusElement.textContent = "Unable to load family archive";
    renderError("The family tree could not be loaded.");
  }
}

loadFamilyArchive();
