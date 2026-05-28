/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";
import { el } from "../src/utils.js";

describe("el", () => {
  it("creates an element with class, text, and children", () => {
    const child = el("span", { text: "child" });
    const node = el("div", { className: "box", text: "hello" }, [child]);

    expect(node.tagName).toBe("DIV");
    expect(node.className).toBe("box");
    expect(node.childNodes).toHaveLength(2);
    expect(node.textContent).toBe("hellochild");
  });

  it("wires event handlers", () => {
    let clicked = false;
    const btn = el("button", { onClick: () => { clicked = true; }, text: "Go" });
    btn.click();
    expect(clicked).toBe(true);
  });
});
