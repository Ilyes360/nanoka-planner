import { el, formatNumber } from "../utils.js";

export function renderLevelingBlock(block, variant) {
  const items = variant === "character" ? block.books : block.ores;
  const itemLabel = variant === "character" ? "books" : "ores";
  const itemCount = variant === "character" ? block.book_count : block.ore_count;

  const children = [
    el("p", {
      className: "leveling-block__title",
      text: `Level ${block.from_level} → ${block.to_level} · ${formatNumber(block.total_exp)} EXP${
        block.mora_cost != null ? ` · ${formatNumber(block.mora_cost)} Mora (XP)` : ""
      }${itemCount != null ? ` · ${itemCount} ${itemLabel}` : ""}`,
    }),
  ];

  if (items?.length) {
    children.push(
      el(
        "ul",
        { className: "leveling-block__items" },
        items.map((item) => el("li", { text: `×${formatNumber(item.count)} ${item.name}` })),
      ),
    );
  }
  if (block.remainder_exp) {
    children.push(el("p", { className: "muted", text: `${formatNumber(block.remainder_exp)} EXP not covered` }));
  }

  return el("div", { className: "leveling-block" }, children);
}
