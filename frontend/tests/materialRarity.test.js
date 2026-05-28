import { describe, expect, it } from "vitest";
import { materialRarityClass } from "../src/utils/materialRarity.js";

describe("materialRarityClass", () => {
  it("marks Mora as gold", () => {
    expect(materialRarityClass("Mora")).toBe("material-card--gold");
  });

  it("marks gems as gold", () => {
    expect(materialRarityClass("Vayuda Turquoise Gemstone")).toBe("material-card--gold");
  });

  it("marks EXP books and ores as purple", () => {
    expect(materialRarityClass("Hero's Wit")).toBe("material-card--purple");
    expect(materialRarityClass("Mystic Enhancement Ore")).toBe("material-card--purple");
  });

  it("marks fragments as teal", () => {
    expect(materialRarityClass("Mask of the Wicked Lieutenant's Fragment")).toBe("material-card--teal");
  });

  it("defaults to blue", () => {
    expect(materialRarityClass("Local Specialty")).toBe("material-card--blue");
  });
});
