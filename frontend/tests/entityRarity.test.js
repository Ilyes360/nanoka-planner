import { describe, expect, it } from "vitest";
import {
  entityIconRarityClass,
  filterChipThemeClass,
  plannerAvatarClass,
  rarityFrameClass,
} from "../src/utils/entityRarity.js";

describe("rarityFrameClass", () => {
  it("mappe chaque rareté vers le modificateur de cadre", () => {
    expect(rarityFrameClass("5★")).toBe("rarity-frame--gold");
    expect(rarityFrameClass("4★")).toBe("rarity-frame--purple");
    expect(rarityFrameClass("3★")).toBe("rarity-frame--blue");
    expect(rarityFrameClass("2★")).toBe("rarity-frame--green");
    expect(rarityFrameClass("1★")).toBe("rarity-frame--gray");
  });

  it("retourne une chaîne vide si la rareté est absente", () => {
    expect(rarityFrameClass("")).toBe("");
    expect(rarityFrameClass(undefined)).toBe("");
  });
});

describe("entityIconRarityClass", () => {
  it("combine la classe de base et le modificateur de rareté", () => {
    expect(entityIconRarityClass("5★")).toBe("entity-card__icon rarity-frame--gold");
    expect(entityIconRarityClass("")).toBe("entity-card__icon");
  });
});

describe("plannerAvatarClass", () => {
  it("applique le cadre de rareté sur l'avatar planificateur", () => {
    expect(plannerAvatarClass("character-page__avatar", "4★")).toBe(
      "character-page__avatar rarity-frame--purple",
    );
    expect(plannerAvatarClass("weapon-page__avatar", "5★")).toBe(
      "weapon-page__avatar rarity-frame--gold",
    );
  });
});

describe("filterChipThemeClass", () => {
  it("colore uniquement les puces de rarete", () => {
    expect(filterChipThemeClass("rarity", "5★")).toBe("rarity-frame--gold");
    expect(filterChipThemeClass("element", "Cryo")).toBe("");
    expect(filterChipThemeClass("weapon_type", "Sword")).toBe("");
  });
});
