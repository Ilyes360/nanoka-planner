/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderMaterialList } from "../src/components/materialList.js";
import { renderMaterialCard, renderMaterialGrid } from "../src/components/materialCard.js";
import { renderLevelingBlock } from "../src/components/levelingBlock.js";
import { renderAscensionPlanner } from "../src/components/ascensionPlanner.js";
import { renderLevelPlanner } from "../src/components/levelPlanner.js";
import { renderTalentPlanner } from "../src/components/talentPlanner.js";
import { renderCharacterPage } from "../src/components/characterPage.js";
import { renderWeaponPage } from "../src/components/weaponPage.js";
import {
  renderPlannerHeader,
  renderPlannerSplashBackdrop,
} from "../src/components/plannerHero.js";

beforeEach(() => {
  document.body.innerHTML = "";
});

describe("renderMaterialList", () => {
  it("affiche le libellé vide quand il n'y a pas de matériaux", () => {
    const node = renderMaterialList([], "Rien ici");
    expect(node.tagName).toBe("P");
    expect(node.textContent).toBe("Rien ici");
  });

  it("rend une ligne par matériau avec quantité formatée", () => {
    const node = renderMaterialList([
      { name: "Mora", count: 12000, icon_url: "/media/mora.webp" },
      { name: "Slime", count: 3 },
    ]);
    const items = node.querySelectorAll(".material-list__item");
    expect(items).toHaveLength(2);
    expect(node.querySelector(".material-list__count").textContent).toBe("×12,000");
    // icône présente sur le premier seulement
    expect(items[0].querySelector("img")).not.toBeNull();
    expect(items[1].querySelector("img")).toBeNull();
  });
});

describe("renderMaterialCard / renderMaterialGrid", () => {
  it("affiche une image quand l'icône est résolue", () => {
    const card = renderMaterialCard({ name: "Mora", count: 100, icon_url: "/media/mora.webp" });
    const img = card.querySelector("img.material-card__img");
    expect(img).not.toBeNull();
    expect(img.getAttribute("src")).toBe("/media/mora.webp");
    expect(card.querySelector(".material-card__qty").textContent).toBe("x100");
  });

  it("affiche un fallback texte quand aucune icône n'est résolue", () => {
    const card = renderMaterialCard({ name: "Mystery Item", count: 1 });
    expect(card.querySelector("img")).toBeNull();
    expect(card.querySelector(".material-card__fallback").textContent).toBe("M");
  });

  it("remplace l'image par un fallback en cas d'erreur de chargement", () => {
    const card = renderMaterialCard({ name: "Sakura Bloom", count: 1, icon_url: "/media/x.webp" });
    const img = card.querySelector("img.material-card__img");
    img.dispatchEvent(new Event("error"));
    expect(card.querySelector("img")).toBeNull();
    expect(card.querySelector(".material-card__fallback").textContent).toBe("S");
  });

  it("affiche le libellé vide dans la grille sans matériaux", () => {
    const grid = renderMaterialGrid([], "Vide");
    expect(grid.querySelector(".muted").textContent).toBe("Vide");
  });

  it("affiche une carte par matériau dans la grille", () => {
    const grid = renderMaterialGrid([
      { name: "Mora", count: 1, icon_url: "/m.webp" },
      { name: "Slime", count: 2, icon_url: "/s.webp" },
    ]);
    expect(grid.querySelectorAll(".material-card")).toHaveLength(2);
  });
});

describe("renderLevelingBlock", () => {
  it("utilise les livres pour un personnage", () => {
    const node = renderLevelingBlock(
      {
        from_level: 1,
        to_level: 20,
        total_exp: 120000,
        mora_cost: 5000,
        book_count: 3,
        books: [{ name: "Wanderer's Advice", count: 3 }],
        remainder_exp: 250,
      },
      "character",
    );
    const title = node.querySelector(".leveling-block__title").textContent;
    expect(title).toContain("Level 1 → 20");
    expect(title).toContain("120,000 EXP");
    expect(title).toContain("5,000 Mora");
    expect(title).toContain("3 books");
    expect(node.querySelector(".leveling-block__items li").textContent).toBe("×3 Wanderer's Advice");
    expect(node.querySelector(".muted").textContent).toContain("250 EXP not covered");
  });

  it("utilise les minerais pour une arme", () => {
    const node = renderLevelingBlock(
      {
        from_level: 1,
        to_level: 20,
        total_exp: 50000,
        ore_count: 4,
        ores: [{ name: "Enhancement Ore", count: 4 }],
      },
      "weapon",
    );
    expect(node.querySelector(".leveling-block__title").textContent).toContain("4 ores");
    expect(node.querySelector("li").textContent).toBe("×4 Enhancement Ore");
  });
});

