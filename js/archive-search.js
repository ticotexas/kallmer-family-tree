/*
 * Archive Search
 * Shared person search component used throughout the archive.
 */

"use strict";

class ArchiveSearch {
  constructor(options = {}) {
    this.options = options;

    this.people = [];
    this.peopleById = new Map();
    this.searchablePeople = [];
  }

  setPeople(people = []) {
    this.people = [...people];

    this.peopleById = new Map(
      this.people.map((person) => [person.id, person]),
    );

    this.searchablePeople = [];
  }

  getPerson(id) {
    return this.peopleById.get(id) ?? null;
  }
}

window.ArchiveSearch = ArchiveSearch;
