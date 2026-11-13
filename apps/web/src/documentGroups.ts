// Belge grupları ve okunur adlar: yalnız dosya adına bakar, belgeye özel kural yok.

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

/**
 * Ad dosya adına benziyorsa (boşluk yok) uzantı atılır, "-" ve "_" boşluk olur.
 * Boşluklu adlara dokunulmaz: "PNT-1126 ölçü föyü" gibi koddaki tire korunur.
 */
export function readableName(title: string): string {
  const trimmed = title.trim();
  if (/\s/.test(trimmed)) {
    return trimmed;
  }
  return trimmed.replace(EXTENSION_RE, "").replace(/[-_]+/g, " ").trim() || trimmed;
}
