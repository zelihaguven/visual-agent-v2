import type { ReactNode } from "react";

import type { DocumentSummary } from "./DocumentsPanel";

type Props = {
  canTalk: boolean;
  summary: DocumentSummary | null;
  onWrite: () => void;
  onTalk: () => void;
  onAddDocument: () => void;
  onOpenDocuments: () => void;
};

function Icon({ path }: { path: string }) {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path fill="currentColor" d={path} />
    </svg>
  );
}

const ICONS = {
  write: "M3 17.25V21h3.75l11-11.03-3.75-3.75L3 17.25Zm17.7-10.2a1 1 0 0 0 0-1.42l-2.33-2.33a1 1 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.83-1.83Z",
  talk: "M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.9V22h2v-3.1a7 7 0 0 0 6-6.9h-2Z",
  add: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Zm-1 13v3h-2v-3H8v-2h3v-3h2v3h3v2h-3Zm0-7V3.5L18.5 9H13Z",
};

function ActionCard({
  icon,
  title,
  text,
  onClick,
}: {
  icon: string;
  title: string;
  text: string;
  onClick: () => void;
}) {
  return (
    <button type="button" className="action-card" onClick={onClick}>
      <Icon path={icon} />
      <span className="action-title">{title}</span>
      <span className="action-text">{text}</span>
    </button>
  );
}

function statusText(summary: DocumentSummary): string {
  return [
    `${summary.ready} belge hazır`,
    summary.pending > 0 ? `${summary.pending} işleniyor` : "",
    summary.failed > 0 ? `${summary.failed} hata` : "",
  ]
    .filter(Boolean)
    .join(", ");
}

function StatusParts({ summary }: { summary: DocumentSummary }): ReactNode {
  return (
    <>
      <span className="status-ready">{summary.ready} belge hazır</span>
      {summary.pending > 0 && <span className="status-pending">{summary.pending} işleniyor</span>}
      {summary.failed > 0 && <span className="status-failed">{summary.failed} hata</span>}
    </>
  );
}

/** Açılış ekranının işlem kartları ve belge durumu; hepsi mevcut işlevlere bağlanır. */
export function LandingActions({
  canTalk,
  summary,
  onWrite,
  onTalk,
  onAddDocument,
  onOpenDocuments,
}: Props) {
  return (
    <>
      <div className="actions">
        <ActionCard
          icon={ICONS.write}
          title="Yazarak sor"
          text="Soruyu kutuya yazın."
          onClick={onWrite}
        />
        {canTalk && (
          <ActionCard
            icon={ICONS.talk}
            title="Sesli sor"
            text="Konuşma modunu açın."
            onClick={onTalk}
          />
        )}
        <ActionCard
          icon={ICONS.add}
          title="Belge ekle"
          text="PDF, Word, Excel ya da görsel yükleyin."
          onClick={onAddDocument}
        />
      </div>
      {summary !== null &&
        (summary.failed > 0 ? (
          <button
            type="button"
            className="status-card is-attention"
            aria-label={`${statusText(summary)}. Belgeleri aç`}
            onClick={onOpenDocuments}
          >
            <StatusParts summary={summary} />
          </button>
        ) : (
          <p className="status-card" role="status" aria-label={statusText(summary)}>
            <StatusParts summary={summary} />
          </p>
        ))}
    </>
  );
}
