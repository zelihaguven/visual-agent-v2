import { useEffect, useRef, useState } from "react";

import { transcribeAudio, type Citation, type PhraseAudio } from "../api";
import {
  listenForBargeIn,
  listenForUtterance,
  openMicrophone,
  type Microphone,
} from "../listening";
import type { AudioQueue } from "../speech";
import type { Turn } from "../turn";
import { TurnView } from "./TurnView";

const LEVEL_GAIN = 7;
export const WAITING_DELAY_MS = 2000;

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
  onAsk: (
    question: string,
    signal: AbortSignal,
    onAudio: () => void,
    onSearching: () => void,
  ) => Promise<void>;
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

    /** Cevabı verir; kullanıcı araya girdiyse onun kaydını döndürür. */
    async function handleUtterance(mic: Microphone, recording: Blob): Promise<Blob | null> {
      setPhase("thinking");
      setNotice(null);
      const control = new AbortController();
      const monitorEnd = new AbortController();
      let hasBargedIn = false;
      turnControl.current = control;
      const monitor = listenForBargeIn(mic, session.signal, monitorEnd.signal, () => {
        hasBargedIn = true;
        control.abort();
        audio.stop();
        setPhase("listening");
      });
      const text = await transcribeSafely(recording);
      if (!text && !control.signal.aborted && !session.signal.aborted) {
        setNotice(NOT_HEARD);
      }
      if (text && !control.signal.aborted && !session.signal.aborted) {
        let waitingTimer: number | undefined;
        await latest.current.onAsk(
          text,
          control.signal,
          () => {
            window.clearTimeout(waitingTimer);
            setPhase("speaking");
          },
          () => {
            waitingTimer = window.setTimeout(() => {
              if (!control.signal.aborted) {
                latest.current.playWaiting();
              }
            }, WAITING_DELAY_MS);
          },
        );
        window.clearTimeout(waitingTimer);
      }
      await audio.whenIdle();
      turnControl.current = null;
      if (!hasBargedIn) {
        monitorEnd.abort();
      }
      return monitor;
    }

    async function converse() {
      let mic: Microphone;
      try {
        mic = await openMicrophone();
      } catch {
        setError(NO_MICROPHONE);
        return;
      }
      if (session.signal.aborted) {
        mic.close();
        return;
      }
      microphone = mic;
      const greeting = latest.current.takeGreeting();
      if (greeting !== null) {
        setPhase("speaking");
        audio.enqueue(greeting.audio, greeting.mime);
        await audio.whenIdle();
      }
      let recording: Blob | null = null;
      while (!session.signal.aborted) {
        if (recording === null) {
          setPhase("listening");
          showLevel(0);
          recording = await listenForUtterance(mic, showLevel, session.signal);
        }
        recording = recording === null ? null : await handleUtterance(mic, recording);
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
