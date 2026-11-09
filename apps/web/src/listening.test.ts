import { describe, expect, it } from "vitest";

import { INITIAL_VAD, speechThreshold, stepVad, type VadDecision, type VadState } from "./listening";

const TICK = 50;

function run(levels: number[], start: VadState = INITIAL_VAD) {
  let state = start;
  const decisions: VadDecision[] = [];
  for (const level of levels) {
    const step = stepVad(state, level, TICK);
    state = step.state;
    decisions.push(step.decision);
  }
  return { state, decisions };
}

const ticks = (level: number, ms: number) => Array<number>(Math.ceil(ms / TICK)).fill(level);

describe("speech detection", () => {
  it("ends after a pause that follows speech", () => {
    const { decisions } = run([...ticks(0.2, 400), ...ticks(0.001, 900)]);

    expect(decisions.at(-1)).toBe("end");
    expect(decisions.slice(0, -1)).not.toContain("end");
  });

  it("does not end during a short pause between words", () => {
    const { decisions } = run([...ticks(0.2, 400), ...ticks(0.001, 500), ...ticks(0.2, 100)]);

    expect(decisions).not.toContain("end");
  });

  it("ignores a short click", () => {
    const { state, decisions } = run([...ticks(0.5, 100), ...ticks(0.001, 2000)]);

    expect(state.hasSpeech).toBe(false);
    expect(decisions).not.toContain("end");
  });

  it("restarts the recording when nobody speaks", () => {
    expect(run(ticks(0.001, 15_000)).decisions.at(-1)).toBe("restart");
  });

  it("stops a very long utterance", () => {
    expect(run(ticks(0.2, 30_000)).decisions.at(-1)).toBe("end");
  });

  it("raises the threshold in a noisy room", () => {
    const { state } = run(ticks(0.015, 4000));
    const noisy = run(ticks(0.03, 1000), { ...INITIAL_VAD, noiseFloor: 0.015 });

    expect(speechThreshold(0.015)).toBeGreaterThan(0.03);
    expect(state.hasSpeech).toBe(false);
    expect(noisy.state.hasSpeech).toBe(false);
  });
});
