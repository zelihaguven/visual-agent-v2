import type { CSSProperties } from "react";

import type { AskResult, SpokenItem } from "../api";
import { CitationList, type OpenSource } from "./Citations";

/* Bitmiş cevabın gösterimi: doğrulama rozeti, büyük değer, gizlenen cümleler ve seslendirme.
   "Yanlış değer doğrulanmış gibi gösterilmez" kuralının görünüm tarafı burada toplanır. */

type AnsweredResult = Extract<AskResult, { kind: "answered" }>;
type AnsweredItem = AnsweredResult["items"][number];

const BADGES = {
  verified: { label: "Doğrulandı", tone: "ok" },
  partial: { label: "Kısmen doğrulandı", tone: "warn" },
  failed: { label: "Doğrulanamadı", tone: "bad" },
} as const;

const OCR_BADGE = { label: "Taramadan okundu · kaynaktan kontrol edin", tone: "warn" } as const;

/** Kısmi durumun tek nedeni taranmış kaynak mı (gizlenen ya da eksik cümle yok). */
function isOnlyScanned(result: AnsweredResult): boolean {
  return (
    result.status === "partial" &&
    result.problems.length === 0 &&
    result.items.every((item) => item.verified) &&
    result.items.some((item) => item.from_ocr)
  );
}

/** Kısmi durumun tek nedeni taranmış kaynaksa rozet bunu söyler; akışı yarıda kalan cevap sorun
 * taşır ve "Kısmen doğrulandı" kalır. Doğrulanamayan cevapta en az bir cümle gösterildiyse rozet
 * gizlenen cümle sayısını söyler (yalnız görünüm; durum aynı). */
function badgeFor(result: AnsweredResult) {
  if (isOnlyScanned(result)) {
    return OCR_BADGE;
  }
  const hidden = result.items.filter((item) => !item.verified).length;
  if (result.status === "failed" && hidden > 0 && hidden < result.items.length) {
    return { label: `Kısmen doğrulandı · ${hidden} cümle gizlendi`, tone: "warn" } as const;
  }
  return BADGES[result.status];
}

/** Düz sayı ("38,0", "1200"); işaretli, aralıklı, kesirli ya da ayraçlı yazım değil. */
const PLAIN_NUMBER = /^\d+(?:[.,]\d+)?$/;
/** Harfle başlayıp tire ya da alt çizgiyle bağlı kod: GML-6473, TT-100156, MUSTERI_KODU. */
const JOINED_CODE = /^\p{L}[\p{L}\d]*(?:[-_][\p{L}\d]+)+$/u;
/** Sözcüğün çevresindeki noktalama ve Türkçe ek ("94'tür", "(38,0)"). */
const WORD_EDGES = /^[("“'‘[]+|['’]\p{L}*[.,;:!?)"”\]]*$|[.,;:!?)"”\]]+$/gu;

/** Tek doğrulanmış cümlede tek düz sayı varsa büyük gösterilir. Tutucu: rakam taşıyan her sözcük
 * ya düz sayı ya kod olmalı; "1-5", "M8x1,25", "27½", "−5", "%15", "10x20" gibi bir yazım varsa
 * hiç büyük değer gösterilmez (sayının bir parçasını büyük göstermek yanlış değer olur).
 * Yalnız doğrulanmış dijital cevapta: taramadan okunan değer (iki okuyucu aynı yanlışı okuyabilir),
 * akışı yarıda kalan ya da kaynakları çelişen cevap büyümez; doğrulanmamış değer hiç büyümez. */
function headlineValue(result: AnsweredResult): string | null {
  const [only, ...rest] = result.items;
  if (result.status !== "verified" || result.has_conflict || only === undefined || rest.length > 0) {
    return null;
  }
  if (!only.verified || only.from_ocr || only.code !== null) {
    return null;
  }
  const values: string[] = [];
  for (const word of only.text.split(/\s+/)) {
    const core = word.replace(WORD_EDGES, "");
    if (!/\d/.test(word)) {
      continue;
    }
    if (PLAIN_NUMBER.test(core)) {
      values.push(core);
    } else if (!JOINED_CODE.test(core)) {
      return null;
    }
  }
  return values.length === 1 ? values[0] : null;
}

const UNVERIFIED_TEXT = "Bu cümle kaynakla doğrulanamadığı için gösterilmiyor.";

const UNVERIFIED_OCR_TEXT = "Bu değeri doğrulayamadım. Kaynağı aşağıda; değeri oradan okuyun.";

/** Taramadan okunup doğrulanamayan değerde kullanıcı kaynağa yönlendirilir. */
export function unverifiedText(hasSources: boolean, fromOcr = false): string {
  if (hasSources && fromOcr) {
    return UNVERIFIED_OCR_TEXT;
  }
  return hasSources ? `${UNVERIFIED_TEXT} Kaynağa bakın.` : UNVERIFIED_TEXT;
}

