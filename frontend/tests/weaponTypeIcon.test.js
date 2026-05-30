import { describe, expect, it } from "vitest";
import { weaponTypeIconUrl } from "../src/utils/weaponTypeIcon.js";

describe("weaponTypeIconUrl", () => {
  it("retourne l'icone d'attaque normale pour chaque type d'arme", () => {
    expect(weaponTypeIconUrl("Sword")).toBe("https://static.nanoka.cc/assets/gi/Skill_A_01.webp");
    expect(weaponTypeIconUrl("Bow")).toBe("https://static.nanoka.cc/assets/gi/Skill_A_02.webp");
    expect(weaponTypeIconUrl("Polearm")).toBe("https://static.nanoka.cc/assets/gi/Skill_A_03.webp");
    expect(weaponTypeIconUrl("Claymore")).toBe("https://static.nanoka.cc/assets/gi/Skill_A_04.webp");
    expect(weaponTypeIconUrl("Catalyst")).toBe("https://static.nanoka.cc/assets/gi/Skill_A_Catalyst_MD.webp");
  });

  it("retourne une chaine vide pour un type inconnu", () => {
    expect(weaponTypeIconUrl("Spear")).toBe("");
    expect(weaponTypeIconUrl("")).toBe("");
  });
});
