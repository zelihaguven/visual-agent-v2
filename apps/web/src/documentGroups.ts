// Belge grupları: sunucunun verdiği konu, konu yoksa dosya uzantısı. Belgeye özel kural yok.
// Okunur ad sunucuda üretilir (apps/api/display_names.py); burada ad dönüştürülmez.

export const GROUP_ORDER = [
  "PDF",
  "Word",
  "Excel",
  "Markdown",
  "SQL",
  "Görsel",
  "Diğer",
] as const;

export type DocumentGroup = (typeof GROUP_ORDER)[number];

const GROUP_BY_EXTENSION: Record<string, DocumentGroup> = {
  pdf: "PDF",
  doc: "Word",
  docx: "Word",
  odt: "Word",
  rtf: "Word",
  xls: "Excel",
  xlsx: "Excel",
  md: "Markdown",
  sql: "SQL",
  jpg: "Görsel",
  jpeg: "Görsel",
  png: "Görsel",
  tif: "Görsel",
  tiff: "Görsel",
};

const EXTENSION_RE = /\.([a-z0-9]{1,5})$/i;

export function groupOf(filename: string): DocumentGroup {
  const extension = EXTENSION_RE.exec(filename)?.[1]?.toLowerCase();
  return (extension && GROUP_BY_EXTENSION[extension]) || "Diğer";
}

const TOPIC_COLLATOR = new Intl.Collator("tr");

/**
 * Konusu verilmiş belgeler konusuna göre (sunucuda model belirler, alfabetik), henüz konusu
 * olmayanlar dosya türüne göre (sabit sırada) gruplanır. Boş grup yok.
 */
export function groupDocuments<
  T extends { filename: string; topic?: string | null },
>(documents: T[]): { group: string; documents: T[] }[] {
  const topics = [
    ...new Set(
      documents.flatMap((document) => (document.topic ? [document.topic] : [])),
    ),
  ]
    .sort(TOPIC_COLLATOR.compare)
    .map((topic) => ({
      group: topic,
      documents: documents.filter((document) => document.topic === topic),
    }));
  const untopiced = documents.filter((document) => !document.topic);
  const byType = GROUP_ORDER.map((group) => ({
    group: group as string,
    documents: untopiced.filter(
      (document) => groupOf(document.filename) === group,
    ),
  })).filter((entry) => entry.documents.length > 0);
  return [...topics, ...byType];
}
