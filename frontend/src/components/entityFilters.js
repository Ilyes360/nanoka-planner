import { el } from "../utils.js";
import { collectFilterOptions, hasActiveFilters } from "../utils/entityFilters.js";
import { elementIconUrl } from "../utils/elementIcon.js";
import { filterChipThemeClass } from "../utils/entityRarity.js";
import { weaponTypeIconUrl } from "../utils/weaponTypeIcon.js";

/**
 * Barre de filtres a puces (multi-selection par groupe).
 * @param {object} opts
 * @param {object[]} opts.groups — { key, label, order }
 * @param {object[]} opts.items — entites chargees (pour les options disponibles)
 * @param {Record<string, Set<string>>} opts.selected
 * @param {(next: Record<string, Set<string>>) => void} opts.onChange
 */
export function renderEntityFilters({ groups, items, selected, onChange }) {
  const optionGroups = groups
    .map((group) => ({
      ...group,
      options: collectFilterOptions(items, group.key, group.order),
    }))
    .filter((group) => group.options.length > 0);

  if (!optionGroups.length) return null;

  function toggle(key, value) {
    const next = {};
    for (const [k, set] of Object.entries(selected)) {
      next[k] = new Set(set);
    }
    const bucket = next[key] ?? new Set();
    if (bucket.has(value)) bucket.delete(value);
    else bucket.add(value);
    next[key] = bucket;
    onChange(next);
  }

  function clearAll() {
    const next = {};
    for (const { key } of groups) next[key] = new Set();
    onChange(next);
  }

  const sections = optionGroups.map((group) =>
    el("div", { className: "entity-filters__group" }, [
      el("span", { className: "entity-filters__label", text: group.label }),
      el(
        "div",
        { className: "entity-filters__chips", role: "group", "aria-label": group.label },
        group.options.map((option) => {
          const active = selected[group.key]?.has(option) ?? false;
          const themeClass = filterChipThemeClass(group.key, option);
          const chipClass = [
            "entity-filter-chip",
            `entity-filter-chip--${group.key}`,
            themeClass,
            active ? "entity-filter-chip--active" : "",
          ]
            .filter(Boolean)
            .join(" ");
          const chipChildren = [];
          if (group.key === "weapon_type") {
            const iconUrl = weaponTypeIconUrl(option);
            if (iconUrl) {
              chipChildren.push(el("img", {
                className: "entity-filter-chip__icon",
                src: iconUrl,
                alt: "",
                loading: "lazy",
              }));
            }
          } else if (group.key === "element") {
            const iconUrl = elementIconUrl(option);
            if (iconUrl) {
              chipChildren.push(el("img", {
                className: "entity-filter-chip__icon",
                src: iconUrl,
                alt: "",
                loading: "lazy",
              }));
            }
          }
          chipChildren.push(document.createTextNode(option));
          return el("button", {
            type: "button",
            className: chipClass,
            "aria-pressed": active ? "true" : "false",
            onClick: () => toggle(group.key, option),
          }, chipChildren);
        }),
      ),
    ]),
  );

  const children = [...sections];
  if (hasActiveFilters(selected)) {
    children.push(
      el("button", {
        type: "button",
        className: "entity-filters__clear",
        text: "Clear filters",
        onClick: clearAll,
      }),
    );
  }

  return el("div", { className: "entity-filters" }, children);
}
