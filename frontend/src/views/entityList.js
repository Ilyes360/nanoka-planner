import { apiClient } from "../apiClient.js";
import { el, filterByName } from "../utils.js";

function renderEntityCard(entity, linkPrefix) {
  const iconChild = entity.icon_url
    ? el("img", { src: entity.icon_url, alt: "", loading: "lazy" })
    : el("span", { className: "entity-card__placeholder", text: entity.name.charAt(0) });

  const card = el(
    "a",
    { href: `${linkPrefix}/${entity.id}`, className: "entity-card", "data-link": "" },
    [el("div", { className: "entity-card__icon" }, [iconChild]), el("span", { className: "entity-card__name", text: entity.name })],
  );

  card.addEventListener("mouseenter", () => {
    const load = linkPrefix === "/characters" ? apiClient.character : apiClient.weapon;
    load(entity.id).catch(() => {});
  }, { once: true });

  return card;
}

export async function renderEntityList(container, { title, placeholder, load, linkPrefix }) {
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

  let query = "";

  function paint() {
    const filtered = filterByName(items, query);
    const grid = el(
      "div",
      { className: "entity-grid" },
      filtered.map((entity) => renderEntityCard(entity, linkPrefix)),
    );

    const root = el("div", { className: "list-page" }, [
      el("header", { className: "page-header" }, [
        el("h1", { text: title }),
        el("input", {
          type: "search",
          className: "search",
          placeholder,
          value: query,
          onInput: (e) => {
            query = e.target.value;
            paint();
          },
        }),
      ]),
      el("p", { className: "muted list-count", text: `${filtered.length} / ${items.length}` }),
      grid,
    ]);

    if (!filtered.length) {
      root.append(el("p", { className: "muted", text: "No results." }));
    }
    container.replaceChildren(root);
  }

  paint();
}

export function charactersList(container) {
  return renderEntityList(container, {
    title: "Characters",
    placeholder: "Search for a character…",
    load: () => apiClient.characters(),
    linkPrefix: "/characters",
  });
}

export function weaponsList(container) {
  return renderEntityList(container, {
    title: "Weapons",
    placeholder: "Search for a weapon…",
    load: () => apiClient.weapons(),
    linkPrefix: "/weapons",
  });
}
