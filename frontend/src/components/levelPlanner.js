import { el, formatNumber } from "../utils.js";
import { renderMaterialCard } from "./materialCard.js";
import { renderLevelSlider } from "./levelSlider.js";
import { nearestMilestone } from "../utils/plannerAggregate.js";

/**
 * @param {object} opts
 * @param {string} opts.title
 * @param {number[]} opts.levels
 * @param {number} opts.initialLevel
 * @param {(level: number) => { materials: object[], totalMora?: number, ascensionMora?: number, levelingMora?: number }} opts.getDataForLevel
 */
export function renderLevelPlanner({ title, levels, initialLevel, getDataForLevel }) {
  let currentLevel = nearestMilestone(levels, initialLevel);
  const gridMount = el("div", { className: "material-grid" });
  const subtitle = el("p", { className: "planner-board__subtitle", text: `Level: ${currentLevel}` });
  const moraLine = el("p", { className: "planner-board__mora muted" });

  function paint() {
    const data = getDataForLevel(currentLevel);
    subtitle.textContent = `Level: ${currentLevel}`;
    gridMount.replaceChildren();
    if (!data.materials.length) {
      gridMount.append(el("p", { className: "muted", text: "No materials for this level." }));
    } else {
      gridMount.append(...data.materials.map(renderMaterialCard));
    }
    const parts = [];
    if (data.totalMora != null) parts.push(`${formatNumber(data.totalMora)} Mora total`);
    if (data.ascensionMora) parts.push(`${formatNumber(data.ascensionMora)} ascension`);
    if (data.levelingMora) parts.push(`${formatNumber(data.levelingMora)} leveling / talents`);
    moraLine.textContent = parts.length ? parts.join(" · ") : "";
  }

  const slider = renderLevelSlider(levels, currentLevel, (lv) => {
    currentLevel = lv;
    paint();
  }, { label: "Level" });

  const board = el("section", { className: "planner-board" }, [
    el("header", { className: "planner-board__header" }, [
      el("h2", { className: "planner-board__title", text: title }),
      subtitle,
      moraLine,
    ]),
    el("div", { className: "planner-board__body" }, [
      el("div", { className: "planner-board__grid-wrap" }, [gridMount]),
      slider,
    ]),
  ]);

  paint();
  return el("div", { className: "level-planner" }, [board]);
}
