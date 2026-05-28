import { describe, expect, it } from "vitest";
import {
  aggregateAscensionReport,
  aggregateTalentReportDetailed,
  aggregateTalentReportWithLevels,
  mergeMaterialMaps,
  nearestMilestone,
} from "../src/utils/plannerAggregate.js";

const sampleAscension = {
  ascensions: [
    {
      at_level: 20,
      mora: 1000,
      materials: [{ name: "Slime Condensate", count: 3, item_id: "112002" }],
      leveling: {
        to_level: 20,
        mora_cost: 500,
        books: [{ name: "Wanderer's Advice", count: 2, item_id: 104001 }],
      },
    },
    {
      at_level: 40,
      mora: 2000,
      materials: [{ name: "Slime Condensate", count: 6, item_id: "112002" }],
      leveling: {
        to_level: 40,
        mora_cost: 800,
        books: [{ name: "Adventurer's Experience", count: 1, item_id: 104002 }],
      },
    },
  ],
};

describe("aggregateAscensionReport", () => {
  it("includes only phases up to the target level", () => {
    const at20 = aggregateAscensionReport(sampleAscension, 20, "character");
    expect(at20.ascensionMora).toBe(1000);
    expect(at20.levelingMora).toBe(500);
    expect(at20.materials).toHaveLength(2);
    expect(at20.materials.find((m) => m.name === "Slime Condensate").count).toBe(3);

    const at40 = aggregateAscensionReport(sampleAscension, 40, "character");
    expect(at40.ascensionMora).toBe(3000);
    expect(at40.materials.find((m) => m.name === "Slime Condensate").count).toBe(9);
  });

  it("uses ores for weapons", () => {
    const weaponAsc = {
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
    };
    const result = aggregateAscensionReport(weaponAsc, 20, "weapon");
    expect(result.materials).toEqual([{ name: "Enhancement Ore", count: 4, item_id: 104011, icon_url: "" }]);
  });
});

describe("aggregateTalentReportWithLevels", () => {
  const report = {
    talents: [
      {
        track: 1,
        levels: [
          { level: 2, mora: 100, materials: [{ name: "Slime Condensate", count: 6 }] },
          { level: 3, mora: 200, materials: [{ name: "Slime Condensate", count: 12 }] },
        ],
      },
      {
        track: 2,
        levels: [{ level: 2, mora: 150, materials: [{ name: "Treasure Hoarder", count: 3 }] }],
      },
    ],
  };

  it("returns no materials at talent level 1", () => {
    const { tracks, total } = aggregateTalentReportWithLevels(report, { 1: 1, 2: 1 });
    expect(tracks.every((t) => t.materials.length === 0)).toBe(true);
    expect(total.totalMora).toBe(0);
  });

  it("aggregates per-track levels independently", () => {
    const { tracks, total } = aggregateTalentReportWithLevels(report, { 1: 3, 2: 2 });
    const t1 = tracks.find((t) => t.track === 1);
    const t2 = tracks.find((t) => t.track === 2);
    expect(t1.totalMora).toBe(300);
    expect(t1.materials[0].count).toBe(18);
    expect(t2.totalMora).toBe(150);
    expect(total.totalMora).toBe(450);
  });

  it("supports Map for levelsByTrack", () => {
    const levels = new Map([[1, 2], [2, 2]]);
    const { total } = aggregateTalentReportWithLevels(report, levels);
    expect(total.totalMora).toBe(250);
  });
});

describe("aggregateTalentReportDetailed", () => {
  it("applies the same level to every track", () => {
    const report = {
      talents: [{ track: 1, levels: [{ level: 2, mora: 50, materials: [] }] }],
    };
    const { total } = aggregateTalentReportDetailed(report, 2);
    expect(total.totalMora).toBe(50);
  });
});

describe("mergeMaterialMaps", () => {
  it("merges counts for the same material key", () => {
    const a = new Map([["Slime|112002", { name: "Slime", count: 3, item_id: "112002", icon_url: "" }]]);
    const b = new Map([["Slime|112002", { name: "Slime", count: 5, item_id: "112002", icon_url: "" }]]);
    expect(mergeMaterialMaps([a, b])).toEqual([{ name: "Slime", count: 8, item_id: "112002", icon_url: "" }]);
  });
});

describe("nearestMilestone", () => {
  it("snaps to the closest defined level", () => {
    const levels = [1, 20, 40, 50, 60, 70, 80, 90];
    expect(nearestMilestone(levels, 38)).toBe(40);
    expect(nearestMilestone(levels, 39)).toBe(40);
    expect(nearestMilestone(levels, 1)).toBe(1);
  });
});
