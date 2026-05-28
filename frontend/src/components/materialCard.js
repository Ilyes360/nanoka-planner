import { el, formatNumber } from "../utils.js";
import { resolveMaterialIcon } from "../utils/materialIcon.js";
import { materialRarityClass } from "../utils/materialRarity.js";

export function renderMaterialCard(mat) {
  const src = resolveMaterialIcon(mat);
  const icon = src
    ? el("img", {
        className: "material-card__img",
        src,
        alt: mat.name,
        loading: "lazy",
        onError: (e) => {
          e.target.replaceWith(el("span", { className: "material-card__fallback", text: mat.name.charAt(0) }));
        },
      })
    : el("span", { className: "material-card__fallback", text: mat.name.charAt(0) });

  return el(
    "div",
    { className: `material-card ${materialRarityClass(mat.name)}`, title: mat.name },
    [
      el("div", { className: "material-card__icon-wrap" }, [icon]),
      el("span", { className: "material-card__qty", text: `x${formatNumber(mat.count)}` }),
    ],
  );
}

export function renderMaterialGrid(materials, emptyLabel = "No materials for this level.") {
  const grid = el("div", { className: "material-grid" });
  if (!materials?.length) {
    grid.append(el("p", { className: "muted", text: emptyLabel }));
  } else {
    grid.append(...materials.map(renderMaterialCard));
  }
  return grid;
}