/** Alıntı birden çok bedenin değerini taşıyabilir; sesle okunmaz, ekranda olduğu söylenir. */
export const SOURCE_LINE_SPOKEN = "Kaynaktaki satır ekranda gösteriliyor.";

/** Cümle yalnız kaynakta yazmayan birim yüzünden gizlendiyse kaynağın kendi yazdığı gösterilir. */
export const SOURCE_QUOTE_LABEL = "Kaynaktaki metin";

/** Kaynak alıntısı nötr metin; gizleme mesajı uyarı rengiyle ayrılır. */
export function HiddenText({
  quote,
  hasSources,
  fromOcr = false,
}: {
  quote?: string | null;
  hasSources: boolean;
  fromOcr?: boolean;
}) {
  return quote ? (
    <span className="source-quote">
      <span className="quote-label">{SOURCE_QUOTE_LABEL}</span> <q>{quote}</q>
    </span>
  ) : (
    <span className="hidden-note">{unverifiedText(hasSources, fromOcr)}</span>
  );
}

/** Art arda gelen, aynı uyarıyı taşıyan gizli cümleler tek satırda toplanır; kaynakları birleşir. */
function mergeHidden(items: AnsweredItem[]): AnsweredItem[] {
  const merged: AnsweredItem[] = [];
  for (const item of items) {
    const last = merged.at(-1);
    const repeats =
      last !== undefined &&
      !item.verified &&
      !last.verified &&
      !item.source_quote &&
      !last.source_quote &&
      unverifiedText(item.citations.length > 0, item.from_ocr) ===
        unverifiedText(last.citations.length > 0, last.from_ocr);
    if (!repeats) {
      merged.push(item);
      continue;
    }
    const known = new Set(last.citations.map((citation) => citation.chunk_id));
    const added = item.citations.filter((citation) => !known.has(citation.chunk_id));
    merged[merged.length - 1] = { ...last, citations: [...last.citations, ...added] };
  }
  return merged;
}

/** Sesle okunacaklar: doğrulanmış cümleler; alıntının yerine yalnız ekranda olduğu söylenir. */
function spokenItems(result: AnsweredResult): SpokenItem[] {
  return result.items.flatMap((item) => {
    if (item.verified) {
      return [{ text: item.text, has_code: item.code !== null }];
    }
    return item.source_quote ? [{ text: SOURCE_LINE_SPOKEN, has_code: false }] : [];
  });
}

/** Cümle metni yalnız kod bloğunu ya da büyük değeri aynen tekrarlamıyorsa yazılır. */
function shouldShowText(item: AnsweredItem, value: string | null): boolean {
  return (
    item.verified &&
    item.text.trim() !== item.code?.trim() &&
    item.text.trim().replace(/\.$/, "") !== value
  );
}

export type SpeechStatus = "idle" | "loading" | "playing";

const SPEECH_LABELS: Record<SpeechStatus, string> = {
  idle: "Cevabı Seslendir",
  loading: "Ses hazırlanıyor",
  playing: "Seslendirmeyi Durdur",
};

function SpeakButton({ status, onClick }: { status: SpeechStatus; onClick: () => void }) {
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

export function FinalAnswer({
  result,
  onOpenSource,
  speechStatus = "idle",
  onSpeak,
}: {
  result: AnsweredResult;
  onOpenSource: OpenSource;
  speechStatus?: SpeechStatus;
  onSpeak?: (items: SpokenItem[]) => void;
}) {
  const badge = badgeFor(result);
  const value = headlineValue(result);
  const spoken = spokenItems(result);
  return (
    <>
      <div className="answer-head">
        <span className={`badge is-${badge.tone}`}>{badge.label}</span>
        {onSpeak && spoken.length > 0 && (
          <SpeakButton status={speechStatus} onClick={() => onSpeak(spoken)} />
        )}
      </div>
      {result.has_conflict && <p className="notice">Kaynaklar birbiriyle çelişiyor.</p>}
      {value !== null && (
        // Uzunluk stile gider: yazı, değerin tamamı karta sığacak kadar küçülür (turn.css).
        <p className="answer-value" style={{ "--chars": value.length } as CSSProperties}>
          {value}
        </p>
      )}
      <ol className="answer-items">
        {mergeHidden(result.items).map((item, index) => (
          <li key={index} className={`answer-item ${item.verified ? "is-verified" : "is-unverified"}`}>
            {!item.verified && (
              <HiddenText
                quote={item.source_quote}
                hasSources={item.citations.length > 0}
                fromOcr={item.from_ocr}
              />
            )}
            {shouldShowText(item, value) && item.text}
            {item.code !== null && (
              <pre className="code-block">
                <code>{item.code}</code>
              </pre>
            )}
            <CitationList citations={item.citations} onOpenSource={onOpenSource} />
          </li>
        ))}
      </ol>
    </>
  );
}
