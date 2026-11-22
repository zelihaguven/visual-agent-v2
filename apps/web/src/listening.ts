/** Konuşma modu: kullanıcının konuşmasının başını ve sonunu sesten anlar. */

const TICK_MS = 50;
const MIN_THRESHOLD = 0.02;
const NOISE_FACTOR = 3;
const NOISE_SMOOTHING = 0.05;
const MIN_SPEECH_MS = 200;
const END_SILENCE_MS = 900;
const MAX_UTTERANCE_MS = 30_000;
const NO_SPEECH_RESTART_MS = 15_000;
const BARGE_SETTLE_MS = 500;
const BARGE_MIN_THRESHOLD = 0.05;
const BARGE_ECHO_FACTOR = 1.8;
const BARGE_ECHO_SMOOTHING = 0.05;
const BARGE_SPEECH_MS = 300;
const BARGE_LATE_SPEECH_MS = 150;
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

/**
 * Sistem konuşurken eşik, mikrofona sızan kendi sesinin üstünde tutulur. Yankı tahmini yavaş
 * yükselir, hiç düşmez: eşiğin altında kalan tek bir an (kullanıcının hece arası) tahmini
 * sıçratırsa eşik konuşanın sesinin üstüne çıkar ve söz kesilemez. Turun ilk yarım saniyesi
 * ne söz kesme sayılır ne yankı: o an sistem henüz konuşmuyor, duyulan kullanıcının sorusunun
 * sonudur (2026-11-22 ölçümü: bu ses yankı sayılınca eşik tur boyunca kilitleniyordu).
 */
export function bargeThreshold(echoPeak: number): number {
  return Math.max(BARGE_MIN_THRESHOLD, echoPeak * BARGE_ECHO_FACTOR);
}

export function stepBarge(
  state: BargeState,
  level: number,
  deltaMs: number,
): { state: BargeState; isBarge: boolean } {
  const elapsedMs = state.elapsedMs + deltaMs;
  if (elapsedMs <= BARGE_SETTLE_MS) {
    return { state: { ...state, elapsedMs }, isBarge: false };
  }
  if (level > bargeThreshold(state.echoPeak)) {
    const speechMs = state.speechMs + deltaMs;
    return { state: { ...state, elapsedMs, speechMs }, isBarge: speechMs >= BARGE_SPEECH_MS };
  }
  return {
    state: {
      elapsedMs,
      speechMs: Math.max(0, state.speechMs - deltaMs),
      echoPeak: state.echoPeak + Math.max(0, level - state.echoPeak) * BARGE_ECHO_SMOOTHING,
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

/** Kullanıcı "bitti" dedi (halkaya bastı): o ana kadar söylenen, sessizlik beklenmeden alınır. */
export type FinishRequest = { requested: boolean };

function takeFinish(finish: FinishRequest | undefined, vad: VadState | null): boolean {
  if (finish === undefined || !finish.requested) {
    return false;
  }
  finish.requested = false;
  return vad !== null && vad.hasSpeech;
}

export type Recording = { stop: () => Promise<Blob>; cancel: () => void };

export function record(stream: MediaStream): Recording {
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
  finishRequest?: FinishRequest,
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
      if (step.decision === "end" || takeFinish(finishRequest, vad)) {
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
 * bitince kaydı döner; kayıt sürekli yenilendiği için ilk heceler kaybolmaz. Sistem sustuğu
 * anda kullanıcı konuşmaya başlamışsa (kısa cevabın sonuna denk gelen söz) o da araya girme
 * sayılır: kayıt atılıp dinleme baştan başlasaydı ilk sözcükler kaybolurdu.
 */
export function listenForBargeIn(
  microphone: Microphone,
  session: AbortSignal,
  turnDone: AbortSignal,
  onBargeIn: () => void,
  finishRequest?: FinishRequest,
): Promise<Blob | null> {
  return new Promise((resolve) => {
    let recording = record(microphone.stream);
    let barge = INITIAL_BARGE;
    let rollingMs = 0;
    let vad: VadState | null = null;
    const interrupt = () => {
      vad = { ...INITIAL_VAD, hasSpeech: true, noiseFloor: microphone.noiseFloor ?? 0 };
      onBargeIn();
    };
    const timer = window.setInterval(() => {
      const isOver = vad === null && turnDone.aborted;
      if (isOver && !session.aborted && barge.speechMs >= BARGE_LATE_SPEECH_MS) {
        interrupt();
        return;
      }
      if (session.aborted || isOver) {
        window.clearInterval(timer);
        recording.cancel();
        resolve(null);
        return;
      }
      const level = microphone.level();
      if (vad !== null) {
        const step = stepVad(vad, level, TICK_MS);
        vad = step.state;
        if (step.decision === "end" || takeFinish(finishRequest, vad)) {
          window.clearInterval(timer);
          void recording.stop().then(resolve);
        }
        return;
      }
      const step = stepBarge(barge, level, TICK_MS);
      barge = step.state;
      rollingMs += TICK_MS;
      if (step.isBarge) {
        interrupt();
      } else if (rollingMs >= PRE_ROLL_MS) {
        recording.cancel();
        recording = record(microphone.stream);
        rollingMs = 0;
      }
    }, TICK_MS);
  });
}
