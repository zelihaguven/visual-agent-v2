import type { AskResult, Citation, DocumentChoice, SpokenItem } from "../api";
import type { Turn, TurnItem } from "../turn";
import { CitationList } from "./Citations";
import { FinalAnswer, HiddenText, type SpeechStatus } from "./FinalAnswer";
import { Icon } from "./Icon";

export { citationDetail, citationLabel, citationLocation } from "./Citations";
export {
  SOURCE_LINE_SPOKEN,
  SOURCE_QUOTE_LABEL,
  unverifiedText,
  type SpeechStatus,
} from "./FinalAnswer";

const STAGE_LABELS: Record<string, string> = {
  context: "Soru tamamlanıyor",
  scope: "Belgeler belirleniyor",
  intent: "Hazırlanıyor",
  retrieve: "Kaynaklar aranıyor",
  generate: "Cevap yazılıyor",
  verify: "Kaynakla kontrol ediliyor",
};

type Props = {
  turn: Turn;
  speechStatus?: SpeechStatus;
  onSpeak?: (items: SpokenItem[]) => void;
  onOpenSource: (citation: Citation) => void;
  /** allDocuments: "Tüm Belgelerde Ara"; sorudaki kod aramayı daraltmaz. */
  onAskAgain: (question: string, docIds: string[] | null, allDocuments?: boolean) => void;
  /** Bir soru sürerken yeniden sorma düğmeleri kilitlenir; eski turlardakiler dahil. */
  isBusy?: boolean;
  /** Yalnız son tur ekran okuyucuya duyurulur; eski turlar sessizdir. */
  isLatest?: boolean;
};

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
            {item.state === "unverified" && (
              <HiddenText quote={item.quote} hasSources={citations.length > 0} />
            )}
            {item.state !== "streaming" && (
              <CitationList citations={citations} onOpenSource={onOpenSource} />
            )}
          </li>
        );
      })}
    </ol>
  );
}

function InventoryView({ result }: { result: Extract<AskResult, { kind: "inventory" }> }) {
  return (
    <div className="result-block inventory">
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
    <ul className="choices">
      {choices.map((choice) => (
        <li key={choice.doc_id}>
          <button
            type="button"
            className="choice"
            disabled={isBusy}
            onClick={() => onChoose(choice.doc_id)}
          >
            {choice.label}
          </button>
        </li>
      ))}
    </ul>
  );
}

function notFoundText(turn: Turn): string {
  if (turn.scopeInherited) {
    return "Bu bilgi bu belgede yok.";
  }
  return turn.scopeNarrowed
    ? "Bu bilgi bu kodun geçtiği belgelerde yok."
    : "Bu bilgi belgelerde bulunamadı.";
}

function ResultView({ turn, onOpenSource, onAskAgain, speechStatus, onSpeak, isBusy = false }: Props) {
  const { result } = turn;
  const fullQuestion = turn.resolvedQuestion ?? turn.question;
  const chooseDocument = (docId: string) => onAskAgain(fullQuestion, [docId]);
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
        <div className="result-block clarify">
          <p className="clarify-question">{result.question}</p>
          <DocumentChoices choices={result.options} isBusy={isBusy} onChoose={chooseDocument} />
        </div>
      );
    case "not_found":
      return (
        <div className="result-block">
          <p className="notice">{notFoundText(turn)}</p>
          <p className="muted">
            {result.reason || "Soruyu başka sözcüklerle sorarsanız yeniden bakarım."}
          </p>
          <DocumentChoices
            choices={result.suggestions}
            isBusy={isBusy}
            onChoose={chooseDocument}
          />
          {(turn.scopeInherited || turn.scopeNarrowed) && (
            <div className="choices">
              <button
                type="button"
                className="choice"
                disabled={isBusy}
                onClick={() => onAskAgain(fullQuestion, null, true)}
              >
                <Icon name="search" />
                Tüm Belgelerde Ara
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
        <div className="result-block">
          <p className="notice is-bad">{result.reason}</p>
          <CitationList citations={result.citations} onOpenSource={onOpenSource} />
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
      <h2 className="question">{turn.question}</h2>
      {isRephrased(turn) && <p className="resolved">Anlaşılan soru: {turn.resolvedQuestion}</p>}
      <div className="answer" aria-live={props.isLatest ? "polite" : undefined}>
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
