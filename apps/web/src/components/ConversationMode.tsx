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

/** Ekrandaki netleştirme ya da "Tüm belgelerde ara" seçimi: soru o belgelerde yeniden sorulur. */
export type Choice = { question: string; docIds: string[] | null };

type Props = {
  audio: AudioQueue;
  lastTurn: Turn | null;
  takeGreeting: () => PhraseAudio | null;
  playWaiting: () => void;
  onAsk: (
    question: string,
    choice: Choice | null,
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
  const [canChoose, setCanChoose] = useState(false);
  const bars = useRef<HTMLButtonElement>(null);
  const turnControl = useRef<AbortController | null>(null);
  const listenControl = useRef<AbortController | null>(null);
  const pendingChoice = useRef<Choice | null>(null);
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
    async function handleTurn(
      mic: Microphone,
      question: () => Promise<string>,
      choice: Choice | null,
    ): Promise<Blob | null> {
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
      const text = await question();
      if (!text && !control.signal.aborted && !session.signal.aborted) {
        setNotice(NOT_HEARD);
      }
      if (text && !control.signal.aborted && !session.signal.aborted) {
        let waitingTimer: number | undefined;
        await latest.current.onAsk(
          text,
          choice,
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
          // Ekrandaki seçim dinlemeyi keser ve döngünün içinde bir tur gibi cevaplanır:
          // araya girme ve bekleme sesi aynı kalır, mikrofon cevabı soru sanmaz.
          const listen = new AbortController();
          const stopListening = () => listen.abort();
          session.signal.addEventListener("abort", stopListening);
          listenControl.current = listen;
          setCanChoose(true);
          recording = await listenForUtterance(mic, showLevel, listen.signal);
          setCanChoose(false);
          session.signal.removeEventListener("abort", stopListening);
          listenControl.current = null;
          // Dinleme bir kayıtla bittiği anda seçim de yapıldıysa seçim kazanır; kayıt atılır.
          const choice = pendingChoice.current;
          pendingChoice.current = null;
          if (choice !== null && !session.signal.aborted) {
            recording = await handleTurn(mic, async () => choice.question, choice);
            continue;
          }
        }
        if (recording !== null) {
          const heard = recording;
          recording = await handleTurn(mic, () => transcribeSafely(heard), null);
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

  function choose(question: string, docIds: string[] | null) {
    if (listenControl.current !== null) {
      pendingChoice.current = { question, docIds };
      listenControl.current.abort();
    }
  }

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
          <TurnView
            turn={lastTurn}
            onOpenSource={onOpenSource}
            onAskAgain={choose}
            isBusy={!canChoose}
          />
        )}
      </div>
      <button type="button" className="ghost talk-end" onClick={onClose}>
        Bitir
      </button>
    </section>
  );
}
