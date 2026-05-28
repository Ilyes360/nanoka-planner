import { describe, expect, it } from "vitest";
import { resolveMaterialIcon } from "../src/utils/materialIcon.js";

describe("resolveMaterialIcon", () => {
  it("prefers API icon_url", () => {
    expect(resolveMaterialIcon({ name: "Mora", icon_url: "/media/items/mora.webp" })).toBe("/media/items/mora.webp");
  });

  it("builds static URL from item_id", () => {
    expect(resolveMaterialIcon({ name: "Unknown", item_id: 202 })).toBe(
      "https://static.nanoka.cc/assets/gi/UI_ItemIcon_202.webp",
    );
  });

  it("resolves known EXP book names", () => {
    expect(resolveMaterialIcon({ name: "Hero's Wit" })).toBe(
      "https://static.nanoka.cc/assets/gi/UI_ItemIcon_104003.webp",
    );
  });

  it("returns empty string when no icon can be resolved", () => {
    expect(resolveMaterialIcon({ name: "Mystery Item" })).toBe("");
  });
});
