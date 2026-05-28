import { el } from "../utils.js";

function metaChip(text) {
  if (!text) return null;
  return el("span", { className: "character-page__chip", text });
}

function renderSplashBlock(data) {
  const src = data.splash_url || data.icon_url;
  if (!src) return null;

  const img = el("img", {
    className: `character-splash__img${data.splash_url ? "" : " character-splash__img--fallback"}`,
    src,
    alt: "",
    loading: "eager",
    decoding: "async",
  });

  return el("aside", { className: "character-splash", "aria-label": "Character illustration" }, [
    el("div", { className: "character-splash__frame" }, [img]),
  ]);
}

function renderProfileHeader(data) {
  const chips = el(
    "div",
    { className: "character-page__chips" },
    [metaChip(data.element), metaChip(data.weapon_type)].filter(Boolean),
  );

  const identity = el("div", { className: "character-page__identity" }, [
    el("a", { href: "/characters", className: "character-page__back", "data-link": "", text: "← Characters" }),
    el("h1", { className: "character-page__name", text: data.name }),
    data.title ? el("p", { className: "character-page__title", text: data.title }) : null,
    chips.childNodes.length ? chips : null,
    data.description ? el("p", { className: "character-page__desc", text: data.description }) : null,
  ]);

  const head = el("header", { className: "character-page__profile" }, [identity]);

  if (data.icon_url) {
    head.prepend(
      el("img", {
        className: "character-page__avatar",
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
 * @param {object} data — réponse API /api/characters/:id
 * @param {HTMLElement[]} plannerSections
 */
export function renderCharacterPage(data, plannerSections) {
  const splash = renderSplashBlock(data);
  const heroChildren = [renderProfileHeader(data)];
  if (splash) heroChildren.push(splash);

  return el("article", { className: "character-page" }, [
    el("div", { className: "character-page__hero" }, heroChildren),
    el("div", { className: "character-page__planners" }, plannerSections),
  ]);
}
