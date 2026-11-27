import { useCallback, useEffect, useState, type ChangeEvent, type Ref } from "react";

import {
  deleteDocument,
  listDocuments,
  reprocessDocument,
  uploadDocument,
  type DocumentInfo,
  type DocumentReport,
  type ProcessingProgress,
  type ProcessingStep,
} from "../api";
import { groupDocuments } from "../documentGroups";
import { ConfirmDialog } from "./ConfirmDialog";
import { Icon } from "./Icon";
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
  // Belge bozuk değil: taranmış sayfaların okuyucusu yok; gelince "Yeniden İşle" ile okunur.
  waiting_reader: "Okuyucu bekleniyor",
};
// Bu kadar ya da daha az belgeli grup açık başlar; kalabalık grup başlığıyla gelir.
const OPEN_GROUP_LIMIT = 10;

/** Dosya adları büyük-küçük harf, baştaki/sondaki boşluk ve Unicode biçimi (NFC/NFD) farkı
 * olmadan karşılaştırılır. Türkçe ve genel küçük harf kuralının ikisi de denenir: "INVOICE" ile
 * "invoice" de, "IŞIK" ile "ışık" da aynı addır. */
function sameFileName(a: string, b: string): boolean {
  const forms = (name: string) => {
    const base = name.trim().normalize("NFC");
    return [base.toLowerCase(), base.toLocaleLowerCase("tr")];
  };
  const [left, right] = [forms(a), forms(b)];
  return left.some((form, index) => form === right[index]);
}

function isPending(document: DocumentInfo): boolean {
  return document.status === "queued" || document.status === "processing";
}

function needsAttention(document: DocumentInfo): boolean {
  return document.status !== "ready" || document.outdated === true;
}

/** Onay bekleyen işlem: ikisi de belgenin dizinini değiştirir, yanlış dokunuşla başlamamalı. */
type PendingAction = { kind: "reprocess" | "delete"; document: DocumentInfo };

const CONFIRMATIONS = {
  reprocess: {
    question: "yeniden işlensin mi?",
    body:
      "Belge baştan okunur; parçaları ve arama dizini yenilenir. Bitene kadar belge işleniyor " +
      "görünür. Taranmış belgelerde dakikalar sürebilir.",
    confirmLabel: "Yeniden İşle",
    confirmIcon: "refresh",
    action: reprocessDocument,
  },
  delete: {
    question: "silinsin mi?",
    body: "Belge, parçaları ve dosyaları kalıcı olarak silinir.",
    confirmLabel: "Sil",
    confirmIcon: "trash",
    action: deleteDocument,
  },
} as const;

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

export type DocumentSummary = { total: number; ready: number; pending: number; failed: number };

function summarize(documents: DocumentInfo[]): DocumentSummary {
  return {
    total: documents.length,
    ready: documents.filter((document) => document.status === "ready").length,
    pending: documents.filter(isPending).length,
    failed: documents.filter((document) => document.status === "failed").length,
  };
}

type Props = {
  onClose: () => void;
  onSummary?: (summary: DocumentSummary) => void;
  uploadInput?: Ref<HTMLInputElement>;
};

