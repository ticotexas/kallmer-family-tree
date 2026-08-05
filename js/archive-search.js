/*
 * Archive Search
 * Shared person search component used throughout the archive.
 */

"use strict";

class ArchiveSearch {
  constructor(options = {}) {
    this.options = options;

    this.people = [];
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

  getSearchableNameText(person) {
    const names = [person.name];

    if (person.nickname) {
      names.push(person.nickname);
    }

    if (person.birth_name) {
      names.push(person.birth_name);
    }

    if (Array.isArray(person.alternate_names)) {
      person.alternate_names.forEach((entry) => {
        if (typeof entry === "string") {
          names.push(entry);
        } else if (entry?.name) {
          names.push(entry.name);
        }
      });
    }

    return names.filter(Boolean).join(" ");
  }

  setPeople(people = []) {
    this.people = [...people];

    this.searchablePeople = this.people.map((person) => ({
      person,
      searchName: this.normalizeText(
        this.getSearchableNameText(person),
      ),
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
}

window.ArchiveSearch = ArchiveSearch;
