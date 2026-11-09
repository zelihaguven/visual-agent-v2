import { useRef, useState, type FormEvent } from "react";

import { askQuestion, type Citation, type ConversationContext } from "./api";
import "./App.css";
import { ContextBar } from "./components/ContextBar";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { MicButton } from "./components/MicButton";
import { SourcePanel } from "./components/SourcePanel";
import { TurnView } from "./components/TurnView";
import { AudioQueue } from "./speech";
import { applyEvent, newTurn, type Turn } from "./turn";

const ASK_FAILED = "Cevap alınamadı. Bağlantınızı kontrol edip yeniden deneyin.";

export function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [draft, setDraft] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [source, setSource] = useState<Citation | null>(null);
  const [context, setContext] = useState<ConversationContext | null>(null);
  const [speaks, setSpeaks] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const nextId = useRef(0);
  const audio = useRef<AudioQueue | null>(null);
  const draftInput = useRef<HTMLInputElement>(null);

  function audioQueue(): AudioQueue {
    audio.current ??= new AudioQueue();
    return audio.current;
  }

  async function ask(
    question: string,
    docIds: string[] | null,
    turnContext: ConversationContext | null,
  ) {
    nextId.current += 1;
    const id = String(nextId.current);
    const updateTurn = (change: (turn: Turn) => Turn) =>
      setTurns((current) => current.map((turn) => (turn.id === id ? change(turn) : turn)));
    setTurns((current) => [...current, newTurn(id, question, docIds)]);
    setIsAsking(true);
    if (speaks) {
      audioQueue().stop();
      audioQueue().unlock();
    }
    try {
      await askQuestion(question, docIds, turnContext, speaks, (event) => {
        updateTurn((turn) => applyEvent(turn, event));
        if (event.type === "item_audio") {
          audioQueue().enqueue(event.audio, event.mime);
        }
        if (event.type === "done") {
          setContext(event.context);
        }
      });
    } catch {
      updateTurn((turn) => applyEvent(turn, { type: "error", message: ASK_FAILED }));
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
      void ask(question, null, context);
    }
  }

  function toggleSpeech() {
    if (speaks) {
      audioQueue().stop();
    }
    setSpeaks(!speaks);
  }

  function handleTranscript(text: string) {
    setVoiceError(null);
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
              onAskAgain={(question, docIds) => void ask(question, docIds, null)}
            />
          ))}
        </div>
        {context !== null && <ContextBar context={context} onClear={() => setContext(null)} />}
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
            onChange={(event) => setDraft(event.target.value)}
          />
          <MicButton isDisabled={isAsking} onTranscript={handleTranscript} onError={setVoiceError} />
          <button
            type="button"
            className={`icon-button ${speaks ? "is-active" : ""}`}
            aria-label="Sesli cevap"
            title="Sesli cevap"
            aria-pressed={speaks}
            onClick={toggleSpeech}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path
                fill="currentColor"
                d="M3 9v6h4l5 5V4L7 9H3Zm13.5 3A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4Zm-2.5-9v2a7 7 0 0 1 0 14v2a9 9 0 0 0 0-18Z"
              />
            </svg>
          </button>
          <button type="submit" disabled={isAsking || draft.trim() === ""}>
            Sor
          </button>
        </form>
      </main>
      {source !== null && <SourcePanel citation={source} onClose={() => setSource(null)} />}
    </div>
  );
}
