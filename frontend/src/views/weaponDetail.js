import { apiClient } from "../apiClient.js";
import { renderLevelPlanner } from "../components/levelPlanner.js";
import { renderWeaponPage } from "../components/weaponPage.js";
import { el, scrollToTop } from "../utils.js";
import { aggregateAscensionReport, ASCENSION_LEVELS } from "../utils/plannerAggregate.js";

export async function renderWeaponDetail(container, id) {
  container.replaceChildren(el("p", { className: "status", text: "Loading planner…" }));

  let data;
  try {
    data = await apiClient.weapon(id);
  } catch (err) {
    container.replaceChildren(
      el("p", { className: "status status--error" }, [
        document.createTextNode(`${err.message}. `),
        el("a", { href: "/weapons", "data-link": "", text: "Back" }),
      ]),
    );
    return;
  }

  const asc = data.ascension;

  const planners = [
    renderLevelPlanner({
      title: "Ascension",
      levels: ASCENSION_LEVELS,
      initialLevel: 90,
      getDataForLevel: (level) => aggregateAscensionReport(asc, level, "weapon"),
    }),
  ];

  container.replaceChildren(renderWeaponPage(data, planners));
  scrollToTop();
}
