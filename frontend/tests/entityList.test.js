/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/apiClient.js", () => ({
  apiClient: { characters: vi.fn(), character: vi.fn() },
}));

import { apiClient } from "../src/apiClient.js";
import { charactersList } from "../src/views/entityList.js";

const LIST = [
  { id: "1", name: "Albedo", element: "Geo", weapon_type: "Sword", rarity: "5★" },
  { id: "2", name: "Bennett", element: "Pyro", weapon_type: "Sword", rarity: "4★" },
];

describe("entityList dynamic search", () => {
  let app;

  beforeEach(() => {
    document.body.innerHTML = '<main id="app"></main>';
    app = document.getElementById("app");
    apiClient.characters.mockResolvedValue(LIST);
  });

  it("rend cards and keeps search mounted on filter", async () => {
    await charactersList(app);

    const grid = app.querySelector(".entity-grid");
    const count = app.querySelector(".list-count");
    expect(grid?.children.length).toBe(2);
    expect(count?.textContent).toBe("2 / 2");

    const search = app.querySelector("input.search");
    search.value = "ben";
    search.dispatchEvent(new Event("input", { bubbles: true }));

    expect(app.querySelector(".entity-grid")?.children.length).toBe(1);
    expect(app.querySelector("input.search")).toBe(search);
    expect(count?.textContent).toBe("1 / 2");
  });
});
