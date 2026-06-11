// @vitest-environment jsdom

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import QuestionPanel from "../../../src/content/ui/QuestionPanel.svelte";
import { resetAppState } from "../../helpers/app-state.js";
import { renderSvelte, flushUi } from "../../helpers/svelte.js";

describe("QuestionPanel integration", () => {
  beforeEach(() => {
    resetAppState({
      ui: { showToast: vi.fn() },
    });
    document.body.innerHTML = `
      <div class="ds-textarea">
        <textarea id="chat-input"></textarea>
      </div>
      <button title="Send message"></button>
    `;
    document.querySelector('button[title="Send message"]').click = vi.fn();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders questions, supports keyboard selection, and submits answers", async () => {
    const { target, cleanup } = renderSvelte(QuestionPanel);
    await flushUi();

    window.dispatchEvent(
      new CustomEvent("bds-ask-questions", {
        detail: {
          questions: [
            {
              id: "q1",
              question: "Pick one",
              type: "test",
              options: ["Alpha", "Beta"],
            },
          ],
        },
      }),
    );
    await vi.advanceTimersByTimeAsync(150);
    await flushUi();

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    await vi.advanceTimersByTimeAsync(1000);

    expect(document.querySelector("#chat-input").value).toContain("Beta");
    expect(document.querySelector('button[title="Send message"]').click).toHaveBeenCalled();
    cleanup();
  });

  it("attaches to a contenteditable composer when no textarea is present", async () => {
    document.body.innerHTML = `
      <div class="composer-shell">
        <div role="textbox" contenteditable="plaintext-only"></div>
      </div>
      <button title="Send message"></button>
    `;
    document.querySelector('button[title="Send message"]').click = vi.fn();

    const { cleanup } = renderSvelte(QuestionPanel);
    await flushUi();

    window.dispatchEvent(
      new CustomEvent("bds-ask-questions", {
        detail: {
          questions: [
            {
              id: "q1",
              question: "Pick one",
              type: "test",
              options: ["Alpha", "Beta"],
            },
          ],
        },
      }),
    );
    await vi.advanceTimersByTimeAsync(150);
    await flushUi();

    expect(document.querySelector(".bds-question-panel")?.parentElement?.classList.contains("composer-shell")).toBe(true);

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }));
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    await vi.advanceTimersByTimeAsync(1000);

    expect(document.querySelector('[role="textbox"]').textContent).toContain("Beta");
    expect(document.querySelector('button[title="Send message"]').click).toHaveBeenCalled();
    cleanup();
  });

  it("does not consume typing keys while a panel input is focused", async () => {
    const { cleanup } = renderSvelte(QuestionPanel);
    await flushUi();

    window.dispatchEvent(
      new CustomEvent("bds-ask-questions", {
        detail: {
          questions: [
            {
              id: "q1",
              question: "Explain",
              type: "input",
            },
          ],
        },
      }),
    );
    await vi.advanceTimersByTimeAsync(150);
    await flushUi();

    const input = document.querySelector(".bds-text-input");
    input.focus();
    const event = new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true, cancelable: true });
    window.dispatchEvent(event);

    expect(event.defaultPrevented).toBe(false);
    cleanup();
  });
});
