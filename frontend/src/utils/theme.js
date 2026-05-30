export const STORAGE_KEY = "nanoka-background";
export const DEFAULT_THEME = "default";

/** @deprecated ancienne clé accent — ignorée si la nouvelle est absente */
const LEGACY_STORAGE_KEY = "nanoka-theme";

export const THEMES = [
  { id: "default", label: "Default", swatch: "#0b0620" },
  { id: "ocean", label: "Ocean", swatch: "#071820" },
  { id: "forest", label: "Forest", swatch: "#081810" },
  { id: "ember", label: "Ember", swatch: "#140c08" },
  { id: "slate", label: "Slate", swatch: "#0e1218" },
  { id: "wine", label: "Wine", swatch: "#120818" },
  { id: "abyss", label: "Abyss", swatch: "#060c14" },
];

const VALID_IDS = new Set(THEMES.map((theme) => theme.id));

export function isValidTheme(id) {
  return VALID_IDS.has(id);
}

function readStoredTheme() {
  try {
    const current = localStorage.getItem(STORAGE_KEY);
    if (current && isValidTheme(current)) return current;
    /* Anciens thèmes accent → retour au défaut */
    if (localStorage.getItem(LEGACY_STORAGE_KEY)) return DEFAULT_THEME;
  } catch {
    /* localStorage indisponible */
  }
  return DEFAULT_THEME;
}

export function getTheme() {
  return readStoredTheme();
}

export function applyTheme(id) {
  const theme = isValidTheme(id) ? id : DEFAULT_THEME;
  document.documentElement.dataset.theme = theme;
  return theme;
}

export function setTheme(id) {
  if (!isValidTheme(id)) return DEFAULT_THEME;
  try {
    localStorage.setItem(STORAGE_KEY, id);
    localStorage.removeItem(LEGACY_STORAGE_KEY);
  } catch {
    /* ignore */
  }
  return applyTheme(id);
}

export function initThemeOnLoad() {
  return applyTheme(getTheme());
}
