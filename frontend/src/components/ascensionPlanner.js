import { el, formatNumber } from "../utils.js";
import { renderLevelingBlock } from "./levelingBlock.js";
import { renderMaterialList } from "./materialList.js";

export function renderAscensionPlanner({ phases, totals, totalMora, variant, extra = {} }) {
  const sections = [
    el("section", { className: "planner-section" }, [
      el("h2", { text: "By ascension phase" }),
      el(
        "div",
        { className: "phase-list" },
        phases.map((phase) =>
          el("article", { className: "phase-card" }, [
            el("header", { className: "phase-card__header" }, [
              el("h3", { text: phase.label }),
              el("span", { className: "badge", text: `${formatNumber(phase.mora)} Mora` }),
            ]),
            phase.leveling ? renderLevelingBlock(phase.leveling, variant) : null,
            renderMaterialList(phase.materials, "No ascension materials"),
          ]),
        ),
      ),
    ]),
  ];

  if (extra.levelingAfterLast) {
    sections.push(
      el("section", { className: "planner-section" }, [
        el("h2", { text: "After final ascension" }),
        el("article", { className: "phase-card" }, [renderLevelingBlock(extra.levelingAfterLast, "weapon")]),
      ]),
    );
  }

  const totalsChildren = [
    el("h2", { text: "Totals" }),
    el("p", { className: "totals-line", text: `Ascension Mora: ${formatNumber(totalMora)}` }),
  ];

  if (extra.levelingMoraTotal != null) {
    totalsChildren.push(
      el("p", {
        className: "totals-line",
        text: `Leveling Mora: ${formatNumber(extra.levelingMoraTotal)}`,
      }),
    );
  }
  if (variant === "character" && extra.expBooksTotal?.length) {
    totalsChildren.push(el("h3", { text: "EXP books total" }), renderMaterialList(extra.expBooksTotal));
  }
  if (variant === "weapon" && extra.enhancementOresTotal?.length) {
    totalsChildren.push(el("h3", { text: "Enhancement ores total" }), renderMaterialList(extra.enhancementOresTotal));
  }
  totalsChildren.push(el("h3", { text: "Ascension materials" }), renderMaterialList(totals));

  if (extra.expToMax) {
    totalsChildren.push(
      el("div", { className: "exp-max" }, [
        el("h3", { text: `Target level ${extra.expToMax.to_level}` }),
        renderLevelingBlock(extra.expToMax, variant),
      ]),
    );
  }

  sections.push(el("section", { className: "planner-section planner-section--totals" }, totalsChildren));

  return el("div", { className: "planner" }, sections);
}
