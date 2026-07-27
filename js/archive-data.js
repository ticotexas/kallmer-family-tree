/*
 * Archive Data
 * Shared owner of archive records and primary lookup maps.
 */

"use strict";

class ArchiveData {
  constructor() {
    this.people = [];
    this.families = [];
    this.peopleById = new Map();
    this.familiesById = new Map();
  }

  setData(data = {}) {
    const { people, families } = data;

    if (!Array.isArray(people) || !Array.isArray(families)) {
      throw new Error("Family data has an unexpected structure.");
    }

    this.people = [...people];
    this.families = [...families];

    this.peopleById = new Map(
      this.people.map((person) => [person.id, person]),
    );

    this.familiesById = new Map(
      this.families.map((family) => [family.id, family]),
    );
  }

  getPerson(id) {
    return this.peopleById.get(id) ?? null;
  }

  getFamily(id) {
    return this.familiesById.get(id) ?? null;
  }
}

window.ArchiveData = ArchiveData;
