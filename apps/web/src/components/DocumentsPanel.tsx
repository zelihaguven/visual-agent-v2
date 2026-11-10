import { useCallback, useEffect, useState, type ChangeEvent } from "react";

import { listDocuments, uploadDocument, type DocumentInfo, type DocumentReport } from "../api";

const POLL_MILLISECONDS = 3000;
const ACCEPTED_TYPES = ".pdf,.docx,.doc,.pptx,.ppt,.odt,.rtf,.xlsx,.xls,.jpg,.jpeg,.png,.tif,.tiff,.sql,.txt,.md";
const STATUS_LABELS: Record<DocumentInfo["status"], string> = {
  queued: "Sırada",
  processing: "İşleniyor",
  ready: "Hazır",
  failed: "İşlenemedi",
};

function isPending(document: DocumentInfo): boolean {
  return document.status === "queued" || document.status === "processing";
}

function DocumentNotes({ title, report }: { title: string; report: DocumentReport }) {
  if (report.warnings.length === 0 && report.uncertain_values === 0) {
    return null;
  }
  return (
    <ul className="document-notes" aria-label={`${title} uyarıları`}>
      {report.warnings.map((warning, index) => (
        <li key={`${index}-${warning}`}>{warning}</li>
      ))}
      {report.uncertain_values > 0 && (
        <li>
          {report.uncertain_values} değer net okunamadı; cevapta gizlenir. Gerekirse belgeden kontrol
          edin.
        </li>
      )}
    </ul>
  );
}

export function DocumentsPanel() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    try {
      setDocuments(await listDocuments(signal));
    } catch {
      if (!signal?.aborted) {
        setError("Belge listesi alınamadı.");
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void refresh(controller.signal);
    return () => controller.abort();
  }, [refresh]);

  const hasPending = documents.some(isPending);
  useEffect(() => {
    if (!hasPending) {
      return;
    }
    const timer = setInterval(() => void refresh(), POLL_MILLISECONDS);
    return () => clearInterval(timer);
  }, [hasPending, refresh]);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setError(null);
    setIsUploading(true);
    try {
      await uploadDocument(file);
      await refresh();
    } catch (uploadError: unknown) {
      setError(uploadError instanceof Error ? uploadError.message : "Belge yüklenemedi.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="documents" aria-labelledby="documents-heading">
      <h2 id="documents-heading">Belgeler</h2>
      <label className={`upload ${isUploading ? "is-busy" : ""}`}>
        <span>{isUploading ? "Yükleniyor" : "Belge ekle"}</span>
        <input
          type="file"
          accept={ACCEPTED_TYPES}
          aria-label="Belge yükle"
          disabled={isUploading}
          onChange={(event) => void handleFile(event)}
        />
      </label>
      {error !== null && (
        <p className="notice is-bad" role="alert">
          {error}
        </p>
      )}
      <ul className="document-list" aria-label="Belgeler">
        {documents.map((document) => (
          <li key={document.doc_id} className="document">
            <span className="document-title">{document.title}</span>
            <span className={`status is-${document.status}`}>{STATUS_LABELS[document.status]}</span>
            {document.error !== null && <span className="document-error">{document.error}</span>}
            {document.report !== null && (
              <DocumentNotes title={document.title} report={document.report} />
            )}
          </li>
        ))}
      </ul>
      {documents.length === 0 && error === null && (
        <p className="muted">Soru sormak için önce bir belge ekleyin.</p>
      )}
    </section>
  );
}
