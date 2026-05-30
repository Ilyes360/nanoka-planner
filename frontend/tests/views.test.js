/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/apiClient.js", () => ({
  apiClient: {
    characters: vi.fn(),
    character: vi.fn(),
    weapons: vi.fn(),
    weapon: vi.fn(),
  },
}));

import { apiClient } from "../src/apiClient.js";
import { renderCharacterDetail } from "../src/views/characterDetail.js";
import { renderWeaponDetail } from "../src/views/weaponDetail.js";
import { charactersList, weaponsList } from "../src/views/entityList.js";

const CHARACTER = {
  id: "10000002",
  name: "Kamisato Ayaka",
  title: "Frostflake Heron",
  element: "Cryo",
  weapon_type: "Sword",
  rarity: "5★",
  description: "Daughter of the Yashiro Commission's Kamisato Clan.",
  icon_url: "/media/characters/ayaka_icon.webp",
  splash_url: "/media/characters/ayaka_splash.webp",
  ascension: {
    ascensions: [
      {
        at_level: 20,
        mora: 1000,
        materials: [{ name: "Sakura Bloom", count: 3, item_id: "112002" }],
        leveling: {
          to_level: 20,
          mora_cost: 500,
          books: [{ name: "Wanderer's Advice", count: 2, item_id: 104001 }],
        },
      },
    ],
  },
  talents: {
    talents: [
      { track: 1, levels: [{ level: 2, mora: 100, materials: [{ name: "Sakura Bloom", count: 6 }] }] },
    ],
  },
};

const WEAPON = {
  id: "11401",
  name: "Mistsplitter Reforged",
  weapon_type: "Sword",
  rarity: "5★",
  description: "A blade that splits the mist.",
  icon_url: "/media/weapons/mistsplitter.webp",
  ascension: {
    ascensions: [
      {
        at_level: 20,
        mora: 500,
        materials: [],
        leveling: {
          to_level: 20,
          mora_cost: 100,
          ores: [{ name: "Enhancement Ore", count: 4, item_id: 104011 }],
        },
      },
    ],
  },
};

let app;

beforeEach(() => {
  vi.clearAllMocks();
  window.scrollTo = vi.fn();
  document.body.innerHTML = '<main id="app"></main>';
  app = document.getElementById("app");
});

describe("renderCharacterDetail", () => {
  it("affiche la page et les planificateurs en cas de succès", async () => {
    apiClient.character.mockResolvedValue(CHARACTER);

    await renderCharacterDetail(app, "10000002");

    expect(apiClient.character).toHaveBeenCalledWith("10000002");
    expect(app.querySelector(".character-page")).not.toBeNull();
    expect(app.querySelector(".character-page__name").textContent).toBe("Kamisato Ayaka");
    expect(app.querySelector(".character-page__avatar.rarity-frame--gold")).not.toBeNull();
    // un planner d'ascension + un planner de talents
    expect(app.querySelectorAll(".level-planner")).toHaveLength(2);
  });

  it("affiche un message d'erreur et un lien retour en cas d'échec", async () => {
    apiClient.character.mockRejectedValue(new Error("Not found"));

    await renderCharacterDetail(app, "999");

    const status = app.querySelector(".status--error");
    expect(status).not.toBeNull();
    expect(status.textContent).toContain("Not found");
    const back = status.querySelector('a[href="/characters"]');
    expect(back).not.toBeNull();
    expect(back.textContent).toBe("Back");
    expect(app.querySelector(".character-page")).toBeNull();
  });
});

describe("renderWeaponDetail", () => {
  it("affiche la page arme et un planner en cas de succès", async () => {
    apiClient.weapon.mockResolvedValue(WEAPON);

    await renderWeaponDetail(app, "11401");

    expect(app.querySelector(".weapon-page__name").textContent).toBe("Mistsplitter Reforged");
    expect(app.querySelector(".weapon-page__avatar.rarity-frame--gold")).not.toBeNull();
    expect(app.querySelectorAll(".level-planner")).toHaveLength(1);
  });

  it("affiche un message d'erreur avec lien vers /weapons", async () => {
    apiClient.weapon.mockRejectedValue(new Error("boom"));

    await renderWeaponDetail(app, "0");

    const back = app.querySelector('.status--error a[href="/weapons"]');
    expect(back).not.toBeNull();
  });
});

