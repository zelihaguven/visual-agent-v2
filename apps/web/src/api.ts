export type Location = {
  page: number | null;
  sheet: string | null;
  row: number | null;
};

export type Citation = {
  chunk_id: string;
  doc_id: string;
  title: string;
  location: Location;
};

export type AnsweredItem = {
  text: string;
  citations: Citation[];
  verified: boolean;
  from_figure: boolean;
  code: string | null;
  problems: string[];
};

export type AskResult =
  | {
      kind: "answered";
      status: "verified" | "partial" | "failed";
      items: AnsweredItem[];
      has_conflict: boolean;
      problems: string[];
    }
  | { kind: "clarify"; question: string; options: { doc_id: string; label: string }[] }
  | { kind: "not_found"; reason: string; suggested_doc_ids: string[] }
  | { kind: "failed"; reason: string; citations: Citation[] };

export type AskEvent =
  | { type: "status"; stage: string }
  | { type: "sources"; sources: Citation[] }
  | { type: "item_stream"; index: number; text: string }
  | {
      type: "item_verified";
      index: number;
      text: string;
      source_numbers: number[];
      from_figure: boolean;
    }
  | { type: "item_unverified"; index: number; message: string; source_numbers: number[] }
  | { type: "reset" }
  | { type: "incomplete"; message: string }
  | { type: "done"; result: AskResult; timings: Record<string, number> }
  | { type: "error"; message: string };

export type DocumentStatus = "queued" | "processing" | "ready" | "failed";

export type DocumentInfo = {
  doc_id: string;
  title: string;
  filename: string;
  status: DocumentStatus;
  error: string | null;
};

export type SourceView =
  | { kind: "page"; page: number; title: string; image_url: string }
  | {
      kind: "sheet";
      sheet: string;
      title: string;
      highlight_row: number;
      rows: { row: number; text: string }[];
    }
  | { kind: "text"; text: string; title: string };

const EVENT_SEPARATOR = "\n\n";
const DATA_PREFIX = "data: ";

function parseEvent(block: string): AskEvent | null {
  return block.startsWith(DATA_PREFIX)
    ? (JSON.parse(block.slice(DATA_PREFIX.length)) as AskEvent)
    : null;
}

export async function askQuestion(
  question: string,
  docIds: string[] | null,
  onEvent: (event: AskEvent) => void,
): Promise<void> {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(docIds ? { question, doc_ids: docIds } : { question }),
  });
  if (!response.ok || response.body === null) {
    throw new Error(`Soru gönderilemedi: ${response.status}`);
  }
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) {
      return;
    }
    buffer += value;
    const blocks = buffer.split(EVENT_SEPARATOR);
    buffer = blocks.pop() ?? "";
    for (const block of blocks) {
      const event = parseEvent(block);
      if (event !== null) {
        onEvent(event);
      }
    }
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    return typeof body.detail === "string" ? body.detail : "İşlem tamamlanamadı.";
  } catch {
    return "İşlem tamamlanamadı.";
  }
}

export async function listDocuments(signal?: AbortSignal): Promise<DocumentInfo[]> {
  const response = await fetch("/api/documents", { signal });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as DocumentInfo[];
}

export async function uploadDocument(file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch("/api/documents", { method: "POST", body: form });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
}

export async function fetchSource(chunkId: string): Promise<SourceView> {
  const response = await fetch(`/api/chunks/${encodeURIComponent(chunkId)}/source`);
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as SourceView;
}
