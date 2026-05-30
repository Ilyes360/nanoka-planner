import { describe, expect, it } from "vitest";
import { elementIconUrl } from "../src/utils/elementIcon.js";

describe("elementIconUrl", () => {
  it("retourne l'icone elementaire Nanoka pour chaque element", () => {
    expect(elementIconUrl("Pyro")).toBe("https://static.nanoka.cc/assets/gi/Pyro.webp");
    expect(elementIconUrl("Hydro")).toBe("https://static.nanoka.cc/assets/gi/Hydro.webp");
    expect(elementIconUrl("Electro")).toBe("https://static.nanoka.cc/assets/gi/Electro.webp");
    expect(elementIconUrl("Cryo")).toBe("https://static.nanoka.cc/assets/gi/Cryo.webp");
    expect(elementIconUrl("Anemo")).toBe("https://static.nanoka.cc/assets/gi/Anemo.webp");
    expect(elementIconUrl("Geo")).toBe("https://static.nanoka.cc/assets/gi/Geo.webp");
    expect(elementIconUrl("Dendro")).toBe("https://static.nanoka.cc/assets/gi/Dendro.webp");
  });

  it("retourne une chaine vide pour un element inconnu", () => {
    expect(elementIconUrl("Unknown")).toBe("");
    expect(elementIconUrl("")).toBe("");
  });
});
