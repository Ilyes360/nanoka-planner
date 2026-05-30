/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderLevelSlider } from "../src/components/levelSlider.js";

const LEVELS = [1, 20, 40, 50, 60, 70, 80, 90];

function mount(initialValue, opts) {
  const onChange = vi.fn();
  const node = renderLevelSlider(LEVELS, initialValue, onChange, opts);
  document.body.replaceChildren(node);
  return {
    onChange,
    node,
    badge: node.querySelector(".level-slider__badge"),
    input: node.querySelector(".level-slider__input"),
    ticks: [...node.querySelectorAll(".level-slider__ticks > span")],
  };
}

beforeEach(() => {
  document.body.innerHTML = "";
});

describe("renderLevelSlider", () => {
  it("aligne la valeur initiale sur le palier le plus proche", () => {
    const { badge, input, ticks } = mount(38);
    expect(badge.textContent).toBe("40");
    expect(input.getAttribute("aria-valuenow")).toBe("40");
    expect(ticks[2].classList.contains("active")).toBe(true);
  });

  it("appelle onChange une fois au montage avec la valeur initiale", () => {
    const { onChange } = mount(90);
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenLastCalledWith(90);
  });

  it("met à jour badge, aria et onChange au clic sur un tick", () => {
    const { onChange, badge, input, ticks } = mount(90);
    onChange.mockClear();

    ticks[0].click();

    expect(badge.textContent).toBe("1");
    expect(input.value).toBe("0");
    expect(input.getAttribute("aria-valuenow")).toBe("1");
    expect(ticks[0].classList.contains("active")).toBe(true);
    expect(ticks[7].classList.contains("active")).toBe(false);
    expect(onChange).toHaveBeenLastCalledWith(1);
  });

  it("réagit à l'événement input du range", () => {
    const { onChange, badge, input } = mount(1);
    onChange.mockClear();

    input.value = "3";
    input.dispatchEvent(new Event("input"));

    expect(badge.textContent).toBe("50");
    expect(onChange).toHaveBeenLastCalledWith(50);
  });

  it("active un tick au clavier (Enter et Espace)", () => {
    const { onChange, ticks } = mount(1);
    onChange.mockClear();

    ticks[4].dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    expect(onChange).toHaveBeenLastCalledWith(60);

    ticks[1].dispatchEvent(new KeyboardEvent("keydown", { key: " ", bubbles: true }));
    expect(onChange).toHaveBeenLastCalledWith(20);
  });

  it("ignore les autres touches", () => {
    const { onChange, ticks } = mount(1);
    onChange.mockClear();
    ticks[5].dispatchEvent(new KeyboardEvent("keydown", { key: "Tab", bubbles: true }));
    expect(onChange).not.toHaveBeenCalled();
  });

  it("applique le pourcentage de remplissage via --pct", () => {
    const { input, ticks } = mount(1);
    expect(input.style.getPropertyValue("--pct")).toBe("0%");
    ticks[7].click();
    expect(input.style.getPropertyValue("--pct")).toBe("100%");
  });

  it("prend en charge le mode compact", () => {
    const { node } = mount(1, { compact: true });
    expect(node.classList.contains("level-slider--compact")).toBe(true);
  });

  it("affiche le label fourni", () => {
    const { node } = mount(1, { label: "Niveau" });
    expect(node.querySelector("h3").textContent).toBe("Niveau");
  });
});
