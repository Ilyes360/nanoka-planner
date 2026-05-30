import { el } from "../utils.js";
import { weaponTypeIconUrl } from "../utils/weaponTypeIcon.js";

/**
 * Puce de profil (personnage / arme) avec icone optionnelle.
 * @param {string} baseClass — ex. character-page__chip
 */
export function renderProfileChip(text, { baseClass, themeClass = "", iconUrl = "" } = {}) {
  if (!text) return null;
  const className = [baseClass, themeClass].filter(Boolean).join(" ");
  const children = [];
  if (iconUrl) {
    children.push(el("img", {
      className: `${baseClass}-icon`,
      src: iconUrl,
      alt: "",
      loading: "lazy",
    }));
  }
  children.push(document.createTextNode(text));
  return el("span", { className }, children);
}

export function renderWeaponTypeChip(text, baseClass) {
  return renderProfileChip(text, { baseClass, iconUrl: weaponTypeIconUrl(text) });
}
