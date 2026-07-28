/*
 * Archive Relationships
 * Shared relationship queries over archive family records.
 */

"use strict";

class ArchiveRelationships {
  constructor(archiveData) {
    if (!archiveData) {
      throw new Error("ArchiveRelationships requires ArchiveData.");
    }

    this.archiveData = archiveData;
  }

  findParentFamily(personId) {
    return [...this.archiveData.familiesById.values()].find(
      (family) =>
        Array.isArray(family.children) &&
        family.children.includes(personId),
    );
  }

  findSpouseFamilies(personId) {
    return [...this.archiveData.familiesById.values()].filter(
      (family) =>
        family.husband === personId || family.wife === personId,
    );
  }

  getOtherSpouseId(family, personId) {
    if (family.husband === personId) {
      return family.wife;
    }

    if (family.wife === personId) {
      return family.husband;
    }

    return null;
  }
}

window.ArchiveRelationships = ArchiveRelationships;
