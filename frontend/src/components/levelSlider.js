import { el } from "../utils.js";
import { nearestMilestone } from "../utils/plannerAggregate.js";

function indexForLevel(levels, value) {
  const snapped = nearestMilestone(levels, value);
  const idx = levels.indexOf(snapped);
  return idx >= 0 ? idx : 0;
}

function fillPercent(index, count) {
  if (count <= 1) return 100;
  return (index / (count - 1)) * 100;
}

/**
 * Slider à paliers discrets : une position = une valeur (curseur aligné aux ticks).
 * @param {number[]} levels — paliers (ex. [1,20,40,…] ou [1,2,…,10])
 * @param {number} initialValue
 * @param {(level: number) => void} onChange
 * @param {{ compact?: boolean, label?: string }} [opts]
 */
export function renderLevelSlider(levels, initialValue, onChange, opts = {}) {
  const { compact = false, label = "Level" } = opts;
  const count = levels.length;
  const maxIndex = Math.max(0, count - 1);

  let currentIndex = indexForLevel(levels, initialValue);
  const badge = el("span", { className: "level-slider__badge", text: String(levels[currentIndex]) });

  const tickEls = levels.map((lv, i) => {
    const span = el("span", { text: String(lv), role: "button", tabIndex: 0 });
    span.classList.toggle("active", i === currentIndex);
    span.addEventListener("click", () => applyIndex(i));
    span.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        applyIndex(i);
      }
    });
    return span;
  });

  const input = el("input", {
    type: "range",
    className: "level-slider__input",
    min: "0",
    max: String(maxIndex),
    step: "1",
    value: String(currentIndex),
    "aria-valuemin": String(levels[0]),
    "aria-valuemax": String(levels[maxIndex]),
    "aria-valuenow": String(levels[currentIndex]),
    onInput: (e) => applyIndex(Number(e.target.value)),
  });

  function applyIndex(index) {
    const clamped = Math.min(maxIndex, Math.max(0, index));
    currentIndex = clamped;
    const value = levels[clamped];
    input.value = String(clamped);
    input.setAttribute("aria-valuenow", String(value));
    input.style.setProperty("--pct", `${fillPercent(clamped, count)}%`);
    badge.textContent = String(value);
    tickEls.forEach((node, i) => node.classList.toggle("active", i === clamped));
    onChange(value);
  }

  applyIndex(currentIndex);

  const ticks = el("div", {
    className: "level-slider__ticks",
    style: `--tick-count: ${count}`,
  }, tickEls);

  return el("aside", { className: `level-slider${compact ? " level-slider--compact" : ""}` }, [
    el("div", { className: "level-slider__head" }, [el("h3", { text: label }), badge]),
    input,
    ticks,
  ]);
}