describe("renderAscensionPlanner", () => {
  const basePhase = {
    label: "1 → 20",
    mora: 1000,
    materials: [{ name: "Slime", count: 3, icon_url: "/s.webp" }],
    leveling: { from_level: 1, to_level: 20, total_exp: 1000, mora_cost: 500, book_count: 2, books: [] },
  };

  it("rend les phases et la section totaux", () => {
    const node = renderAscensionPlanner({
      phases: [basePhase],
      totals: [{ name: "Slime", count: 3 }],
      totalMora: 1000,
      variant: "character",
    });
    expect(node.querySelectorAll(".phase-card")).toHaveLength(1);
    expect(node.textContent).toContain("Ascension Mora: 1,000");
    expect(node.querySelector(".planner-section--totals")).not.toBeNull();
  });

  it("affiche les sections optionnelles (after last, EXP books, expToMax)", () => {
    const node = renderAscensionPlanner({
      phases: [basePhase],
      totals: [],
      totalMora: 2000,
      variant: "character",
      extra: {
        levelingAfterLast: { from_level: 80, to_level: 90, total_exp: 9000, ores: [] },
        levelingMoraTotal: 1500,
        expBooksTotal: [{ name: "Hero's Wit", count: 10, icon_url: "/h.webp" }],
        expToMax: { from_level: 1, to_level: 90, total_exp: 8000 },
      },
    });
    expect(node.textContent).toContain("After final ascension");
    expect(node.textContent).toContain("Leveling Mora: 1,500");
    expect(node.textContent).toContain("EXP books total");
    expect(node.textContent).toContain("Target level 90");
  });

  it("affiche les minerais totaux pour une arme", () => {
    const node = renderAscensionPlanner({
      phases: [basePhase],
      totals: [],
      totalMora: 500,
      variant: "weapon",
      extra: { enhancementOresTotal: [{ name: "Enhancement Ore", count: 8, icon_url: "/o.webp" }] },
    });
    expect(node.textContent).toContain("Enhancement ores total");
  });
});

describe("renderLevelPlanner", () => {
  const LEVELS = [1, 20, 40, 50, 60, 70, 80, 90];

  function dataFor(level) {
    if (level <= 1) return { materials: [], totalMora: 0 };
    return {
      materials: [{ name: "Slime", count: level, icon_url: "/s.webp" }],
      totalMora: level * 10,
      ascensionMora: level * 6,
      levelingMora: level * 4,
    };
  }

  it("peint la grille et la ligne de mora au niveau initial", () => {
    const node = renderLevelPlanner({ title: "Ascension", levels: LEVELS, initialLevel: 90, getDataForLevel: dataFor });
    document.body.appendChild(node);
    expect(node.querySelector(".planner-board__title").textContent).toBe("Ascension");
    expect(node.querySelector(".planner-board__subtitle").textContent).toBe("Level: 90");
    expect(node.querySelectorAll(".material-card")).toHaveLength(1);
    expect(node.querySelector(".planner-board__mora").textContent).toContain("900 Mora total");
  });

  it("repeint à 'aucun matériau' quand on descend au niveau 1", () => {
    const node = renderLevelPlanner({ title: "Ascension", levels: LEVELS, initialLevel: 90, getDataForLevel: dataFor });
    document.body.appendChild(node);

    const firstTick = node.querySelector(".level-slider__ticks > span");
    firstTick.click();

    expect(node.querySelector(".planner-board__subtitle").textContent).toBe("Level: 1");
    expect(node.querySelectorAll(".material-card")).toHaveLength(0);
    expect(node.querySelector(".material-grid .muted").textContent).toBe("No materials for this level.");
  });
});

