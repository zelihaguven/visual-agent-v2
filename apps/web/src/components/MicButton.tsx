import { useRef, useState } from "react";

import { transcribeAudio } from "../api";
import { canListen } from "../listening";

const MAX_RECORDING_MS = 60_000;

type MicState = "idle" | "recording" | "transcribing";

type Props = {
  isDisabled: boolean;
  onTranscript: (text: string) => void;
  onError: (message: string) => void;
};

const LABELS: Record<MicState, string> = {
  idle: "Konuşarak sor",
  recording: "Kaydı bitir",
  transcribing: "Yazıya çevriliyor",
};

export function MicButton({ isDisabled, onTranscript, onError }: Props) {
  const [state, setState] = useState<MicState>("idle");
  const recorder = useRef<MediaRecorder | null>(null);
  const limit = useRef<number | undefined>(undefined);

  async function send(audio: Blob) {
    setState("transcribing");
    try {
      const text = await transcribeAudio(audio);
      if (text) {
        onTranscript(text);
      } else {
        onError("Konuşma anlaşılamadı. Yeniden deneyin.");
      }
    } catch {
      onError("Ses yazıya çevrilemedi. Yeniden deneyin ya da yazarak sorun.");
    } finally {
      setState("idle");
    }
  }

  async function start() {
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      onError("Mikrofona erişilemedi. Tarayıcı iznini kontrol edin.");
      return;
    }
    const active = new MediaRecorder(stream);
    const parts: Blob[] = [];
    active.ondataavailable = (event) => parts.push(event.data);
    active.onstop = () => {
      window.clearTimeout(limit.current);
      stream.getTracks().forEach((track) => track.stop());
      void send(new Blob(parts, { type: active.mimeType }));
    };
    recorder.current = active;
    active.start();
    limit.current = window.setTimeout(() => active.stop(), MAX_RECORDING_MS);
    setState("recording");
  }

  function toggle() {
    if (state === "recording") {
      recorder.current?.stop();
    } else if (state === "idle") {
      void start();
    }
  }

  if (!canListen()) {
    return null;
  }
  return (
    <button
      type="button"
      className={`icon-button ${state === "recording" ? "is-active" : ""}`}
      aria-label={LABELS[state]}
      title={LABELS[state]}
      aria-pressed={state === "recording"}
      disabled={state === "transcribing" || (isDisabled && state === "idle")}
      onClick={toggle}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.9V22h2v-3.1a7 7 0 0 0 6-6.9h-2Z"
        />
      </svg>
    </button>
  );
}
