import { afterEach, describe, expect, it, vi } from "vitest";

import {
  INITIAL_BARGE,
  INITIAL_VAD,
  TURN_FAILED,
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
    // Yankı engellemeden sonra kalan düzey (2026-11-22 ölçümü: en çok 0,035).
    expect(runBarge(ticks(0.035, 8000)).hasBarged).toBe(false);
  });

  it("slowly raises the bar above a lasting echo", () => {
    const { state, hasBarged } = runBarge([...ticks(0.045, 4000), ...ticks(0.07, 400)]);

    expect(hasBarged).toBe(false);
    expect(bargeThreshold(state.echoPeak)).toBeGreaterThan(0.07);
  });

  it("does not take the tail of the question for its own echo", () => {
    // 2026-11-22 ölçümü: turun ilk yarım saniyesinde sorunun sonu duyuldu (0,08); yankı
    // sayılınca eşik 0,144'e kilitlendi ve 0,12–0,18 düzeyindeki söz hiç kesemedi.
    const tail = [0.002, 0.003, 0.015, 0.007, 0.008, 0.08, 0.056, 0.068, 0.047, 0.074];
    const speech = [0.166, 0.054, 0.076, 0.065, 0.155, 0.135, 0.135, 0.104, 0.12, 0.111];

    const { hasBarged } = runBarge([...tail, ...ticks(0.005, 2000), ...speech]);

    expect(hasBarged).toBe(true);
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

  it("is not locked out by the dips of the user's own speech", () => {
    // 2026-11-22 ölçümü (Mac, hoparlör): yankı 0,02'yi geçmedi; kullanıcının sesi 0,1–0,27
    // arasında, hece aralarında eşiğin hemen altına düşerek geldi ve eşiği 0,49'a taşımıştı.
    const answer = ticks(0.02, 2000);
    const speech = [0.146, 0.04, 0.107, 0.049, 0.134, 0.08, 0.26, 0.14, 0.275, 0.006, 0.174, 0.166];

    const { state, hasBarged } = runBarge([...ticks(0.002, 600), ...answer, ...speech, ...speech]);

    expect(hasBarged).toBe(true);
    expect(bargeThreshold(state.echoPeak)).toBeLessThan(0.1);
  });

  it("does not trigger in the first half second of the turn", () => {
    expect(runBarge(ticks(0.5, 450)).hasBarged).toBe(false);
  });
});

describe("listening with a working recorder", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  class FakeRecorder {
    state = "recording";
    mimeType = "audio/webm";
    ondataavailable: ((event: { data: Blob }) => void) | null = null;
    onstop: (() => void) | null = null;
    start() {}
    stop() {
      this.state = "inactive";
      this.ondataavailable?.({ data: new Blob(["ses"]) });
      this.onstop?.();
    }
  }

  function microphoneAt(level: { value: number }): Microphone {
    return { stream: {}, level: () => level.value, close: () => undefined } as unknown as Microphone;
  }

  it("takes what was said so far when the user says they are done", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const level = { value: 0.3 };
    const finish = { requested: false };
    const result = listenForUtterance(
      microphoneAt(level),
      () => undefined,
      new AbortController().signal,
      finish,
    );
    let heard: Blob | null | undefined;
    void result.then((blob) => (heard = blob));

    await vi.advanceTimersByTimeAsync(400);
    expect(heard).toBeUndefined();
    finish.requested = true;
    await vi.advanceTimersByTimeAsync(60);

    expect(heard).toBeInstanceOf(Blob);
    expect(finish.requested).toBe(false);
  });

  it("ignores being told it is done before anything was said", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const finish = { requested: true };
    const result = listenForUtterance(
      microphoneAt({ value: 0 }),
      () => undefined,
      new AbortController().signal,
      finish,
    );
    let heard: Blob | null | undefined;
    void result.then((blob) => (heard = blob));

    await vi.advanceTimersByTimeAsync(300);

    expect(heard).toBeUndefined();
    expect(finish.requested).toBe(false);
  });

  it("keeps words that start just as the system stops talking", async () => {
    // Kısa cevabın sonuna denk gelen söz: 300 ms dolmadan sistem sustu; kayıt atılmamalı.
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const level = { value: 0 };
    const turnDone = new AbortController();
    const onBargeIn = vi.fn();
    const result = listenForBargeIn(
      microphoneAt(level),
      new AbortController().signal,
      turnDone.signal,
      onBargeIn,
    );
    let heard: Blob | null | undefined;
    void result.then((blob) => (heard = blob));

    await vi.advanceTimersByTimeAsync(600);
    level.value = 0.3;
    await vi.advanceTimersByTimeAsync(200);
    turnDone.abort();
    await vi.advanceTimersByTimeAsync(60);
    expect(onBargeIn).toHaveBeenCalledTimes(1);
    expect(heard).toBeUndefined();
    level.value = 0;
    await vi.advanceTimersByTimeAsync(1000);

    expect(heard).toBeInstanceOf(Blob);
  });

  it("does not let a stale request cut the next interruption short", async () => {
    // "Bitti" sistem konuşurken ya da dinleme biterken basılmış olabilir; sonraki söz kesmede
    // kullanıcının sorusu ilk hecede kapanmamalı.
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const level = { value: 0 };
    const finish = { requested: true };
    const result = listenForBargeIn(
      microphoneAt(level),
      new AbortController().signal,
      new AbortController().signal,
      () => undefined,
      finish,
    );
    let heard: Blob | null | undefined;
    void result.then((blob) => (heard = blob));

    await vi.advanceTimersByTimeAsync(600);
    level.value = 0.3;
    await vi.advanceTimersByTimeAsync(800);

    expect(finish.requested).toBe(false);
    expect(heard).toBeUndefined();
  });

  it("does not take speech for a new question when the turn failed", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const level = { value: 0 };
    const turnDone = new AbortController();
    const onBargeIn = vi.fn();
    const result = listenForBargeIn(
      microphoneAt(level),
      new AbortController().signal,
      turnDone.signal,
      onBargeIn,
    );

    await vi.advanceTimersByTimeAsync(600);
    level.value = 0.3;
    await vi.advanceTimersByTimeAsync(200);
    turnDone.abort(TURN_FAILED);
    await vi.advanceTimersByTimeAsync(60);

    await expect(result).resolves.toBeNull();
    expect(onBargeIn).not.toHaveBeenCalled();
  });

  it("just stops when the system finishes and nobody is talking", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    const turnDone = new AbortController();
    const onBargeIn = vi.fn();
    const result = listenForBargeIn(
      microphoneAt({ value: 0.01 }),
      new AbortController().signal,
      turnDone.signal,
      onBargeIn,
    );

    await vi.advanceTimersByTimeAsync(800);
    turnDone.abort();
    await vi.advanceTimersByTimeAsync(60);

    await expect(result).resolves.toBeNull();
    expect(onBargeIn).not.toHaveBeenCalled();
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