describe("renderTalentPlanner", () => {
  const report = {
    talents: [
      {
        track: 1,
        levels: [
          { level: 2, mora: 100, materials: [{ name: "Slime", count: 6, icon_url: "/s.webp" }] },
          { level: 10, mora: 900, materials: [{ name: "Slime", count: 60, icon_url: "/s.webp" }] },
        ],
      },
      {
        track: 2,
        levels: [{ level: 2, mora: 150, materials: [{ name: "Bloom", count: 3, icon_url: "/b.webp" }] }],
      },
    ],
  };
  const LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  it("rend une section par piste plus le total", () => {
    const node = renderTalentPlanner({ report, levels: LEVELS, initialLevel: 10 });
    document.body.appendChild(node);
    // 2 pistes + 1 total
    expect(node.querySelectorAll(".talent-planner__track")).toHaveLength(3);
    expect(node.querySelector(".talent-planner__track-title").textContent).toBe("Normal Attack");
    expect(node.textContent).toContain("Elemental Skill");
  });

  it("recalcule les totaux quand on change le niveau d'une piste", () => {
    const node = renderTalentPlanner({ report, levels: LEVELS, initialLevel: 10 });
    document.body.appendChild(node);

    // piste 1 : descend au niveau 1 (premier tick) → plus de matériaux pour cette piste
    const firstTrackTicks = node.querySelectorAll(".talent-planner__track .level-slider__ticks > span");
    firstTrackTicks[0].click();

    const firstBadge = node.querySelector(".talent-planner__level-badge");
    expect(firstBadge.textContent).toBe("Lv. 1");
  });
});

describe("renderCharacterPage", () => {
  const data = {
    name: "Ayaka",
    title: "Frostflake Heron",
    element: "Cryo",
    weapon_type: "Sword",
    description: "desc",
    icon_url: "/media/icon.webp",
    splash_url: "/media/splash.webp",
  };

  it("rend nom, chips, avatar et splash", () => {
    const node = renderCharacterPage(
      { ...data, rarity: "5★" },
      [document.createElement("div")],
    );
    expect(node.querySelector(".character-page__name").textContent).toBe("Ayaka");
    expect(node.querySelectorAll(".character-page__chip")).toHaveLength(2);
    expect(node.querySelector(".character-page__chip")?.textContent).toBe("Cryo");
    expect(node.querySelector("img.character-page__chip-icon")?.getAttribute("src")).toContain("Cryo.webp");
    expect(node.querySelector("img.character-page__avatar.rarity-frame--gold")).not.toBeNull();
    expect(node.querySelector(".character-splash__img")).not.toBeNull();
  });

  it("omet titre/description/chips/avatar quand absents", () => {
    const node = renderCharacterPage({ name: "Anon" }, []);
    expect(node.querySelector(".character-page__title")).toBeNull();
    expect(node.querySelector(".character-page__desc")).toBeNull();
    expect(node.querySelector(".character-page__chips")).toBeNull();
    expect(node.querySelector("img.character-page__avatar")).toBeNull();
    expect(node.querySelector(".character-splash")).toBeNull();
  });

  it("retombe sur l'icône comme splash quand splash_url manque", () => {
    const node = renderCharacterPage({ name: "X", icon_url: "/i.webp" }, []);
    const splash = node.querySelector(".character-splash__img");
    expect(splash).not.toBeNull();
    expect(splash.classList.contains("character-splash__img--fallback")).toBe(true);
  });
});

describe("renderWeaponPage", () => {
  it("rend nom, chips et avatar", () => {
    const node = renderWeaponPage(
      { name: "Mistsplitter", weapon_type: "Sword", rarity: "5★", description: "d", icon_url: "/w.webp" },
      [],
    );
    expect(node.querySelector(".weapon-page__name").textContent).toBe("Mistsplitter");
    expect(node.querySelectorAll(".weapon-page__chip")).toHaveLength(2);
    expect(node.querySelector("img.weapon-page__avatar.rarity-frame--gold")).not.toBeNull();
    expect(node.querySelector(".weapon-page__chip.rarity-frame--gold")?.textContent).toBe("5★");
    expect(node.querySelector("img.weapon-page__chip-icon")?.getAttribute("src")).toContain("Skill_A_01.webp");
  });
});

describe("plannerHero", () => {
  it("rend l'en-tête avec lien de retour", () => {
    const node = renderPlannerHeader({ name: "Ayaka", backHref: "/characters", backLabel: "← Back" });
    expect(node.querySelector("h1").textContent).toBe("Ayaka");
    const back = node.querySelector("a.planner-header__back");
    expect(back.getAttribute("href")).toBe("/characters");
  });

  it("renvoie null pour le backdrop sans source", () => {
    expect(renderPlannerSplashBackdrop({})).toBeNull();
  });

  it("rend le backdrop avec une source", () => {
    const node = renderPlannerSplashBackdrop({ splashUrl: "/splash.webp" });
    expect(node.querySelector("img").getAttribute("src")).toBe("/splash.webp");
  });
});
