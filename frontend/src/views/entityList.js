import { apiClient } from "../apiClient.js";
import { renderEntityFilters } from "../components/entityFilters.js";
import { el } from "../utils.js";
import {
  CHARACTER_FILTER_GROUPS,
  emptyFilterState,
  filterEntities,
  WEAPON_FILTER_GROUPS,
} from "../utils/entityFilters.js";
import { entityIconRarityClass } from "../utils/entityRarity.js";

function renderEntityCard(entity, linkPrefix) {
  const iconChild = entity.icon_url
    ? el("img", { src: entity.icon_url, alt: "", loading: "lazy" })
    : el("span", { className: "entity-card__placeholder", text: entity.name.charAt(0) });

  const rarityClass = entityIconRarityClass(entity.rarity);
  const iconClassName = rarityClass ? `entity-card__icon ${rarityClass}` : "entity-card__icon";

  const card = el(
    "a",
    { href: `${linkPrefix}/${entity.id}`, className: "entity-card", "data-link": "" },
    [el("div", { className: iconClassName }, [iconChild]), el("span", { className: "entity-card__name", text: entity.name })],
  );

  card.addEventListener("mouseenter", () => {
    const load = linkPrefix === "/characters" ? apiClient.character : apiClient.weapon;
    load(entity.id).catch(() => {});
  }, { once: true });

  return card;
}

function renderSearchField(placeholder, onQueryChange) {
  let query = "";

  const input = el("input", {
    type: "search",
    className: "search",
    placeholder,
    autocomplete: "off",
    spellcheck: "false",
    onInput: () => {
      query = input.value;
      onQueryChange(query);
    },
  });

  const clearBtn = el("button", {
    type: "button",
    className: "search-field__clear",
    "aria-label": "Clear search",
    text: "×",
    hidden: "true",
    onClick: () => {
      query = "";
      input.value = "";
      input.focus();
      onQueryChange(query);
    },
  });

  const field = el("div", { className: "search-field" }, [input, clearBtn]);

  function sync(queryValue) {
    query = queryValue;
    const active = query.trim().length > 0;
    field.classList.toggle("search-field--active", active);
    clearBtn.toggleAttribute("hidden", !active);
  }

  return { field, input, sync, getQuery: () => query };
}

export async function renderEntityList(container, { title, placeholder, load, linkPrefix, filterGroups = [] }) {
  container.replaceChildren(el("p", { className: "status", text: "Loading…" }));

  let items = [];
  try {
    items = await load();
  } catch (err) {
    container.replaceChildren(
      el("p", {
        className: "status status--error",
        text: `Could not load the list. Is the API running? (${err.message})`,
      }),
    );
    return;
  }

  let selectedFilters = emptyFilterState(filterGroups);
  const filterKeys = filterGroups.map((group) => group.key);

  const countEl = el("p", { className: "muted list-count" });
  const gridEl = el("div", { className: "entity-grid" });
  const emptyEl = el("p", { className: "muted list-empty", text: "No results.", hidden: "true" });
  const filtersSlot = el("div", { className: "list-toolbar__filters" });

  const search = renderSearchField(placeholder, (query) => {
    search.sync(query);
    updateResults();
  });

  const toolbar = el("div", { className: "list-toolbar" }, [search.field]);
  if (filterGroups.length) toolbar.append(filtersSlot);

  const root = el("div", { className: "list-page" }, [
    el("header", { className: "page-header" }, [
      el("h1", { text: title }),
      toolbar,
    ]),
    countEl,
    gridEl,
    emptyEl,
  ]);

  container.replaceChildren(root);

  function renderFilters() {
    if (!filterGroups.length) return;
    const filters = renderEntityFilters({
      groups: filterGroups,
      items,
      selected: selectedFilters,
      onChange: (next) => {
        selectedFilters = next;
        updateResults();
        renderFilters();
      },
    });
    filtersSlot.replaceChildren(filters ?? []);
  }

  function updateResults() {
    const query = search.getQuery();
    const filtered = filterEntities(items, { query, selectedFilters, filterKeys });

    countEl.textContent = `${filtered.length} / ${items.length}`;
    countEl.classList.toggle("list-count--filtered", filtered.length !== items.length);

    gridEl.replaceChildren(...filtered.map((entity) => renderEntityCard(entity, linkPrefix)));

    if (filtered.length) {
      emptyEl.setAttribute("hidden", "true");
    } else {
      emptyEl.removeAttribute("hidden");
    }
  }

  renderFilters();
  updateResults();
}

export function charactersList(container) {
  return renderEntityList(container, {
    title: "Characters",
    placeholder: "Search for a character…",
    load: () => apiClient.characters(),
    linkPrefix: "/characters",
    filterGroups: CHARACTER_FILTER_GROUPS,
  });
}

export function weaponsList(container) {
  return renderEntityList(container, {
    title: "Weapons",
    placeholder: "Search for a weapon…",
    load: () => apiClient.weapons(),
    linkPrefix: "/weapons",
    filterGroups: WEAPON_FILTER_GROUPS,
  });
}
