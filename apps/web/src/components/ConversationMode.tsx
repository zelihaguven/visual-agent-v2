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
/** Halkanın görünümü: akışın evresi, ya da dinlerken son kaydın yazıya çevrilememesi. */
type Ring = Phase | "not-heard";

const STATUS: Record<Ring, string> = {
  starting: "Mikrofon açılıyor",
  listening: "Dinliyorum",
  thinking: "Bakıyorum",
  speaking: "Konuşuyorum",
  "not-heard": "Anlayamadım",
};

const HINTS: Record<Ring, string> = {
  starting: "Bir saniye.",
  listening: "Sorunuzu bekliyorum.",
  thinking: "Kaynaklarda arıyorum, bir saniye.",
  speaking: "Araya girip konuşursanız susarım.",
  "not-heard": "Bir daha söyler misiniz? Kodları harf harf söylemek işe yarar.",
};

/** Yeni konuşma başladı sayılan ses düzeyi: "Anlayamadım" görünümü kalkar. */
const SPEECH_LEVEL = 0.3;
const RING_BARS = [0.35, 0.6, 0.85, 0.5, 1, 0.55, 0.8, 0.6, 0.4];
const CODE_RE = /([A-ZÇĞİÖŞÜ]{1,6}[-_]\d[\w-]*|[A-ZÇĞİÖŞÜ]+(?:_[A-ZÇĞİÖŞÜ0-9]+)+|\d{5,})/u;

/** Sorudaki kodlar (GML-6473, MUSTERI_KODU, 6029322) tek aralıklı yazılır; yalnız görünüm. */
function withCodes(text: string) {
  return text
    .split(CODE_RE)
    .map((part, index) => (index % 2 === 1 ? <code key={index}>{part}</code> : part));
}
const VOICE_FAILED = "Ses servisine ulaşılamadı. Bitir'e basıp yazarak sorabilirsiniz.";
const NO_MICROPHONE = "Mikrofona erişilemedi. Tarayıcı iznini kontrol edin.";

/** Ekrandaki netleştirme ya da "Tüm belgelerde ara" seçimi: soru o belgelerde yeniden sorulur. */
export type Choice = { question: string; docIds: string[] | null; allDocuments?: boolean };

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
  /** Sesli moddan çıkıp yazı kutusuna geçer. */
  onWrite: () => void;
};

export function ConversationMode(props: Props) {
  const { audio, lastTurn, onOpenSource, onClose, onWrite } = props;
  const [phase, setPhase] = useState<Phase>("starting");
  const [isNotHeard, setIsNotHeard] = useState(false);
  const notHeard = useRef(false);
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

    const markNotHeard = (value: boolean) => {
      notHeard.current = value;
      setIsNotHeard(value);
    };
    const showLevel = (level: number) => {
      const scaled = Math.min(1, level * LEVEL_GAIN);
      bars.current?.style.setProperty("--level", String(scaled));
      if (notHeard.current && scaled > SPEECH_LEVEL) {
        markNotHeard(false);
      }
    };

    /** Cevabı verir; kullanıcı araya girdiyse onun kaydını döndürür. */
    async function handleTurn(
      mic: Microphone,
      question: () => Promise<string>,
      choice: Choice | null,
    ): Promise<Blob | null> {
      setPhase("thinking");
      markNotHeard(false);
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
      let text: string;
      try {
        text = await question();
      } catch (error) {
        // Boş metin "duyulmadı"dır; servis hatası ayrı gösterilir ve döngü durur.
        turnControl.current = null;
        monitorEnd.abort();
        throw error;
      }
      if (!text && !control.signal.aborted && !session.signal.aborted) {
        markNotHeard(true);
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
          recording = await handleTurn(mic, () => transcribeAudio(heard), null);
        }
      }
    }

    converse().catch(() => {
      if (!session.signal.aborted) {
        setError(VOICE_FAILED);
      }
      // Dinlemiyorken mikrofon açık görünmesin.
      microphone?.close();
      microphone = null;
    });
    return () => {
      session.abort();
      turnControl.current?.abort();
      microphone?.close();
    };
  }, [audio]);

  function choose(question: string, docIds: string[] | null, allDocuments = false) {
    if (listenControl.current !== null) {
      pendingChoice.current = { question, docIds, allDocuments };
      listenControl.current.abort();
    }
  }

  function interrupt() {
    turnControl.current?.abort();
    audio.stop();
  }

  const canInterrupt = error === null && (phase === "thinking" || phase === "speaking");
  const ring: Ring = isNotHeard && phase === "listening" ? "not-heard" : phase;
  const icon = ring === "speaking" ? "speaker" : "mic";
  return (
    <section className="talk" aria-label="Konuşma modu">
      <header className="talk-top">
        <button type="button" className="talk-nav" onClick={onClose}>
          <Icon name="home" />
          Ana sayfa
        </button>
        <p className="talk-title">
          Sesli mod <span>· eller serbest</span>
        </p>
        <button type="button" className="talk-nav" onClick={onWrite}>
          <Icon name="keyboard" />
          Yazarak sor
        </button>
      </header>
      <div className="talk-body">
        <div className="talk-stage">
          <button
            ref={bars}
            type="button"
            className={`talk-ring is-${ring}`}
            aria-label={canInterrupt ? "Sözünü kes" : STATUS[ring]}
            disabled={!canInterrupt}
            onClick={interrupt}
          >
            <Icon name={icon} />
            <span className="talk-wave" aria-hidden="true">
              {RING_BARS.map((weight, index) => (
                <span
                  key={index}
                  style={{ "--weight": weight, "--i": index } as React.CSSProperties}
                />
              ))}
            </span>
            <span className="talk-dots" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
          </button>
          {error !== null ? (
            <p className="notice is-bad" role="alert">
              {error}
            </p>
          ) : (
            <>
              <h2 className="talk-status" role="status">
                {STATUS[ring]}
              </h2>
              <p className="talk-hint">{HINTS[ring]}</p>
            </>
          )}
        </div>
        <div className="talk-side">
          <section className="talk-heard" aria-label="Duyduğum">
            <h3>Duyduğum</h3>
            {ring === "not-heard" ? (
              <p className="talk-heard-empty">Ses geldi ama sözcükler çıkarılamadı.</p>
            ) : lastTurn !== null ? (
              <p className="talk-heard-text">{withCodes(lastTurn.question)}</p>
            ) : (
              <p className="talk-heard-empty">Henüz bir şey duymadım.</p>
            )}
            {canInterrupt && (
              <button type="button" className="talk-again" onClick={interrupt}>
                Tekrar söyleyeceğim
              </button>
            )}
          </section>
          {lastTurn !== null && (
            <div className="talk-turn">
              <TurnView
                turn={lastTurn}
                onOpenSource={onOpenSource}
                onAskAgain={choose}
                isBusy={!canChoose}
              />
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

const ICONS = {
  home: ["M3 11l9-7 9 7", "M5 10v10h14V10"],
  keyboard: [
    "M4 6h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z",
    "M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10",
  ],
  mic: ["M12 3a3 3 0 0 1 3 3v5a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3Z", "M5 11a7 7 0 0 0 14 0", "M12 18v3"],
  speaker: ["M11 5 6 9H3v6h3l5 4Z", "M15.5 8.5a5 5 0 0 1 0 7", "M18.5 5.5a9 9 0 0 1 0 13"],
};

/** Çizgi simgeler; renk metinden gelir. "Anlayamadım"da mikrofon üstü çizili değil: dinleme sürer. */
function Icon({ name }: { name: keyof typeof ICONS }) {
  return (
    <svg
      className="talk-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
