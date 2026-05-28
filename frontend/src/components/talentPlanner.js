import { el, formatNumber } from "../utils.js";
import { aggregateTalentReportWithLevels, nearestMilestone } from "../utils/plannerAggregate.js";
import { renderMaterialGrid } from "./materialCard.js";
import { renderLevelSlider } from "./levelSlider.js";

const TALENT_LABELS = {
  1: "Normal Attack",
  2: "Elemental Skill",
  3: "Elemental Burst",
};

function talentTrackLabel(trackNum) {
  return TALENT_LABELS[trackNum] || `Talent ${trackNum}`;
}

function formatLevelsSummary(levelsByTrack, report) {
  const parts = (report.talents || []).map((track) => {
    const n = Number(track.track) || 0;
    return levelsByTrack.get(n) ?? "—";
  });
  return parts.join(" / ");
}

/**
 * @param {object} opts
 * @param {object} opts.report — API talent report (`data.talents`)
 * @param {number[]} opts.levels
 * @param {number} opts.initialLevel — initial level for each track
 */
export function renderTalentPlanner({ report, levels, initialLevel }) {
  const startLevel = nearestMilestone(levels, initialLevel);
  const levelsByTrack = new Map();

  for (const track of report.talents || []) {
    const trackNum = Number(track.track) || 0;
    levelsByTrack.set(trackNum, startLevel);
  }

  const subtitle = el("p", {
    className: "planner-board__subtitle",
    text: "Pick a target level for each talent.",
  });
  const moraLine = el("p", { className: "planner-board__mora muted" });

  const totalMoraEl = el("span", { className: "talent-planner__track-mora muted" });
  const totalGridMount = el("div", { className: "talent-planner__grid-wrap" });

  const trackPanels = [];

  function refresh() {
    const { tracks, total } = aggregateTalentReportWithLevels(report, levelsByTrack);

    subtitle.textContent = `Levels: ${formatLevelsSummary(levelsByTrack, report)}`;
    moraLine.textContent = `${formatNumber(total.totalMora)} Mora · all talents combined`;

    for (const panel of trackPanels) {
      const data = tracks.find((t) => t.track === panel.trackNum);
      if (!data) continue;
      const lv = levelsByTrack.get(panel.trackNum);
      panel.levelBadge.textContent = `Lv. ${lv}`;
      panel.moraEl.textContent = `${formatNumber(data.totalMora)} Mora`;
      const emptyLabel =
        lv <= 1 ? "Base level — no materials required." : "No materials for this level.";
      panel.gridMount.replaceChildren(renderMaterialGrid(data.materials, emptyLabel));
    }

    totalMoraEl.textContent = `${formatNumber(total.totalMora)} Mora`;
    totalGridMount.replaceChildren(renderMaterialGrid(total.materials, "No materials accumulated."));
  }

  const trackSections = (report.talents || []).map((track) => {
    const trackNum = Number(track.track) || 0;
    const gridMount = el("div", { className: "talent-planner__grid-wrap" });
    const moraEl = el("span", { className: "talent-planner__track-mora muted" });
    const levelBadge = el("span", { className: "talent-planner__level-badge", text: `Lv. ${startLevel}` });

    const slider = renderLevelSlider(
      levels,
      levelsByTrack.get(trackNum),
      (lv) => {
        levelsByTrack.set(trackNum, lv);
        refresh();
      },
      { compact: true, label: "Level" },
    );

    trackPanels.push({ trackNum, gridMount, moraEl, levelBadge });

    return el("section", { className: "talent-planner__track" }, [
      el("header", { className: "talent-planner__track-head" }, [
        el("h3", { className: "talent-planner__track-title", text: talentTrackLabel(trackNum) }),
        el("div", { className: "talent-planner__track-meta" }, [levelBadge, moraEl]),
      ]),
      el("div", { className: "talent-planner__track-body" }, [gridMount, slider]),
    ]);
  });

  const totalSection = el("section", { className: "talent-planner__track talent-planner__track--total" }, [
    el("header", { className: "talent-planner__track-head" }, [
      el("h3", { className: "talent-planner__track-title", text: "Total" }),
      totalMoraEl,
    ]),
    totalGridMount,
  ]);

  const board = el("section", { className: "planner-board talent-planner" }, [
    el("header", { className: "planner-board__header" }, [
      el("h2", { className: "planner-board__title", text: "Talent materials" }),
      subtitle,
      moraLine,
    ]),
    el("div", { className: "talent-planner__sections" }, [...trackSections, totalSection]),
  ]);

  refresh();
  return el("div", { className: "level-planner" }, [board]);
}
