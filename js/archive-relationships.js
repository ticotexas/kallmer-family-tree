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

  findFamilyForParentAndChild(parentId, childId) {
    return [...this.archiveData.familiesById.values()].find(
      (family) =>
        (family.husband === parentId || family.wife === parentId) &&
        Array.isArray(family.children) &&
        family.children.includes(childId),
    );
  }

  findSpouseFamilies(personId) {
    const person = this.archiveData.peopleById.get(personId);
    const orderedFamilyIds = person?.families_as_spouse;

    if (Array.isArray(orderedFamilyIds) && orderedFamilyIds.length > 0) {
      const orderedFamilies = orderedFamilyIds
        .map((familyId) => this.archiveData.familiesById.get(familyId))
        .filter(Boolean);

      if (orderedFamilies.length > 0) {
        return orderedFamilies;
      }
    }

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
