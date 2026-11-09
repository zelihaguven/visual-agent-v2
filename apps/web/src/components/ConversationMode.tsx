import { useEffect, useRef, useState } from "react";

import { transcribeAudio, type Citation, type PhraseAudio } from "../api";
import { listenForUtterance, openMicrophone, type Microphone } from "../listening";
import type { AudioQueue } from "../speech";
import type { Turn } from "../turn";
import { TurnView } from "./TurnView";

const LEVEL_GAIN = 7;

type Phase = "starting" | "listening" | "thinking" | "speaking";

const STATUS: Record<Phase, string> = {
  starting: "Mikrofon açılıyor",
  listening: "Dinliyorum",
  thinking: "Bakıyorum",
  speaking: "Konuşuyorum",
};

const NOT_HEARD = "Anlayamadım, tekrar söyler misiniz?";
const NO_MICROPHONE = "Mikrofona erişilemedi. Tarayıcı iznini kontrol edin.";

type Props = {
  audio: AudioQueue;
  lastTurn: Turn | null;
  takeGreeting: () => PhraseAudio | null;
  playWaiting: () => void;
  onAsk: (question: string, signal: AbortSignal, onAudio: () => void) => Promise<void>;
  onOpenSource: (citation: Citation) => void;
  onClose: () => void;
};

async function transcribeSafely(audio: Blob): Promise<string> {
  try {
    return await transcribeAudio(audio);
  } catch {
    return "";
  }
}

export function ConversationMode(props: Props) {
  const { audio, lastTurn, onOpenSource, onClose } = props;
  const [phase, setPhase] = useState<Phase>("starting");
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bars = useRef<HTMLButtonElement>(null);
  const turnControl = useRef<AbortController | null>(null);
  const latest = useRef(props);

  useEffect(() => {
    latest.current = props;
  });

  useEffect(() => {
    const session = new AbortController();
    let microphone: Microphone | null = null;

    const showLevel = (level: number) =>
      bars.current?.style.setProperty("--level", String(Math.min(1, level * LEVEL_GAIN)));

    async function handleUtterance(recording: Blob) {
      setPhase("thinking");
      setNotice(null);
      latest.current.playWaiting();
      const text = await transcribeSafely(recording);
      if (session.signal.aborted) {
        return;
      }
      if (!text) {
        setNotice(NOT_HEARD);
        return;
      }
      const control = new AbortController();
      turnControl.current = control;
      await latest.current.onAsk(text, control.signal, () => setPhase("speaking"));
      await audio.whenIdle();
      turnControl.current = null;
    }

    async function converse() {
      try {
        microphone = await openMicrophone();
      } catch {
        setError(NO_MICROPHONE);
        return;
      }
      const greeting = latest.current.takeGreeting();
      if (greeting !== null) {
        setPhase("speaking");
        audio.enqueue(greeting.audio, greeting.mime);
        await audio.whenIdle();
      }
      while (!session.signal.aborted) {
        setPhase("listening");
        showLevel(0);
        const recording = await listenForUtterance(microphone, showLevel, session.signal);
        if (recording !== null) {
          await handleUtterance(recording);
        }
      }
    }

    void converse();
    return () => {
      session.abort();
      turnControl.current?.abort();
      microphone?.close();
    };
  }, [audio]);

  function interrupt() {
    turnControl.current?.abort();
    audio.stop();
  }

  const canInterrupt = phase === "thinking" || phase === "speaking";
  return (
    <section className="talk" aria-label="Konuşma modu">
      <div className="talk-stage">
        <button
          ref={bars}
          type="button"
          className={`talk-bars is-${phase}`}
          aria-label={canInterrupt ? "Sözünü kes" : STATUS[phase]}
          disabled={!canInterrupt}
          onClick={interrupt}
        >
          {[0.55, 0.85, 1, 0.85, 0.55].map((weight, index) => (
            <span key={index} style={{ "--weight": weight } as React.CSSProperties} />
          ))}
        </button>
        {error !== null ? (
          <p className="notice is-bad" role="alert">
            {error}
          </p>
        ) : (
          <p className="talk-status" role="status">
            {STATUS[phase]}
          </p>
        )}
        {notice !== null && <p className="muted">{notice}</p>}
      </div>
      <div className="talk-turn">
        {lastTurn !== null && (
          <TurnView turn={lastTurn} onOpenSource={onOpenSource} onAskAgain={() => undefined} />
        )}
      </div>
      <button type="button" className="ghost talk-end" onClick={onClose}>
        Bitir
      </button>
    </section>
  );
}