describe("entityList — charactersList / weaponsList", () => {
  const LIST = [
    { id: "1", name: "Albedo", element: "Geo", weapon_type: "Sword", rarity: "5★", icon_url: "/media/a.webp" },
    { id: "2", name: "Bennett", element: "Pyro", weapon_type: "Sword", rarity: "4★" },
    { id: "3", name: "Amber", element: "Pyro", weapon_type: "Bow", rarity: "4★", icon_url: "/media/am.webp" },
  ];

  it("affiche la grille et le compteur", async () => {
    apiClient.characters.mockResolvedValue(LIST);

    await charactersList(app);

    expect(app.querySelectorAll(".entity-card")).toHaveLength(3);
    expect(app.querySelector(".list-count").textContent).toBe("3 / 3");
    expect(app.querySelector("h1").textContent).toBe("Characters");
    expect(app.querySelector(".entity-card__icon.rarity-frame--gold")).not.toBeNull();
    expect(app.querySelector(".entity-card__icon.rarity-frame--purple")).not.toBeNull();
    expect(app.querySelector(".entity-filter-chip.rarity-frame--gold")).not.toBeNull();
    expect(app.querySelector('img.entity-filter-chip__icon[src*="Pyro.webp"]')).not.toBeNull();
  });

  it("filtre la liste via la recherche", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    const search = app.querySelector("input.search");
    search.value = "am";
    search.dispatchEvent(new Event("input"));

    // "Amber" uniquement (Albedo/Bennett ne contiennent pas "am")
    expect(app.querySelectorAll(".entity-card")).toHaveLength(1);
    expect(app.querySelector(".entity-card__name").textContent).toBe("Amber");
    expect(app.querySelector(".list-count").textContent).toBe("1 / 3");
  });

  it("affiche 'No results.' quand le filtre ne correspond à rien", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    const search = app.querySelector("input.search");
    search.value = "zzz";
    search.dispatchEvent(new Event("input"));

    expect(app.querySelectorAll(".entity-card")).toHaveLength(0);
    expect(app.textContent).toContain("No results.");
  });

  it("affiche une erreur si l'API échoue", async () => {
    apiClient.weapons.mockRejectedValue(new Error("API down"));

    await weaponsList(app);

    const status = app.querySelector(".status--error");
    expect(status).not.toBeNull();
    expect(status.textContent).toContain("API down");
  });

  it("affiche les filtres par element/arme/rareté pour les personnages", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    expect(app.querySelector(".entity-filters")).not.toBeNull();
    expect(app.textContent).toContain("Element");
    expect(app.textContent).toContain("Weapon");
    expect(app.textContent).toContain("Rarity");
    const chipLabels = [...app.querySelectorAll(".entity-filter-chip")].map((btn) => btn.textContent);
    expect(chipLabels).toContain("Pyro");
    expect(app.querySelector('img.entity-filter-chip__icon[src*="Pyro.webp"]')).not.toBeNull();
  });

  it("filtre par element via les puces", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    const geoChip = [...app.querySelectorAll(".entity-filter-chip")].find((btn) => btn.textContent === "Geo");
    geoChip.click();

    expect(app.querySelectorAll(".entity-card")).toHaveLength(1);
    expect(app.querySelector(".entity-card__name").textContent).toBe("Albedo");
    expect(app.querySelector(".list-count").textContent).toBe("1 / 3");
    expect(app.querySelector(".entity-filters__clear")).not.toBeNull();
  });

  it("combine recherche texte et filtres", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    const pyroChip = [...app.querySelectorAll(".entity-filter-chip")].find((btn) => btn.textContent === "Pyro");
    pyroChip.click();

    const search = app.querySelector("input.search");
    search.value = "ben";
    search.dispatchEvent(new Event("input"));

    expect(app.querySelectorAll(".entity-card")).toHaveLength(1);
    expect(app.querySelector(".entity-card__name").textContent).toBe("Bennett");
  });

  it("reinitialise les filtres avec Clear filters", async () => {
    apiClient.characters.mockResolvedValue(LIST);
    await charactersList(app);

    const geoChip = [...app.querySelectorAll(".entity-filter-chip")].find((btn) => btn.textContent === "Geo");
    geoChip.click();
    app.querySelector(".entity-filters__clear").click();

    expect(app.querySelectorAll(".entity-card")).toHaveLength(3);
    expect(app.querySelector(".entity-filters__clear")).toBeNull();
  });
});
