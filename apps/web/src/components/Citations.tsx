import type { Citation } from "../api";

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

export type OpenSource = (citation: Citation) => void;

/** Kaynak düğmeleri; kaynak yoksa boş liste okunmasın diye hiç çizilmez. */
export function CitationList({
  citations,
  onOpenSource,
}: {
  citations: Citation[];
  onOpenSource: OpenSource;
}) {
  if (citations.length === 0) {
    return null;
  }
  return (
    <ul className="citations" aria-label="Kaynaklar">
      {citations.map((citation) => (
        <li key={citation.chunk_id}>
          <button
            type="button"
            className="citation"
            title={citationDetail(citation)}
            onClick={() => onOpenSource(citation)}
          >
            <span className="citation-label">{citationLabel(citation)}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
