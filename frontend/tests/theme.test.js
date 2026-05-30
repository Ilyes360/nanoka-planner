/**
 * @vitest-environment jsdom
 */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  DEFAULT_THEME,
  STORAGE_KEY,
  applyTheme,
  getTheme,
  initThemeOnLoad,
  setTheme,
} from "../src/utils/theme.js";

beforeEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
});

afterEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
});

describe("background theme", () => {
  it("retourne le fond par defaut si rien n'est stocke", () => {
    expect(getTheme()).toBe(DEFAULT_THEME);
  });

  it("persiste et applique un fond valide", () => {
    setTheme("ocean");
    expect(localStorage.getItem(STORAGE_KEY)).toBe("ocean");
    expect(document.documentElement.dataset.theme).toBe("ocean");
    expect(getTheme()).toBe("ocean");
  });

  it("ignore un fond inconnu lors de l'application", () => {
    expect(applyTheme("cyan")).toBe(DEFAULT_THEME);
    expect(document.documentElement.dataset.theme).toBe(DEFAULT_THEME);
  });

  it("initialise le fond stocke au chargement", () => {
    localStorage.setItem(STORAGE_KEY, "forest");
    expect(initThemeOnLoad()).toBe("forest");
    expect(document.documentElement.dataset.theme).toBe("forest");
  });
});
