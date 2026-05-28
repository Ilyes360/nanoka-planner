import { describe, expect, it } from "vitest";
import { filterByName, formatNumber } from "../src/utils.js";

describe("formatNumber", () => {
  it("formats with en-US grouping", () => {
    expect(formatNumber(1234567)).toBe("1,234,567");
  });
});

describe("filterByName", () => {
  const items = [{ name: "Hu Tao" }, { name: "Zhongli" }, { name: "Aino" }];

  it("returns all items when query is empty", () => {
    expect(filterByName(items, "")).toEqual(items);
    expect(filterByName(items, "   ")).toEqual(items);
  });

  it("filters case-insensitively", () => {
    expect(filterByName(items, "hu")).toEqual([{ name: "Hu Tao" }]);
    expect(filterByName(items, "TAO")).toEqual([{ name: "Hu Tao" }]);
  });
});
