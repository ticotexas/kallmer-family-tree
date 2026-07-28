/*
 * Archive Dates
 * Shared date parsing and chronological helpers.
 */

"use strict";

class ArchiveDates {
  extractYear(value) {
    const match = String(value || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
    return match ? Number(match[1]) : null;
  }

  birthYearSortValue(person) {
    return this.extractYear(person?.birth) ?? Number.POSITIVE_INFINITY;
  }

  birthDateSortValue(person) {
    const text = String(person?.birth || "").toUpperCase();

    const year = this.extractYear(text);
    if (year === null) {
      return Number.POSITIVE_INFINITY;
    }

    const months = {
      JAN:1,FEB:2,MAR:3,APR:4,MAY:5,JUN:6,
      JUL:7,AUG:8,SEP:9,OCT:10,NOV:11,DEC:12
    };

    const monthMatch =
      text.match(/\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b/);

    const month = monthMatch ? months[monthMatch[1]] : 1;

    const dayMatch =
      text.match(/\b([0-2]?\d|3[01])\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b/);

    const day = dayMatch ? Number(dayMatch[1]) : 1;

    return year * 10000 + month * 100 + day;
  }
}

window.ArchiveDates = ArchiveDates;
