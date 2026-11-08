import type { AskResult, Citation } from "../api";
import type { Turn, TurnItem } from "../turn";

const STAGE_LABELS: Record<string, string> = {
  scope: "Belgeler belirleniyor",
  retrieve: "Kaynaklar aranıyor",
  generate: "Cevap yazılıyor",
  verify: "Kaynakla kontrol ediliyor",
};

const BADGES = {
  verified: { label: "Doğrulandı", tone: "ok" },
  partial: { label: "Kısmen doğrulandı", tone: "warn" },
  failed: { label: "Doğrulanamadı", tone: "bad" },
} as const;

type Props = {
  turn: Turn;
  onOpenSource: (citation: Citation) => void;
  onAskAgain: (question: string, docIds: string[]) => void;
};

export function citationLabel(citation: Citation): string {
  const { title, location } = citation;
  if (location.sheet !== null) {
    return `${title} · ${location.sheet} · satır ${location.row ?? "?"}`;
  }
  return location.page !== null ? `${title} · s.${location.page}` : title;
}

function MaskedText({ text }: { text: string }) {
  return (
    <>
      {text.split(/(▒▒▒)/).map((part, index) =>
        part === "▒▒▒" ? (
          <span key={index} className="value-mask" aria-label="doğrulanıyor" />
        ) : (
          part
        ),
      )}
    </>
  );
}

function CitationButtons({
  citations,
  onOpenSource,
}: {
  citations: Citation[];
  onOpenSource: Props["onOpenSource"];
}) {
  return (
    <span className="citations">
      {citations.map((citation) => (
        <button
          key={citation.chunk_id}
          type="button"
          className="citation"
          onClick={() => onOpenSource(citation)}
        >
          {citationLabel(citation)}
        </button>
      ))}
    </span>
  );
}

function StreamedItems({
  turn,
  onOpenSource,
}: {
  turn: Turn;
  onOpenSource: Props["onOpenSource"];
}) {
  const indexes = Object.keys(turn.items)
    .map(Number)
    .sort((left, right) => left - right);
  const citationsOf = (item: TurnItem) =>
    item.sourceNumbers.flatMap((number) => turn.sources[number - 1] ?? []);
  return (
    <ol className="answer-items">
      {indexes.map((index) => {
        const item = turn.items[index];
        return (
          <li key={index} className={`answer-item is-${item.state}`}>
            {item.state === "streaming" ? <MaskedText text={item.text} /> : item.text}
            {item.state !== "streaming" && (
              <CitationButtons citations={citationsOf(item)} onOpenSource={onOpenSource} />
            )}
          </li>
        );
      })}
    </ol>
  );
}

function FinalAnswer({
  result,
  onOpenSource,
}: {
  result: Extract<AskResult, { kind: "answered" }>;
  onOpenSource: Props["onOpenSource"];
}) {
  const badge = BADGES[result.status];
  return (
    <>
      <span className={`badge is-${badge.tone}`}>{badge.label}</span>
      {result.has_conflict && <p className="notice">Kaynaklar birbiriyle çelişiyor.</p>}
      <ol className="answer-items">
        {result.items.map((item, index) => (
          <li key={index} className={`answer-item ${item.verified ? "is-verified" : "is-unverified"}`}>
            {item.verified ? item.text : "Değer doğrulanamadı, kaynağa bakın."}
            {item.code !== null && (
              <pre className="code-block">
                <code>{item.code}</code>
              </pre>
            )}
            <CitationButtons citations={item.citations} onOpenSource={onOpenSource} />
          </li>
        ))}
      </ol>
    </>
  );
}

function ResultView({ turn, onOpenSource, onAskAgain }: Props) {
  const { result } = turn;
  if (result === null) {
    return <StreamedItems turn={turn} onOpenSource={onOpenSource} />;
  }
  switch (result.kind) {
    case "answered":
      return <FinalAnswer result={result} onOpenSource={onOpenSource} />;
    case "clarify":
      return (
        <div className="clarify">
          <p>{result.question}</p>
          <div className="choices">
            {result.options.map((option) => (
              <button
                key={option.doc_id}
                type="button"
                className="choice"
                onClick={() => onAskAgain(turn.question, [option.doc_id])}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      );
    case "not_found":
      return (
        <div>
          <p className="notice">Bu bilgi belgelerde bulunamadı.</p>
          {result.reason && <p className="muted">{result.reason}</p>}
        </div>
      );
    case "failed":
      return (
        <div>
          <p className="notice is-bad">{result.reason}</p>
          <CitationButtons citations={result.citations} onOpenSource={onOpenSource} />
        </div>
      );
  }
}

export function TurnView(props: Props) {
  const { turn } = props;
  return (
    <article className="turn">
      <p className="question">{turn.question}</p>
      <div className="answer" aria-live="polite">
        {turn.stage !== null && (
          <p className="stage">{STAGE_LABELS[turn.stage] ?? "Hazırlanıyor"}</p>
        )}
        {turn.error !== null ? (
          <p className="notice is-bad" role="alert">
            {turn.error}
          </p>
        ) : (
          <ResultView {...props} />
        )}
        {turn.notice !== null && <p className="notice">{turn.notice}</p>}
      </div>
    </article>
  );
}
