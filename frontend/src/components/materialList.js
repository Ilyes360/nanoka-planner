import { el, formatNumber } from "../utils.js";

export function renderMaterialList(materials, emptyLabel = "No materials") {
  if (!materials?.length) {
    return el("p", { className: "muted", text: emptyLabel });
  }
  return el(
    "ul",
    { className: "material-list" },
    materials.map((m) =>
      el("li", { className: "material-list__item" }, [
        m.icon_url ? el("img", { src: m.icon_url, alt: "", className: "material-list__icon" }) : null,
        el("span", { className: "material-list__name", text: m.name }),
        el("span", { className: "material-list__count", text: `×${formatNumber(m.count)}` }),
      ]),
    ),
  );
}
