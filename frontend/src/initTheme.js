import { el } from "./utils.js";
import { getTheme, setTheme, THEMES } from "./utils/theme.js";

function syncSwatches(picker, activeId) {
  for (const btn of picker.querySelectorAll(".theme-picker__swatch")) {
    const pressed = btn.dataset.theme === activeId;
    btn.setAttribute("aria-pressed", pressed ? "true" : "false");
  }
}

export function initThemePicker() {
  const mount = document.getElementById("theme-picker");
  if (!mount) return;

  const current = getTheme();
  const picker = el("div", {
    className: "theme-picker",
    role: "group",
    "aria-label": "Background",
  }, [
    el("span", { className: "theme-picker__label", text: "Background" }),
  ]);

  for (const theme of THEMES) {
    picker.append(el("button", {
      type: "button",
      className: "theme-picker__swatch",
      "data-theme": theme.id,
      "aria-label": theme.label,
      "aria-pressed": theme.id === current ? "true" : "false",
      title: theme.label,
      style: `--swatch-bg: ${theme.swatch}`,
      onClick: () => {
        setTheme(theme.id);
        syncSwatches(picker, theme.id);
      },
    }));
  }

  mount.replaceChildren(picker);
}
