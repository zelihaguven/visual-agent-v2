/** Konuşma modu: kullanıcının konuşmasının başını ve sonunu sesten anlar. */

const TICK_MS = 50;
const MIN_THRESHOLD = 0.02;
const NOISE_FACTOR = 3;
const NOISE_SMOOTHING = 0.05;
const MIN_SPEECH_MS = 200;
const END_SILENCE_MS = 900;
const MAX_UTTERANCE_MS = 30_000;
const NO_SPEECH_RESTART_MS = 15_000;
const BARGE_CALIBRATION_MS = 500;
const BARGE_MIN_THRESHOLD = 0.05;
const BARGE_ECHO_FACTOR = 1.8;
const BARGE_SPEECH_MS = 300;
const PRE_ROLL_MS = 1000;

export function canListen(): boolean {
  return typeof MediaRecorder !== "undefined" && Boolean(navigator.mediaDevices?.getUserMedia);
}

export type VadState = {
  hasSpeech: boolean;
  speechMs: number;
  silenceMs: number;
  elapsedMs: number;
  noiseFloor: number;
};

export type VadDecision = "continue" | "end" | "restart";

export const INITIAL_VAD: VadState = {
  hasSpeech: false,
  speechMs: 0,
  silenceMs: 0,
  elapsedMs: 0,
  noiseFloor: 0,
};

/** Eşik ortam gürültüsüne göre yükselir; gürültülü atölyede de konuşma ayırt edilir. */
export function speechThreshold(noiseFloor: number): number {
  return Math.max(MIN_THRESHOLD, noiseFloor * NOISE_FACTOR);
}

function stepBeforeSpeech(state: VadState, isLoud: boolean, level: number, deltaMs: number): VadState {
  if (isLoud) {
    const speechMs = state.speechMs + deltaMs;
    return { ...state, speechMs, hasSpeech: speechMs >= MIN_SPEECH_MS };
  }
  return {
    ...state,
    speechMs: 0,
    noiseFloor: state.noiseFloor + (level - state.noiseFloor) * NOISE_SMOOTHING,
  };
}

export function stepVad(
  state: VadState,
  level: number,
  deltaMs: number,
): { state: VadState; decision: VadDecision } {
  const isLoud = level > speechThreshold(state.noiseFloor);
  const elapsedMs = state.elapsedMs + deltaMs;
  if (!state.hasSpeech) {
    const next = { ...stepBeforeSpeech(state, isLoud, level, deltaMs), elapsedMs };
    return {
      state: next,
      decision: !next.hasSpeech && elapsedMs >= NO_SPEECH_RESTART_MS ? "restart" : "continue",
    };
  }
  const silenceMs = isLoud ? 0 : state.silenceMs + deltaMs;
  const isOver = silenceMs >= END_SILENCE_MS || elapsedMs >= MAX_UTTERANCE_MS;
  return { state: { ...state, elapsedMs, silenceMs }, decision: isOver ? "end" : "continue" };
}

export type BargeState = { elapsedMs: number; speechMs: number; echoPeak: number };

export const INITIAL_BARGE: BargeState = { elapsedMs: 0, speechMs: 0, echoPeak: 0 };

/** Sistem konuşurken eşik, mikrofona sızan kendi sesinin üstünde tutulur. */
export function bargeThreshold(echoPeak: number): number {
  return Math.max(BARGE_MIN_THRESHOLD, echoPeak * BARGE_ECHO_FACTOR);
}

export function stepBarge(
  state: BargeState,
  level: number,
  deltaMs: number,
): { state: BargeState; isBarge: boolean } {
  const elapsedMs = state.elapsedMs + deltaMs;
  if (elapsedMs <= BARGE_CALIBRATION_MS) {
    return {
      state: { ...state, elapsedMs, echoPeak: Math.max(state.echoPeak, level) },
      isBarge: false,
    };
  }
  if (level > bargeThreshold(state.echoPeak)) {
    const speechMs = state.speechMs + deltaMs;
    return { state: { ...state, elapsedMs, speechMs }, isBarge: speechMs >= BARGE_SPEECH_MS };
  }
  return {
    state: {
      elapsedMs,
      speechMs: Math.max(0, state.speechMs - deltaMs),
      echoPeak: Math.max(state.echoPeak, level),
    },
    isBarge: false,
  };
}

