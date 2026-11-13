import type { AskResult, Citation, DocumentChoice, SpokenItem } from "../api";
import type { Turn, TurnItem } from "../turn";

const STAGE_LABELS: Record<string, string> = {
  context: "Soru tamamlanıyor",
  scope: "Belgeler belirleniyor",
  intent: "Hazırlanıyor",
  retrieve: "Kaynaklar aranıyor",
  generate: "Cevap yazılıyor",
  verify: "Kaynakla kontrol ediliyor",
};

const BADGES = {
  verified: { label: "Doğrulandı", tone: "ok" },
  partial: { label: "Kısmen doğrulandı", tone: "warn" },
  failed: { label: "Doğrulanamadı", tone: "bad" },
} as const;

export type SpeechStatus = "idle" | "loading" | "playing";

const SPEECH_LABELS: Record<SpeechStatus, string> = {
  idle: "Cevabı seslendir",
  loading: "Ses hazırlanıyor",
  playing: "Seslendirmeyi durdur",
};

type Props = {
  turn: Turn;
  speechStatus?: SpeechStatus;
  onSpeak?: (items: SpokenItem[]) => void;
  onOpenSource: (citation: Citation) => void;
  onAskAgain: (question: string, docIds: string[] | null) => void;
  /** Bir soru sürerken yeniden sorma düğmeleri kilitlenir; eski turlardakiler dahil. */
  isBusy?: boolean;
};

const UNVERIFIED_TEXT = "Bu cümle kaynakla doğrulanamadığı için gösterilmiyor.";

export function unverifiedText(hasSources: boolean): string {
  return hasSources ? `${UNVERIFIED_TEXT} Kaynağa bakın.` : UNVERIFIED_TEXT;
}

/** Alıntı birden çok bedenin değerini taşıyabilir; sesle okunmaz, ekranda olduğu söylenir. */
export const SOURCE_LINE_SPOKEN = "Kaynaktaki satır ekranda gösteriliyor.";

/** Cümle yalnız kaynakta yazmayan birim yüzünden gizlendiyse kaynağın kendi yazdığı gösterilir. */
export function sourceQuoteText(quote: string): string {
  return `Kaynakta yazan: "${quote}"`;
}

function hiddenText(quote: string | null | undefined, hasSources: boolean): string {
  return quote ? sourceQuoteText(quote) : unverifiedText(hasSources);
}

const SECTION_SEPARATOR = " · ";

/** Kaynağın belgedeki yeri; bölüm yolu belgenin adıyla başlıyorsa ad tekrarlanmaz. */
export function citationLocation(citation: Citation): string {
  const { title, location } = citation;
  if (location.sheet !== null) {
    return `${location.sheet} · satır ${location.row ?? "?"}`;
  }
  if (location.page !== null) {
    return `Sayfa ${location.page}`;
  }
  const parts = location.section ? location.section.split(SECTION_SEPARATOR) : [];
  return (parts[0] === title ? parts.slice(1) : parts).join(SECTION_SEPARATOR);
}

/** Cevabın altındaki kısa etiket: okunur ad (sunucudan) ve sayfa ya da satır. Ayrıntı panelde. */
export function citationLabel(citation: Citation): string {
  const { title, location } = citation;
  if (location.sheet !== null) {
    return `${title} · satır ${location.row ?? "?"}`;
  }
  if (location.page !== null) {
    return `${title} · s.${location.page}`;
  }
  return title;
}

/** Tam ad ve yer: ipucu metni ve kaynak paneli için. */
export function citationDetail(citation: Citation): string {
  const where = citationLocation(citation);
  return where ? `${citation.title} · ${where}` : citation.title;
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
          title={citationDetail(citation)}
          onClick={() => onOpenSource(citation)}
        >
          <span className="citation-label">{citationLabel(citation)}</span>
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
        const citations = citationsOf(item);
        return (
          <li key={index} className={`answer-item is-${item.state}`}>
            {item.state === "streaming" && <MaskedText text={item.text} />}
            {item.state === "verified" && item.text}
            {item.state === "unverified" && hiddenText(item.quote, citations.length > 0)}
            {item.state !== "streaming" && (
              <CitationButtons citations={citations} onOpenSource={onOpenSource} />
            )}
          </li>
        );
      })}
    </ol>
  );
}

function SpeakButton({
  status,
  onClick,
}: {
  status: SpeechStatus;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={`speak-button is-${status}`}
      aria-label={SPEECH_LABELS[status]}
      title={SPEECH_LABELS[status]}
      aria-pressed={status === "playing"}
      disabled={status === "loading"}
      onClick={onClick}
    >
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
        <path
          fill="currentColor"
          d="M3 9v6h4l5 5V4L7 9H3Zm13.5 3A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4Zm-2.5-9v2a7 7 0 0 1 0 14v2a9 9 0 0 0 0-18Z"
        />
      </svg>
    </button>
  );
}

