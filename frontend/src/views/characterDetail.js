import { apiClient } from "../apiClient.js";
import { renderCharacterPage } from "../components/characterPage.js";
import { renderLevelPlanner } from "../components/levelPlanner.js";
import { renderTalentPlanner } from "../components/talentPlanner.js";
import { el, scrollToTop } from "../utils.js";
import { aggregateAscensionReport, ASCENSION_LEVELS, TALENT_LEVELS } from "../utils/plannerAggregate.js";

export async function renderCharacterDetail(container, id) {
  container.replaceChildren(el("p", { className: "status", text: "Loading planner…" }));

  let data;
  try {
    data = await apiClient.character(id);
  } catch (err) {
    container.replaceChildren(
      el("p", { className: "status status--error" }, [
        document.createTextNode(`${err.message}. `),
        el("a", { href: "/characters", "data-link": "", text: "Back" }),
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
      getDataForLevel: (level) => aggregateAscensionReport(asc, level, "character"),
    }),
    renderTalentPlanner({
      report: data.talents,
      levels: TALENT_LEVELS,
      initialLevel: 10,
    }),
  ];

  container.replaceChildren(renderCharacterPage(data, planners));
  scrollToTop();
}
