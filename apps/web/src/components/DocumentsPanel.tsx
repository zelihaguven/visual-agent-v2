import { useCallback, useEffect, useState, type ChangeEvent } from "react";

import {
  deleteDocument,
  listDocuments,
  reprocessDocument,
  uploadDocument,
  type DocumentInfo,
  type DocumentReport,
} from "../api";
import { groupDocuments, readableName, type DocumentGroup } from "../documentGroups";
import { ACCEPTED_TYPES, MAX_UPLOAD_BYTES, uploadLimitMessage } from "../limits";

const POLL_MILLISECONDS = 3000;
// Bekleyen belge yokken de seyrek bakılır: başka sekmeden ya da komutla yüklenen belge görünür.
const IDLE_POLL_MILLISECONDS = 30000;
// Hazır belgede etiket yok; yalnız dikkat isteyen durumlar etiketlenir.
const STATUS_LABELS: Record<DocumentInfo["status"], string | null> = {
  queued: "Kuyrukta",
  processing: "İşleniyor",
  ready: null,
  failed: "Hata",
};
// Bu kadar ya da daha az belgeli grup açık başlar; kalabalık grup başlığıyla gelir.
const OPEN_GROUP_LIMIT = 10;

function isPending(document: DocumentInfo): boolean {
  return document.status === "queued" || document.status === "processing";
}

function needsAttention(document: DocumentInfo): boolean {
  return document.status !== "ready" || document.outdated === true;
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

type Props = {
  onClose: () => void;
  onCountChange?: (count: number) => void;
};

export function DocumentsPanel({ onClose, onCountChange }: Props) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [toggled, setToggled] = useState<Partial<Record<DocumentGroup, boolean>>>({});

  useEffect(() => {
    onCountChange?.(documents.length);
  }, [documents.length, onCountChange]);

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

  function isOpen(group: DocumentGroup, members: DocumentInfo[]): boolean {
    return toggled[group] ?? (members.length <= OPEN_GROUP_LIMIT || members.some(needsAttention));
  }

  return (
    <div className="documents">
      <header className="drawer-header">
        <h2 id="documents-heading">Belgeler</h2>
        <button type="button" className="ghost" onClick={onClose}>
          Kapat
        </button>
      </header>
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
      <ul className="document-groups" aria-label="Belgeler">
        {groupDocuments(documents).map(({ group, documents: members }) => {
          const open = isOpen(group, members);
          return (
            <li key={group} className="document-group">
              <button
                type="button"
                className="group-toggle"
                aria-label={`${group} (${members.length})`}
                aria-expanded={open}
                onClick={() => setToggled((current) => ({ ...current, [group]: !open }))}
              >
                <span>{group}</span>
                <span className="group-count">{members.length}</span>
              </button>
              <ul className="document-list" aria-label={group} hidden={!open}>
                {members.map((document) => (
                  <DocumentRow
                    key={document.doc_id}
                    document={document}
                    isBusy={busyId !== null}
                    onReprocess={() => void runAction(document, reprocessDocument)}
                    onDelete={() => handleDelete(document)}
                  />
                ))}
              </ul>
            </li>
          );
        })}
      </ul>
      {documents.length === 0 && listError === null && (
        <p className="muted">Soru sormak için önce bir belge ekleyin.</p>
      )}
    </div>
  );
}

function DocumentRow({
  document,
  isBusy,
  onReprocess,
  onDelete,
}: {
  document: DocumentInfo;
  isBusy: boolean;
  onReprocess: () => void;
  onDelete: () => void;
}) {
  const status = STATUS_LABELS[document.status];
  return (
    <li className="document">
      <span className="document-title" title={document.filename}>
        {readableName(document.title)}
      </span>
      {status !== null && <span className={`status is-${document.status}`}>{status}</span>}
      {document.outdated === true && <span className="status is-outdated">Eski kural</span>}
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
            disabled={isBusy}
            onClick={onReprocess}
          >
            Yeniden işle
          </button>
        )}
        <button
          type="button"
          className="is-danger"
          aria-label={`${document.title} belgesini sil`}
          disabled={isBusy}
          onClick={onDelete}
        >
          Sil
        </button>
      </div>
    </li>
  );
}
