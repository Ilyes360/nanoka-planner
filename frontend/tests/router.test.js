/**
 * @vitest-environment jsdom
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Les vues sont mockées : le routeur ne doit dépendre que de leur appel,
// pas de leur rendu réel (qui déclencherait des fetch réseau).
vi.mock("../src/views/home.js", () => ({
  renderHome: vi.fn(() => {
    const node = document.createElement("div");
    node.className = "home";
    return node;
  }),
}));
vi.mock("../src/views/entityList.js", () => ({
  charactersList: vi.fn(),
  weaponsList: vi.fn(),
}));
vi.mock("../src/views/characterDetail.js", () => ({
  renderCharacterDetail: vi.fn(),
}));
vi.mock("../src/views/weaponDetail.js", () => ({
  renderWeaponDetail: vi.fn(),
}));

import { renderHome } from "../src/views/home.js";
import { charactersList, weaponsList } from "../src/views/entityList.js";
import { renderCharacterDetail } from "../src/views/characterDetail.js";
import { renderWeaponDetail } from "../src/views/weaponDetail.js";
import { initRouter, navigate } from "../src/router.js";

beforeEach(() => {
  vi.clearAllMocks();
  window.scrollTo = vi.fn();
  history.replaceState(null, "", "/");
  document.body.innerHTML = `
    <nav class="nav">
      <a href="/characters">Characters</a>
      <a href="/weapons">Weapons</a>
    </nav>
    <main id="app"></main>
  `;
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("navigate — routage", () => {
  it("rend la home sur '/'", () => {
    navigate("/");
    expect(renderHome).toHaveBeenCalledTimes(1);
    expect(document.querySelector("#app .home")).not.toBeNull();
  });

  it("rend la liste des personnages sur '/characters'", () => {
    navigate("/characters");
    expect(charactersList).toHaveBeenCalledTimes(1);
    expect(charactersList).toHaveBeenCalledWith(document.getElementById("app"));
  });

  it("rend le détail d'un personnage sur '/characters/:id'", () => {
    navigate("/characters/10000002");
    expect(renderCharacterDetail).toHaveBeenCalledWith(
      document.getElementById("app"),
      "10000002",
    );
  });

  it("rend la liste des armes sur '/weapons'", () => {
    navigate("/weapons");
    expect(weaponsList).toHaveBeenCalledTimes(1);
  });

  it("rend le détail d'une arme sur '/weapons/:id'", () => {
    navigate("/weapons/11401");
    expect(renderWeaponDetail).toHaveBeenCalledWith(
      document.getElementById("app"),
      "11401",
    );
  });

  it("retombe sur la home pour une route inconnue", () => {
    navigate("/unknown/deep/route");
    expect(renderHome).toHaveBeenCalledTimes(1);
    expect(charactersList).not.toHaveBeenCalled();
    expect(window.location.pathname).toBe("/");
  });

  it("ignore les segments vides (slash final)", () => {
    navigate("/characters/");
    expect(charactersList).toHaveBeenCalledTimes(1);
    expect(renderCharacterDetail).not.toHaveBeenCalled();
  });
});

describe("navigate — historique et navigation active", () => {
  it("pousse une entrée d'historique quand le chemin change", () => {
    const spy = vi.spyOn(history, "pushState");
    navigate("/characters");
    expect(spy).toHaveBeenCalledWith(null, "", "/characters");
    expect(window.location.pathname).toBe("/characters");
  });

  it("ne pousse pas d'historique avec push: false", () => {
    const spy = vi.spyOn(history, "pushState");
    navigate("/weapons", { push: false });
    expect(spy).not.toHaveBeenCalled();
  });

  it("active le lien de nav correspondant et désactive les autres", () => {
    navigate("/characters");
    const [charLink, weaponLink] = document.querySelectorAll(".nav a");
    expect(charLink.classList.contains("active")).toBe(true);
    expect(weaponLink.classList.contains("active")).toBe(false);
  });

  it("active le lien parent sur une page de détail", () => {
    navigate("/characters/10000002");
    const charLink = document.querySelector('.nav a[href="/characters"]');
    expect(charLink.classList.contains("active")).toBe(true);
  });

  it("n'active aucun lien sur la home", () => {
    navigate("/");
    const active = document.querySelectorAll(".nav a.active");
    expect(active).toHaveLength(0);
  });
});

describe("initRouter — délégation de clic et popstate", () => {
  it("intercepte le clic sur un lien [data-link] et navigue", () => {
    document.body.innerHTML = `
      <a id="link" href="/characters" data-link="">Characters</a>
      <main id="app"></main>
    `;
    initRouter();
    vi.clearAllMocks();

    document.getElementById("link").click();

    expect(charactersList).toHaveBeenCalledTimes(1);
    expect(window.location.pathname).toBe("/characters");
  });

  it("ignore les clics hors d'un lien [data-link]", () => {
    document.body.innerHTML = `
      <button id="ext">Pas un lien</button>
      <main id="app"></main>
    `;
    initRouter();
    vi.clearAllMocks();

    document.getElementById("ext").click();
    expect(charactersList).not.toHaveBeenCalled();
  });

  it("réagit à l'événement popstate", () => {
    document.body.innerHTML = '<main id="app"></main>';
    history.replaceState(null, "", "/weapons");
    initRouter();
    vi.clearAllMocks();

    window.dispatchEvent(new PopStateEvent("popstate"));
    expect(weaponsList).toHaveBeenCalled();
  });
});
