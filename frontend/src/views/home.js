import { el } from "../utils.js";

function renderGenshinCard() {
  return el("article", { className: "home-game home-game--genshin" }, [
    el("div", { className: "home-game__visual", "aria-hidden": "true" }, [
      el("span", { className: "home-game__mark", text: "GI" }),
    ]),
    el("div", { className: "home-game__body" }, [
      el("h3", { className: "home-game__name", text: "Genshin Impact" }),
      el("p", {
        className: "home-game__desc",
        text: "Ascensions, talents, and weapon leveling — materials, EXP books, ores, and Mora.",
      }),
      el("div", { className: "home-game__actions" }, [
        el("a", {
          href: "/characters",
          className: "home-game__btn home-game__btn--primary",
          "data-link": "",
          text: "Characters",
        }),
        el("a", { href: "/weapons", className: "home-game__btn", "data-link": "", text: "Weapons" }),
      ]),
    ]),
  ]);
}

export function renderHome() {
  return el("div", { className: "home" }, [
    el("header", { className: "home-hero" }, [
      el("p", { className: "home-hero__eyebrow", text: "Welcome" }),
      el("h1", { className: "home-hero__title", text: "Nanoka Planner" }),
      el("p", {
        className: "home-hero__lead",
        text: "Plan your in-game resources using Nanoka data. Pick a game to get started.",
      }),
    ]),
    el("section", { className: "home-games", "aria-labelledby": "home-games-title" }, [
      el("h2", { id: "home-games-title", className: "home-games__title", text: "Choose a game" }),
      el("p", {
        className: "home-games__subtitle",
        text: "More games can be added here in the future.",
      }),
      el("div", { className: "home-games__grid" }, [renderGenshinCard()]),
    ]),
  ]);
}
