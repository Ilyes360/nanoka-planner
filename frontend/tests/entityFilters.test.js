import { describe, expect, it } from "vitest";
import {
  CHARACTER_FILTER_GROUPS,
  collectFilterOptions,
  emptyFilterState,
  filterEntities,
  hasActiveFilters,
  WEAPON_FILTER_GROUPS,
  WEAPON_TYPE_ORDER,
} from "../src/utils/entityFilters.js";

const CHARACTERS = [
  { name: "Ayaka", element: "Cryo", weapon_type: "Sword", rarity: "5★" },
  { name: "Bennett", element: "Pyro", weapon_type: "Sword", rarity: "4★" },
  { name: "Ganyu", element: "Cryo", weapon_type: "Bow", rarity: "5★" },
];

describe("collectFilterOptions", () => {
  it("retourne les valeurs distinctes triées selon l'ordre du jeu", () => {
    expect(collectFilterOptions(CHARACTERS, "element", ["Pyro", "Cryo", "Geo"])).toEqual(["Pyro", "Cryo"]);
    expect(collectFilterOptions(CHARACTERS, "weapon_type", WEAPON_TYPE_ORDER)).toEqual(["Sword", "Bow"]);
  });
});

describe("filterEntities", () => {
  it("combine recherche texte et filtres par facettes", () => {
    const selected = emptyFilterState(CHARACTER_FILTER_GROUPS);
    selected.element.add("Cryo");
    selected.weapon_type.add("Sword");

    const result = filterEntities(CHARACTERS, {
      query: "",
      selectedFilters: selected,
      filterKeys: ["element", "weapon_type", "rarity"],
    });
    expect(result.map((c) => c.name)).toEqual(["Ayaka"]);
  });

  it("applique un OR intra-groupe et un AND inter-groupes", () => {
    const selected = emptyFilterState(CHARACTER_FILTER_GROUPS);
    selected.element.add("Cryo");
    selected.element.add("Pyro");

    const result = filterEntities(CHARACTERS, {
      selectedFilters: selected,
      filterKeys: ["element"],
    });
    expect(result).toHaveLength(3);
  });

  it("filtre par rareté", () => {
    const selected = emptyFilterState(CHARACTER_FILTER_GROUPS);
    selected.rarity.add("4★");

    const result = filterEntities(CHARACTERS, {
      selectedFilters: selected,
      filterKeys: ["rarity"],
    });
    expect(result.map((c) => c.name)).toEqual(["Bennett"]);
  });
});

describe("hasActiveFilters", () => {
  it("detecte les selections actives", () => {
    const empty = emptyFilterState(WEAPON_FILTER_GROUPS);
    expect(hasActiveFilters(empty)).toBe(false);
    empty.rarity.add("5★");
    expect(hasActiveFilters(empty)).toBe(true);
  });
});