function FinalAnswer({
  result,
  onOpenSource,
  speechStatus = "idle",
  onSpeak,
}: {
  result: Extract<AskResult, { kind: "answered" }>;
  onOpenSource: Props["onOpenSource"];
  speechStatus?: SpeechStatus;
  onSpeak?: Props["onSpeak"];
}) {
  const badge = BADGES[result.status];
  const spoken = result.items.flatMap((item) => {
    if (item.verified) {
      return [{ text: item.text, has_code: item.code !== null }];
    }
    return item.source_quote ? [{ text: SOURCE_LINE_SPOKEN, has_code: false }] : [];
  });
  return (
    <>
      <div className="answer-head">
        <span className={`badge is-${badge.tone}`}>{badge.label}</span>
        {onSpeak && spoken.length > 0 && (
          <SpeakButton status={speechStatus} onClick={() => onSpeak(spoken)} />
        )}
      </div>
      {result.has_conflict && <p className="notice">Kaynaklar birbiriyle çelişiyor.</p>}
      <ol className="answer-items">
        {result.items.map((item, index) => (
          <li key={index} className={`answer-item ${item.verified ? "is-verified" : "is-unverified"}`}>
            {!item.verified && hiddenText(item.source_quote, item.citations.length > 0)}
            {item.verified && item.text.trim() !== item.code?.trim() && item.text}
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

function InventoryView({ result }: { result: Extract<AskResult, { kind: "inventory" }> }) {
  return (
    <div className="inventory">
      <p className="inventory-total">
        {result.document_count} belge, {result.code_count} kod
      </p>
      {result.documents.length === 0 && result.document_count > 0 && (
        <p className="muted">Bir konu ya da belge adı yazarsanız ona göre ararım.</p>
      )}
      <ul>
        {result.documents.map((document) => (
          <li key={document.doc_id}>
            <strong>{document.title}</strong>
            {document.codes.length > 0 && (
              <p className="inventory-codes">
                {document.codes.join(", ")}
                {document.code_count > document.codes.length &&
                  ` ve ${document.code_count - document.codes.length} kod daha`}
              </p>
            )}
          </li>
        ))}
      </ul>
      {result.documents.length > 0 && <p className="muted">Hangisini soruyorsunuz?</p>}
    </div>
  );
}

function DocumentChoices({
  choices,
  isBusy,
  onChoose,
}: {
  choices: DocumentChoice[];
  isBusy: boolean;
  onChoose: (docId: string) => void;
}) {
  if (choices.length === 0) {
    return null;
  }
  return (
    <div className="choices">
      {choices.map((choice) => (
        <button
          key={choice.doc_id}
          type="button"
          className="choice"
          disabled={isBusy}
          onClick={() => onChoose(choice.doc_id)}
        >
          {choice.label}
        </button>
      ))}
    </div>
  );
}

function ResultView({ turn, onOpenSource, onAskAgain, speechStatus, onSpeak, isBusy = false }: Props) {
  const { result } = turn;
  const fullQuestion = turn.resolvedQuestion ?? turn.question;
  if (result === null) {
    return <StreamedItems turn={turn} onOpenSource={onOpenSource} />;
  }
  switch (result.kind) {
    case "answered":
      return (
        <FinalAnswer
          result={result}
          onOpenSource={onOpenSource}
          speechStatus={speechStatus}
          onSpeak={onSpeak}
        />
      );
    case "clarify":
      return (
        <div className="clarify">
          <p>{result.question}</p>
          <DocumentChoices
            choices={result.options}
            isBusy={isBusy}
            onChoose={(docId) => onAskAgain(fullQuestion, [docId])}
          />
        </div>
      );
    case "not_found":
      return (
        <div>
          <p className="notice">
            {turn.scopeInherited ? "Bu bilgi bu belgede yok." : "Bu bilgi belgelerde bulunamadı."}
          </p>
          {result.reason ? (
            <p className="muted">{result.reason}</p>
          ) : (
            <p className="muted">Soruyu başka sözcüklerle sorarsanız yeniden bakarım.</p>
          )}
          <DocumentChoices
            choices={result.suggestions}
            isBusy={isBusy}
            onChoose={(docId) => onAskAgain(fullQuestion, [docId])}
          />
          {turn.scopeInherited && (
            <div className="choices">
              <button
                type="button"
                className="choice"
                disabled={isBusy}
                onClick={() => onAskAgain(fullQuestion, null)}
              >
                Tüm belgelerde ara
              </button>
            </div>
          )}
        </div>
      );
    case "small_talk":
      return <p className="small-talk">{result.text}</p>;
    case "inventory":
      return <InventoryView result={result} />;
    case "failed":
      return (
        <div>
          <p className="notice is-bad">{result.reason}</p>
          <CitationButtons citations={result.citations} onOpenSource={onOpenSource} />
        </div>
      );
  }
}

/** "Anlaşılan soru" yalnız yazılandan farklıysa gösterilir. */
function isRephrased(turn: Turn): boolean {
  const resolved = turn.resolvedQuestion?.trim();
  return Boolean(resolved) && resolved !== turn.question.trim();
}

export function TurnView(props: Props) {
  const { turn } = props;
  return (
    <article className="turn">
      <p className="question">{turn.question}</p>
      {isRephrased(turn) && <p className="resolved">Anlaşılan soru: {turn.resolvedQuestion}</p>}
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
