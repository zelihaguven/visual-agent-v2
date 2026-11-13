// Belge grupları: yalnız dosya uzantısına bakar, belgeye özel kural yok.
// Okunur ad sunucuda üretilir (apps/api/display_names.py); burada ad dönüştürülmez.

export const GROUP_ORDER = ["PDF", "Word", "Excel", "Markdown", "SQL", "Görsel", "Diğer"] as const;

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

/** Gruplar sabit sırada; boş grup yok. */
export function groupDocuments<T extends { filename: string }>(
  documents: T[],
): { group: DocumentGroup; documents: T[] }[] {
  return GROUP_ORDER.map((group) => ({
    group,
    documents: documents.filter((document) => groupOf(document.filename) === group),
  })).filter((entry) => entry.documents.length > 0);
}
