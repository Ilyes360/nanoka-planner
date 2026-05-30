import { filterByName } from "../utils.js";

/** Ordre d'affichage des filtres (style Genshin). */
export const ELEMENT_ORDER = ["Pyro", "Hydro", "Electro", "Cryo", "Anemo", "Geo", "Dendro"];
export const WEAPON_TYPE_ORDER = ["Sword", "Claymore", "Polearm", "Bow", "Catalyst"];
export const RARITY_ORDER = ["5★", "4★", "3★", "2★", "1★"];

export const CHARACTER_FILTER_GROUPS = [
  { key: "element", label: "Element", order: ELEMENT_ORDER },
  { key: "weapon_type", label: "Weapon", order: WEAPON_TYPE_ORDER },
  { key: "rarity", label: "Rarity", order: RARITY_ORDER },
];

export const WEAPON_FILTER_GROUPS = [
  { key: "weapon_type", label: "Type", order: WEAPON_TYPE_ORDER },
  { key: "rarity", label: "Rarity", order: RARITY_ORDER },
];

function sortByOrder(values, order) {
  const rank = new Map(order.map((v, i) => [v, i]));
  return [...values].sort((a, b) => {
    const ra = rank.has(a) ? rank.get(a) : order.length;
    const rb = rank.has(b) ? rank.get(b) : order.length;
    return ra - rb || a.localeCompare(b, "en");
  });
}

/** Valeurs distinctes presentes dans la liste, triees selon l'ordre du jeu. */
export function collectFilterOptions(items, key, order) {
  const values = new Set();
  for (const item of items) {
    const value = String(item[key] || "").trim();
    if (value) values.add(value);
  }
  return sortByOrder(values, order);
}

function matchesFacetFilters(item, selectedFilters, filterKeys) {
  for (const key of filterKeys) {
    const selected = selectedFilters[key];
    if (!selected?.size) continue;
    const value = String(item[key] || "").trim();
    if (!selected.has(value)) return false;
  }
  return true;
}

/** Filtre par nom puis par facettes (OR intra-groupe, AND inter-groupes). */
export function filterEntities(items, { query = "", selectedFilters = {}, filterKeys = [] } = {}) {
  let result = filterByName(items, query);
  if (!filterKeys.length) return result;
  return result.filter((item) => matchesFacetFilters(item, selectedFilters, filterKeys));
}

export function hasActiveFilters(selectedFilters) {
  return Object.values(selectedFilters).some((set) => set?.size > 0);
}

export function emptyFilterState(groups) {
  const state = {};
  for (const { key } of groups) state[key] = new Set();
  return state;
}

export function cloneFilterState(state) {
  const next = {};
  for (const [key, set] of Object.entries(state)) {
    next[key] = new Set(set);
  }
  return next;
}
