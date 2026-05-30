/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";
import { renderHome } from "../src/views/home.js";

describe("renderHome", () => {
  it("rend le héros et la carte du jeu avec les liens de navigation", () => {
    const node = renderHome();

    expect(node.querySelector(".home-hero__title").textContent).toBe("Nanoka Planner");
    expect(node.querySelector(".home-game--genshin")).not.toBeNull();

    const links = [...node.querySelectorAll("a[data-link]")].map((a) => a.getAttribute("href"));
    expect(links).toContain("/characters");
    expect(links).toContain("/weapons");
  });
});