export type Microphone = {
  stream: MediaStream;
  level: () => number;
  close: () => void;
  noiseFloor?: number;
};

export async function openMicrophone(): Promise<Microphone> {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
  });
  const context = new AudioContext();
  await context.resume();
  const analyser = context.createAnalyser();
  analyser.fftSize = 1024;
  context.createMediaStreamSource(stream).connect(analyser);
  const samples = new Float32Array(analyser.fftSize);
  return {
    stream,
    level: () => {
      analyser.getFloatTimeDomainData(samples);
      return Math.sqrt(samples.reduce((sum, value) => sum + value * value, 0) / samples.length);
    },
    close: () => {
      stream.getTracks().forEach((track) => track.stop());
      void context.close();
    },
  };
}

function record(stream: MediaStream): { stop: () => Promise<Blob>; cancel: () => void } {
  const recorder = new MediaRecorder(stream);
  const parts: Blob[] = [];
  recorder.ondataavailable = (event) => parts.push(event.data);
  recorder.start();
  const toBlob = () => new Blob(parts, { type: recorder.mimeType });
  return {
    stop: () =>
      new Promise((resolve) => {
        if (recorder.state === "inactive") {
          resolve(toBlob());
          return;
        }
        recorder.onstop = () => resolve(toBlob());
        recorder.stop();
      }),
    cancel: () => {
      if (recorder.state !== "inactive") {
        recorder.stop();
      }
    },
  };
}

/** Bir konuşma bitene kadar dinler; iptal edilirse null döner. */
export function listenForUtterance(
  microphone: Microphone,
  onLevel: (level: number) => void,
  signal: AbortSignal,
): Promise<Blob | null> {
  return new Promise((resolve) => {
    let recording = record(microphone.stream);
    let vad = INITIAL_VAD;
    const finish = (timer: number, result: Promise<Blob | null>) => {
      window.clearInterval(timer);
      void result.then(resolve);
    };
    const timer = window.setInterval(() => {
      if (signal.aborted) {
        recording.cancel();
        finish(timer, Promise.resolve(null));
        return;
      }
      const level = microphone.level();
      onLevel(level);
      const step = stepVad(vad, level, TICK_MS);
      vad = step.state;
      if (step.decision === "end") {
        microphone.noiseFloor = vad.noiseFloor;
        finish(timer, recording.stop());
      } else if (step.decision === "restart") {
        recording.cancel();
        recording = record(microphone.stream);
        vad = { ...INITIAL_VAD, noiseFloor: vad.noiseFloor };
      }
    }, TICK_MS);
  });
}

/**
 * Sistem konuşurken dinler. Kullanıcı araya girerse onBargeIn çağrılır ve konuşması
 * bitince kaydı döner; kayıt sürekli yenilendiği için ilk heceler kaybolmaz.
 */
export function listenForBargeIn(
  microphone: Microphone,
  session: AbortSignal,
  turnDone: AbortSignal,
  onBargeIn: () => void,
): Promise<Blob | null> {
  return new Promise((resolve) => {
    let recording = record(microphone.stream);
    let barge = INITIAL_BARGE;
    let rollingMs = 0;
    let vad: VadState | null = null;
    const timer = window.setInterval(() => {
      if (session.aborted || (vad === null && turnDone.aborted)) {
        window.clearInterval(timer);
        recording.cancel();
        resolve(null);
        return;
      }
      const level = microphone.level();
      if (vad !== null) {
        const step = stepVad(vad, level, TICK_MS);
        vad = step.state;
        if (step.decision === "end") {
          window.clearInterval(timer);
          void recording.stop().then(resolve);
        }
        return;
      }
      const step = stepBarge(barge, level, TICK_MS);
      barge = step.state;
      rollingMs += TICK_MS;
      if (step.isBarge) {
        vad = { ...INITIAL_VAD, hasSpeech: true, noiseFloor: microphone.noiseFloor ?? 0 };
        onBargeIn();
      } else if (rollingMs >= PRE_ROLL_MS) {
        recording.cancel();
        recording = record(microphone.stream);
        rollingMs = 0;
      }
    }, TICK_MS);
  });
}
