import { el } from "../utils.js";

function metaChip(text) {
  if (!text) return null;
  return el("span", { className: "weapon-page__chip", text });
}

function renderProfileHeader(data) {
  const chips = el(
    "div",
    { className: "weapon-page__chips" },
    [metaChip(data.weapon_type), metaChip(data.rarity)].filter(Boolean),
  );

  const identity = el("div", { className: "weapon-page__identity" }, [
    el("a", { href: "/weapons", className: "weapon-page__back", "data-link": "", text: "← Weapons" }),
    el("h1", { className: "weapon-page__name", text: data.name }),
    chips.childNodes.length ? chips : null,
    data.description ? el("p", { className: "weapon-page__desc", text: data.description }) : null,
  ]);

  const head = el("header", { className: "weapon-page__profile" }, [identity]);

  if (data.icon_url) {
    head.prepend(
      el("img", {
        className: "weapon-page__avatar",
        src: data.icon_url,
        alt: "",
        width: "112",
        height: "112",
        loading: "eager",
      }),
    );
  }

  return head;
}

/**
 * @param {object} data — réponse API /api/weapons/:id
 * @param {HTMLElement[]} plannerSections
 */
export function renderWeaponPage(data, plannerSections) {
  return el("article", { className: "weapon-page" }, [
    renderProfileHeader(data),
    el("div", { className: "weapon-page__planners" }, plannerSections),
  ]);
}
