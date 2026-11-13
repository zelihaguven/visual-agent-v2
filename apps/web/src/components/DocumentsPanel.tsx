import { useCallback, useEffect, useState, type ChangeEvent } from "react";

import {
  deleteDocument,
  listDocuments,
  reprocessDocument,
  uploadDocument,
  type DocumentInfo,
  type DocumentReport,
} from "../api";
import { ACCEPTED_TYPES, MAX_UPLOAD_BYTES, uploadLimitMessage } from "../limits";

const POLL_MILLISECONDS = 3000;
// Bekleyen belge yokken de seyrek bakılır: başka sekmeden ya da komutla yüklenen belge görünür.
const IDLE_POLL_MILLISECONDS = 30000;
const STATUS_LABELS: Record<DocumentInfo["status"], string> = {
  queued: "Sırada",
  processing: "İşleniyor",
  ready: "Hazır",
  failed: "İşlenemedi",
};

function isPending(document: DocumentInfo): boolean {
  return document.status === "queued" || document.status === "processing";
}

function confirmDeletion(title: string): boolean {
  return window.confirm(
    `"${title}" silinsin mi? Belge, parçaları ve dosyaları kalıcı olarak silinir.`,
  );
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
  const [listError, setListError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    try {
      setDocuments(await listDocuments(signal));
      setListError(null);
    } catch {
      if (!signal?.aborted) {
        setListError("Belge listesi alınamadı.");
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
    // Bir istek bitmeden sonrakine geçilmez; bileşen kapanınca bekleyen istek iptal edilir.
    const controller = new AbortController();
    const delay = hasPending ? POLL_MILLISECONDS : IDLE_POLL_MILLISECONDS;
    let timer: number | undefined;
    const poll = async () => {
      await refresh(controller.signal);
      if (!controller.signal.aborted) {
        timer = window.setTimeout(() => void poll(), delay);
      }
    };
    timer = window.setTimeout(() => void poll(), delay);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [hasPending, refresh]);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setError(uploadLimitMessage());
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

  async function runAction(document: DocumentInfo, action: (docId: string) => Promise<void>) {
    setError(null);
    setBusyId(document.doc_id);
    try {
      await action(document.doc_id);
    } catch (actionError: unknown) {
      setError(actionError instanceof Error ? actionError.message : "İşlem tamamlanamadı.");
    } finally {
      setBusyId(null);
      await refresh();
    }
  }

  function handleDelete(document: DocumentInfo) {
    if (confirmDeletion(document.title)) {
      void runAction(document, deleteDocument);
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
      {[listError, error].map(
        (message) =>
          message !== null && (
            <p key={message} className="notice is-bad" role="alert">
              {message}
            </p>
          ),
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
            {document.outdated === true && (
              <span className="document-error">
                Eski okuma kuralıyla işlendi; güncel kuralla okunması için yeniden işleyin.
              </span>
            )}
            <div className="document-actions">
              {!isPending(document) && (
                <button
                  type="button"
                  aria-label={`${document.title} belgesini yeniden işle`}
                  disabled={busyId !== null}
                  onClick={() => void runAction(document, reprocessDocument)}
                >
                  Yeniden işle
                </button>
              )}
              <button
                type="button"
                className="is-danger"
                aria-label={`${document.title} belgesini sil`}
                disabled={busyId !== null}
                onClick={() => handleDelete(document)}
              >
                Sil
              </button>
            </div>
          </li>
        ))}
      </ul>
      {documents.length === 0 && listError === null && (
        <p className="muted">Soru sormak için önce bir belge ekleyin.</p>
      )}
    </section>
  );
}
