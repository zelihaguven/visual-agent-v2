import { afterEach, describe, expect, it, vi } from "vitest";

import {
  INITIAL_BARGE,
  INITIAL_VAD,
  bargeThreshold,
  speechThreshold,
  stepBarge,
  listenForBargeIn,
  listenForUtterance,
  stepVad,
  type BargeState,
  type Microphone,
  type VadDecision,
  type VadState,
} from "./listening";

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

function runBarge(levels: number[], start: BargeState = INITIAL_BARGE) {
  let state = start;
  let hasBarged = false;
  for (const level of levels) {
    const step = stepBarge(state, level, TICK);
    state = step.state;
    hasBarged = hasBarged || step.isBarge;
  }
  return { state, hasBarged };
}

describe("interrupting by voice", () => {
  it("detects the user talking over the answer", () => {
    expect(runBarge([...ticks(0.01, 600), ...ticks(0.2, 400)]).hasBarged).toBe(true);
  });

  it("is not fooled by its own voice leaking into the microphone", () => {
    expect(runBarge(ticks(0.12, 8000)).hasBarged).toBe(false);
  });

  it("raises the bar to the loudest echo it has heard", () => {
    const { state, hasBarged } = runBarge([...ticks(0.1, 600), ...ticks(0.14, 400)]);

    expect(hasBarged).toBe(false);
    expect(bargeThreshold(state.echoPeak)).toBeGreaterThan(0.14);
  });

  it("still hears a louder voice over the echo", () => {
    expect(runBarge([...ticks(0.05, 600), ...ticks(0.3, 400)]).hasBarged).toBe(true);
  });

  it("ignores a short noise", () => {
    expect(runBarge([...ticks(0.01, 600), ...ticks(0.3, 100), ...ticks(0.01, 300)]).hasBarged).toBe(
      false,
    );
  });

  it("tolerates brief dips inside a word", () => {
    const speech = [0.3, 0.3, 0.3, 0.01, 0.3, 0.3, 0.3, 0.01, 0.3, 0.3, 0.3];

    expect(runBarge([...ticks(0.01, 600), ...speech]).hasBarged).toBe(true);
  });

  it("does not trigger during calibration", () => {
    expect(runBarge(ticks(0.5, 450)).hasBarged).toBe(false);
  });
});

describe("ending while the microphone is already closed", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  class ClosedRecorder {
    state = "inactive";
    mimeType = "audio/webm";
    start() {}
    stop() {
      throw new DOMException("inactive", "InvalidStateError");
    }
  }

  const microphone = { stream: {}, level: () => 0, close: () => undefined } as unknown as Microphone;

  it("finishes listening without an error", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", ClosedRecorder);
    const controller = new AbortController();
    const result = listenForUtterance(microphone, () => undefined, controller.signal);

    controller.abort();
    await vi.advanceTimersByTimeAsync(60);

    await expect(result).resolves.toBeNull();
  });

  it("finishes the interruption monitor without an error", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", ClosedRecorder);
    const session = new AbortController();
    const result = listenForBargeIn(microphone, session.signal, new AbortController().signal, () => undefined);

    session.abort();
    await vi.advanceTimersByTimeAsync(60);

    await expect(result).resolves.toBeNull();
  });
});
