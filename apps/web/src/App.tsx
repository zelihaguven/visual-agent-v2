import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";

import {
  askQuestion,
  fetchVoicePhrases,
  requestSpeech,
  type Citation,
  type ConversationContext,
  type PhraseAudio,
  type SpokenItem,
  type VoicePhrases,
} from "./api";
import "./App.css";
import { ContextBar } from "./components/ContextBar";
import { ConversationMode } from "./components/ConversationMode";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { Drawer } from "./components/Drawer";
import { MicButton } from "./components/MicButton";
import { SourcePanel } from "./components/SourcePanel";
import { TurnView, type SpeechStatus } from "./components/TurnView";
import { MAX_QUESTION_CHARS } from "./limits";
import { canListen } from "./listening";
import { AudioQueue } from "./speech";
import { applyEvent, newTurn, type Turn } from "./turn";

const ASK_FAILED = "Cevap alınamadı. Bağlantınızı kontrol edip yeniden deneyin.";
const ASK_STOPPED = "Soru durduruldu.";

type AskOptions = {
  context: ConversationContext | null;
  speak?: boolean;
  dictated?: boolean;
  signal?: AbortSignal;
  onAudio?: () => void;
  onSearching?: () => void;
};

export function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [draft, setDraft] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [source, setSource] = useState<Citation | null>(null);
  const [context, setContext] = useState<ConversationContext | null>(null);
  const [isTalking, setIsTalking] = useState(false);
  const [speech, setSpeech] = useState<{ turnId: string; status: SpeechStatus } | null>(null);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [hasVoiceService, setHasVoiceService] = useState(true);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [documentCount, setDocumentCount] = useState<number | null>(null);
  const closeLibrary = useCallback(() => setIsLibraryOpen(false), []);
  const nextId = useRef(0);
  const audio = useRef<AudioQueue | null>(null);
  const draftInput = useRef<HTMLInputElement>(null);
  const draftFromVoice = useRef(false);
  const phrases = useRef<VoicePhrases | null>(null);
  const hasGreeted = useRef(false);
  const waitingTurn = useRef(0);
  const latestContext = useRef<ConversationContext | null>(null);
  const activeAsk = useRef<AbortController | null>(null);
  const stoppedByUser = useRef<AbortController | null>(null);
  const speechToken = useRef(0);
  const turnList = useRef<HTMLDivElement>(null);
  const shownTurns = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    fetchVoicePhrases(controller.signal)
      .then((ready) => {
        if (ready === null) {
          setHasVoiceService(false);
        } else {
          phrases.current = ready;
        }
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, []);

  useEffect(() => {
    // Yeni soru görünür alanın en üstüne gelir; önceki sorular yukarıda kalır.
    if (turns.length > shownTurns.current) {
      const newest = turnList.current?.lastElementChild;
      newest?.scrollIntoView?.({ block: "start", behavior: "smooth" });
    }
    shownTurns.current = turns.length;
  }, [turns.length]);

  function audioQueue(): AudioQueue {
    audio.current ??= new AudioQueue();
    return audio.current;
  }

  function playWaitingPhrase() {
    const waiting = phrases.current?.waiting ?? [];
    if (waiting.length > 0) {
      const phrase = waiting[waitingTurn.current % waiting.length];
      waitingTurn.current += 1;
      audioQueue().enqueue(phrase.audio, phrase.mime);
    }
  }

  function updateContext(next: ConversationContext | null) {
    latestContext.current = next;
    setContext(next);
  }

  async function ask(
    question: string,
    docIds: string[] | null,
    { context: turnContext, speak = false, dictated = false, signal, onAudio, onSearching }: AskOptions,
  ) {
    nextId.current += 1;
    const id = String(nextId.current);
    const updateTurn = (change: (turn: Turn) => Turn) =>
      setTurns((current) => current.map((turn) => (turn.id === id ? change(turn) : turn)));
    // Aynı anda tek soru: yenisi öncekini iptal eder, sunucu da onu cevaplamayı bırakır.
    activeAsk.current?.abort();
    const control = new AbortController();
    activeAsk.current = control;
    const stop = () => control.abort();
    if (signal?.aborted) {
      control.abort();
    }
    signal?.addEventListener("abort", stop);
    setTurns((current) => [...current, newTurn(id, question)]);
    setIsAsking(true);
    try {
      await askQuestion(
        question,
        docIds,
        turnContext,
        speak,
        (event) => {
          updateTurn((turn) => applyEvent(turn, event));
          if (event.type === "searching") {
            onSearching?.();
          }
          if (event.type === "item_audio") {
            audioQueue().enqueue(event.audio, event.mime);
            onAudio?.();
          }
          if (event.type === "done" && activeAsk.current === control) {
            updateContext(event.context);
          }
        },
        control.signal,
        dictated,
      );
    } catch {
      updateTurn((turn) => {
        if (stoppedByUser.current === control) {
          return { ...turn, stage: null, notice: ASK_STOPPED };
        }
        return control.signal.aborted
          ? { ...turn, stage: null }
          : applyEvent(turn, { type: "error", message: ASK_FAILED });
      });
    } finally {
      signal?.removeEventListener("abort", stop);
      if (activeAsk.current === control) {
        activeAsk.current = null;
        setIsAsking(false);
      }
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = draft.trim();
    if (question && !isAsking) {
      setDraft("");
      setVoiceError(null);
      const dictated = draftFromVoice.current;
      draftFromVoice.current = false;
      void ask(question, null, { context, dictated });
    }
  }

  function stopAsking() {
    stoppedByUser.current = activeAsk.current;
    activeAsk.current?.abort();
  }

  function takeGreeting(): PhraseAudio | null {
    const greeting = phrases.current?.greeting ?? null;
    if (greeting === null || hasGreeted.current) {
      return null;
    }
    hasGreeted.current = true;
    return greeting;
  }

  function stopAnswerSpeech() {
    speechToken.current += 1;
    audioQueue().stop();
    setSpeech(null);
  }

  function openConversation() {
    stopAnswerSpeech();
    audioQueue().unlock();
    setIsTalking(true);
  }

  function closeConversation() {
    audioQueue().stop();
    setIsTalking(false);
  }

  async function speakAnswer(turnId: string, items: SpokenItem[]) {
    const isSameTurn = speech?.turnId === turnId;
    stopAnswerSpeech();
    if (isSameTurn) {
      return;
    }
    const token = speechToken.current;
    audioQueue().unlock();
    setSpeech({ turnId, status: "loading" });
    try {
      const audios = await requestSpeech(items);
      if (token !== speechToken.current) {
        return;
      }
      audios.forEach((item) => audioQueue().enqueue(item.audio, item.mime));
      setSpeech({ turnId, status: "playing" });
      await audioQueue().whenIdle();
    } catch {
      setVoiceError("Cevap seslendirilemedi. Yeniden deneyin.");
    }
    if (token === speechToken.current) {
      setSpeech(null);
    }
  }

  function handleTranscript(text: string) {
    setVoiceError(null);
    draftFromVoice.current = true;
    setDraft(text);
    draftInput.current?.focus();
  }

  const isLanding = turns.length === 0;
  return (
    <div className={`layout ${isLanding ? "is-landing" : "is-asking"}`}>
      <header className="topbar">
        <span className="brand">Visual Agent</span>
        <button
          type="button"
          className="library-button"
          aria-label={documentCount === null ? "Belgeler" : `Belgeler (${documentCount})`}
          aria-expanded={isLibraryOpen}
          onClick={() => setIsLibraryOpen(true)}
        >
          Belgeler{documentCount !== null && <span className="count">{documentCount}</span>}
        </button>
      </header>
      <main className="conversation">
        {isLanding ? (
          <div className="hero">
            <h1>Belgelerinize sorun.</h1>
            <p>Cevap, kaynağıyla birlikte gelir.</p>
          </div>
        ) : (
          <div className="turns" ref={turnList}>
            {turns.map((turn) => (
              <TurnView
                key={turn.id}
                turn={turn}
                onOpenSource={setSource}
                onAskAgain={(question, docIds) => void ask(question, docIds, { context: null })}
                isBusy={isAsking}
                speechStatus={speech?.turnId === turn.id ? speech.status : "idle"}
                onSpeak={(items) => void speakAnswer(turn.id, items)}
              />
            ))}
          </div>
        )}
        <div className="composer-area">
          {context !== null && (
            <ContextBar context={context} onClear={() => updateContext(null)} />
          )}
          {voiceError !== null && (
            <p className="notice is-bad composer-notice" role="alert">
              {voiceError}
            </p>
          )}
          <form className="composer" onSubmit={handleSubmit}>
            <label htmlFor="question" className="visually-hidden">
              Sorunuz
            </label>
            <input
              id="question"
              ref={draftInput}
              value={draft}
              maxLength={MAX_QUESTION_CHARS}
              autoComplete="off"
              placeholder="Sorunuzu yazın"
              onChange={(event) => {
                if (event.target.value === "") {
                  draftFromVoice.current = false;
                }
                setDraft(event.target.value);
              }}
            />
            <MicButton isDisabled={isAsking} onTranscript={handleTranscript} onError={setVoiceError} />
            {canListen() && hasVoiceService && (
              <button
                type="button"
                className="icon-button"
                aria-label="Konuşma modu"
                title="Konuşma modu"
                onClick={openConversation}
              >
                <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M3 10h2v4H3v-4Zm4-4h2v12H7V6Zm4-3h2v18h-2V3Zm4 3h2v12h-2V6Zm4 4h2v4h-2v-4Z"
                  />
                </svg>
              </button>
            )}
            {isAsking && !isTalking ? (
              <button type="button" className="stop-button" onClick={stopAsking}>
                Durdur
              </button>
            ) : (
              <button type="submit" disabled={isAsking || draft.trim() === ""}>
                Sor
              </button>
            )}
          </form>
        </div>
        {isTalking && (
          <ConversationMode
            audio={audioQueue()}
            lastTurn={turns.at(-1) ?? null}
            takeGreeting={takeGreeting}
            playWaiting={playWaitingPhrase}
            onAsk={(question, choice, signal, onAudio, onSearching) =>
              ask(question, choice?.docIds ?? null, {
                // Seçim yeni bir sorudur; yazılı moddaki gibi bağlam taşımaz.
                context: choice === null ? latestContext.current : null,
                speak: true,
                signal,
                onAudio,
                onSearching,
              })
            }
            onOpenSource={setSource}
            onClose={closeConversation}
          />
        )}
      </main>
      <Drawer isOpen={isLibraryOpen} side="left" label="Belgeler" onClose={closeLibrary}>
        <DocumentsPanel onClose={closeLibrary} onCountChange={setDocumentCount} />
      </Drawer>
      <Drawer isOpen={source !== null} side="right" label="Kaynak" onClose={() => setSource(null)}>
        {source !== null && <SourcePanel citation={source} onClose={() => setSource(null)} />}
      </Drawer>
    </div>
  );
}
