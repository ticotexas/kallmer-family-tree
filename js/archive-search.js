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

  normalizeText(text) {
    return String(text ?? "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/ł/g, "l")
      .replace(/ø/g, "o")
      .replace(/æ/g, "ae")
      .replace(/œ/g, "oe")
      .replace(/ð/g, "d")
      .replace(/þ/g, "th");
  }

  setPeople(people = []) {
    this.people = [...people];

    this.peopleById = new Map(
      this.people.map((person) => [person.id, person]),
    );

    this.searchablePeople = this.people.map((person) => ({
      person,
      searchName: this.normalizeText(person.name),
    }));
  }

  search(query, limit = 12) {
    const normalizedQuery = this.normalizeText(query.trim());

    if (normalizedQuery.length < 2) {
      return [];
    }

    return this.searchablePeople
      .filter(({ searchName }) => searchName.includes(normalizedQuery))
      .slice(0, limit)
      .map(({ person }) => person);
  }

  getPerson(id) {
    return this.peopleById.get(id) ?? null;
  }
}

window.ArchiveSearch = ArchiveSearch;
