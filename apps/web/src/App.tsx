import { useRef, useState, type FormEvent } from "react";

import { askQuestion, type Citation } from "./api";
import "./App.css";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { SourcePanel } from "./components/SourcePanel";
import { TurnView } from "./components/TurnView";
import { applyEvent, newTurn, type Turn } from "./turn";

const ASK_FAILED = "Cevap alınamadı. Bağlantınızı kontrol edip yeniden deneyin.";

export function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [draft, setDraft] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [source, setSource] = useState<Citation | null>(null);
  const nextId = useRef(0);

  async function ask(question: string, docIds: string[] | null) {
    nextId.current += 1;
    const id = String(nextId.current);
    const updateTurn = (change: (turn: Turn) => Turn) =>
      setTurns((current) => current.map((turn) => (turn.id === id ? change(turn) : turn)));
    setTurns((current) => [...current, newTurn(id, question, docIds)]);
    setIsAsking(true);
    try {
      await askQuestion(question, docIds, (event) => {
        updateTurn((turn) => applyEvent(turn, event));
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
      void ask(question, null);
    }
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
              onAskAgain={(question, docIds) => void ask(question, docIds)}
            />
          ))}
        </div>
        <form className="composer" onSubmit={handleSubmit}>
          <label htmlFor="question" className="visually-hidden">
            Sorunuz
          </label>
          <input
            id="question"
            value={draft}
            maxLength={2000}
            autoComplete="off"
            placeholder="Sorunuzu yazın"
            onChange={(event) => setDraft(event.target.value)}
          />
          <button type="submit" disabled={isAsking || draft.trim() === ""}>
            Sor
          </button>
        </form>
      </main>
      {source !== null && <SourcePanel citation={source} onClose={() => setSource(null)} />}
    </div>
  );
}
