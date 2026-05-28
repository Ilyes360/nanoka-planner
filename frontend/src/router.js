import { renderHome } from "./views/home.js";
import { charactersList, weaponsList } from "./views/entityList.js";
import { renderCharacterDetail } from "./views/characterDetail.js";
import { renderWeaponDetail } from "./views/weaponDetail.js";
import { scrollToTop } from "./utils.js";

function updateNav(pathname) {
  document.querySelectorAll(".nav a").forEach((link) => {
    const href = link.getAttribute("href");
    const isHome = pathname === "/";
    const active = !isHome && (href === pathname || pathname.startsWith(`${href}/`));
    link.classList.toggle("active", active);
  });
}

export function navigate(pathname, { push = true } = {}) {
  if (push && window.location.pathname !== pathname) {
    history.pushState(null, "", pathname);
  }
  updateNav(pathname);
  scrollToTop();

  const app = document.getElementById("app");
  const parts = pathname.split("/").filter(Boolean);

  if (parts.length === 0) {
    app.replaceChildren(renderHome());
    return;
  }

  if (parts[0] === "characters" && parts.length === 1) {
    charactersList(app);
    return;
  }

  if (parts[0] === "characters" && parts.length === 2) {
    renderCharacterDetail(app, parts[1]);
    return;
  }

  if (parts[0] === "weapons" && parts.length === 1) {
    weaponsList(app);
    return;
  }

  if (parts[0] === "weapons" && parts.length === 2) {
    renderWeaponDetail(app, parts[1]);
    return;
  }

  navigate("/", { push: true });
}

export function initRouter() {
  document.body.addEventListener("click", (e) => {
    const link = e.target.closest("[data-link]");
    if (!link || link.target === "_blank") return;
    const href = link.getAttribute("href");
    if (!href || !href.startsWith("/")) return;
    e.preventDefault();
    navigate(href);
  });

  window.addEventListener("popstate", () => navigate(window.location.pathname, { push: false }));
  navigate(window.location.pathname, { push: false });
}