export function DocumentsPanel({ onClose, onSummary, uploadInput }: Props) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [toggled, setToggled] = useState<Record<string, boolean>>({});
  const [hasLoaded, setHasLoaded] = useState(false);
  const [pending, setPending] = useState<PendingAction | null>(null);
  // Yüklü bir belgeyle aynı adı taşıyan dosya: yüklemeden önce sorulur.
  const [duplicate, setDuplicate] = useState<File | null>(null);

  useEffect(() => {
    // Liste gelmeden sayı gösterilmez: "0 belge" yanlış izlenim verir.
    if (hasLoaded) {
      onSummary?.(summarize(documents));
    }
  }, [documents, hasLoaded, onSummary]);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    try {
      setDocuments(await listDocuments(signal));
      setHasLoaded(true);
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

  useEffect(() => {
    // Yükleme sürerken sayfa kapanırsa istek yarıda kalır ve belge eklenmez; işlemede uyarı yok,
    // çünkü işleme sunucuda sürer.
    if (!isUploading) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [isUploading]);

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
    if (documents.some((document) => sameFileName(document.filename, file.name))) {
      setDuplicate(file);
      return;
    }
    await upload(file);
  }

  async function upload(file: File) {
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

  function confirmPending() {
    if (pending !== null) {
      setPending(null);
      void runAction(pending.document, CONFIRMATIONS[pending.kind].action);
    }
  }

  function confirmDuplicate() {
    if (duplicate !== null) {
      setDuplicate(null);
      void upload(duplicate);
    }
  }

  function isOpen(group: string, members: DocumentInfo[]): boolean {
    return toggled[group] ?? (members.length <= OPEN_GROUP_LIMIT || members.some(needsAttention));
  }

  return (
    <div className="documents">
      <header className="drawer-header">
        <h2>Belgeler</h2>
        <button type="button" className="ghost" onClick={onClose}>
          <Icon name="close" />
          Kapat
        </button>
      </header>
      <label className={`upload ${isUploading ? "is-busy" : ""}`}>
        <span>
          {!isUploading && <Icon name="plus" />}
          {isUploading ? "Yükleniyor" : "Belge Ekle"}
        </span>
        <input
          ref={uploadInput}
          type="file"
          accept={ACCEPTED_TYPES}
          aria-label="Belge Yükle"
          // Liste gelmeden seçilen dosya aynı ad denetiminden geçemezdi.
          disabled={isUploading || (!hasLoaded && listError === null)}
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
                    onReprocess={() => setPending({ kind: "reprocess", document })}
                    onDelete={() => setPending({ kind: "delete", document })}
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
      {pending !== null && (
        <ConfirmDialog
          title={`"${pending.document.title}" ${CONFIRMATIONS[pending.kind].question}`}
          body={CONFIRMATIONS[pending.kind].body}
          confirmLabel={CONFIRMATIONS[pending.kind].confirmLabel}
          confirmIcon={CONFIRMATIONS[pending.kind].confirmIcon}
          isDanger={pending.kind === "delete"}
          onConfirm={confirmPending}
          onCancel={() => setPending(null)}
        />
      )}
      {duplicate !== null && (
        <ConfirmDialog
          title="Bu adla bir belge zaten var. Yine de eklensin mi?"
          body={`"${duplicate.name}" ayrı bir belge olarak eklenir; mevcut belge değişmez.`}
          confirmLabel="Yine de Ekle"
          confirmIcon="plus"
          onConfirm={confirmDuplicate}
          onCancel={() => setDuplicate(null)}
        />
      )}
    </div>
  );
}

const PHASES = ["Hazırlanıyor", "Okunuyor", "Parçalanıyor", "İndeksleniyor"];
const STEP_PHASE: Record<ProcessingStep, number> = {
  prepare: 0,
  pages: 1,
  text: 1,
  images: 1,
  chunks: 2,
  index: 3,
};
const STEP_DETAIL: Partial<Record<ProcessingStep, string>> = {
  pages: "Sayfa",
  text: "metin çıkarılıyor",
  images: "Görsel",
};

/** İşlemenin dört bölümü: biten dolu, sürenin içindeki sayıyla dolar; sayısı bilinmeyen adımda
 * bölüm belirsiz görünür. Yüzde bölümlerden hesaplanır, süreyi değil adımı gösterir. */
function ProcessingBar({ progress }: { progress: ProcessingProgress }) {
  const phase = STEP_PHASE[progress.step];
  const counted = progress.total > 0;
  const fraction = counted ? Math.min(progress.done / progress.total, 1) : 0;
  const percent = Math.round(((phase + fraction) / PHASES.length) * 100);
  const detail = STEP_DETAIL[progress.step];
  const count = counted ? ` ${progress.done} / ${progress.total}` : "";
  const label = detail ? `${PHASES[phase]} · ${detail}${count}` : PHASES[phase];
  return (
    <div className="document-progress">
      <div
        className="progress-track"
        role="progressbar"
        aria-label="İşleme ilerlemesi"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-valuetext={label}
      >
        {PHASES.map((name, index) => {
          const state =
            index < phase ? "is-done" : index > phase ? "" : counted ? "is-current" : "is-waiting";
          return (
            <span key={name} className={`progress-phase ${state}`}>
              <span
                className="progress-fill"
                style={state === "is-current" ? { width: `${fraction * 100}%` } : undefined}
              />
            </span>
          );
        })}
      </div>
      <span aria-hidden="true">{label}</span>
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
  const pending = isPending(document);
  // Sırada bekleyen ya da işlenen belgenin eski raporu yakında yenilenir; uyarı gösterilmez.
  const outdated = document.outdated === true && !pending;
  return (
    <li className="document">
      <span className="document-title" title={document.filename}>
        {document.title}
      </span>
      {/* Durum ve düğmeler hep başlığın hemen altında, aynı satırda ve aynı sırada durur; durum
          değişince yer değiştirmez. Kullanılamayan düğme gizlenmez, pasif görünür: yanlış düğmeye
          basılmasın. */}
      <div className="document-meta">
        <span className="document-badges">
          {status !== null && <span className={`status is-${document.status}`}>{status}</span>}
          {outdated && <span className="status is-outdated">Eski kural</span>}
        </span>
        <div className="document-actions">
          <button
            type="button"
            aria-label={`${document.title} Belgesini Yeniden İşle`}
            disabled={isBusy || pending}
            title={pending ? "Belge işlenirken yeniden işlenemez." : undefined}
            onClick={onReprocess}
          >
            <Icon name="refresh" size={15} />
            Yeniden İşle
          </button>
          <button
            type="button"
            className="is-danger"
            aria-label={`${document.title} Belgesini Sil`}
            disabled={isBusy}
            onClick={onDelete}
          >
            <Icon name="trash" size={15} />
            Sil
          </button>
        </div>
      </div>
      {document.status === "processing" && document.progress && (
        <ProcessingBar progress={document.progress} />
      )}
      {document.error !== null && <span className="document-error">{document.error}</span>}
      {document.report !== null && (
        <DocumentNotes title={document.title} report={document.report} />
      )}
      {outdated && (
        <span className="document-error">
          Eski okuma kuralıyla işlendi; güncel kuralla okunması için yeniden işleyin.
        </span>
      )}
    </li>
  );
}
