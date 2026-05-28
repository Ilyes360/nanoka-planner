import { el } from "../utils.js";

/** En-tête compact (titre + retour), sans illustration. */
export function renderPlannerHeader({ name, backHref, backLabel, tabs = null }) {
  const inner = [
    el("a", { href: backHref, className: "back-link planner-header__back", "data-link": "", text: backLabel }),
    el("h1", { className: "planner-header__name", text: name }),
  ];
  if (tabs) inner.push(tabs);
  return el("header", { className: "planner-header" }, inner);
}

/**
 * Illustration centrée en arrière-plan, semi-transparente.
 * Le planificateur passe par-dessus.
 */
export function renderPlannerSplashBackdrop({ splashUrl, iconUrl }) {
  const src = splashUrl || iconUrl;
  if (!src) return null;

  const img = el("img", {
    className: `planner-splash-backdrop__img${splashUrl ? "" : " planner-splash-backdrop__img--icon"}`,
    src,
    alt: "",
    loading: "lazy",
    decoding: "async",
  });

  return el("div", { className: "planner-splash-backdrop", "aria-hidden": "true" }, [
    el("div", { className: "planner-splash-backdrop__shade" }),
    img,
  ]);
}

/** @deprecated */
export function renderPlannerSplashAside(opts) {
  return renderPlannerSplashBackdrop(opts);
}

/** @deprecated */
export function renderPlannerSplashFooter(opts) {
  return renderPlannerSplashBackdrop(opts);
}

/** @deprecated */
export function renderPlannerHero(opts) {
  return renderPlannerHeader(opts);
}
