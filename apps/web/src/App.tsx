import { useEffect, useRef, useState, type FormEvent } from "react";

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
import { MicButton } from "./components/MicButton";
import { SourcePanel } from "./components/SourcePanel";
import { TurnView, type SpeechStatus } from "./components/TurnView";
import { canListen } from "./listening";
import { AudioQueue } from "./speech";
import { applyEvent, newTurn, type Turn } from "./turn";

const ASK_FAILED = "Cevap alınamadı. Bağlantınızı kontrol edip yeniden deneyin.";

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
  const nextId = useRef(0);
  const audio = useRef<AudioQueue | null>(null);
  const draftInput = useRef<HTMLInputElement>(null);
  const draftFromVoice = useRef(false);
  const phrases = useRef<VoicePhrases | null>(null);
  const hasGreeted = useRef(false);
  const waitingTurn = useRef(0);
  const latestContext = useRef<ConversationContext | null>(null);
  const speechToken = useRef(0);

  useEffect(() => {
    const controller = new AbortController();
    fetchVoicePhrases(controller.signal)
      .then((ready) => {
        phrases.current = ready;
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, []);

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
    setTurns((current) => [...current, newTurn(id, question, docIds)]);
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
          if (event.type === "done") {
            updateContext(event.context);
          }
        },
        signal,
        dictated,
      );
    } catch {
      updateTurn((turn) =>
        signal?.aborted
          ? { ...turn, stage: null }
          : applyEvent(turn, { type: "error", message: ASK_FAILED }),
      );
    } finally {
      setIsAsking(false);
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

  return (
    <div className={`layout ${source ? "has-source" : ""}`}>
      <DocumentsPanel />
      <main className="conversation">
        <header className="masthead">
          <h1>Visual Agent</h1>
          <p>Belgelerinize sorun, cevabı kaynağıyla görün.</p>
        </header>
        <div className="turns">
          {turns.map((turn) => (
            <TurnView
              key={turn.id}
              turn={turn}
              onOpenSource={setSource}
              onAskAgain={(question, docIds) => void ask(question, docIds, { context: null })}
              speechStatus={speech?.turnId === turn.id ? speech.status : "idle"}
              onSpeak={(items) => void speakAnswer(turn.id, items)}
            />
          ))}
        </div>
        {context !== null && <ContextBar context={context} onClear={() => updateContext(null)} />}
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
            maxLength={2000}
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
          {canListen() && (
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
          <button type="submit" disabled={isAsking || draft.trim() === ""}>
            Sor
          </button>
        </form>
        {isTalking && (
          <ConversationMode
            audio={audioQueue()}
            lastTurn={turns.at(-1) ?? null}
            takeGreeting={takeGreeting}
            playWaiting={playWaitingPhrase}
            onAsk={(question, signal, onAudio, onSearching) =>
              ask(question, null, {
                context: latestContext.current,
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
      {source !== null && <SourcePanel citation={source} onClose={() => setSource(null)} />}
    </div>
  );
}
