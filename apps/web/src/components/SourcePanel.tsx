import { useEffect, useState } from "react";

import { fetchSource, type Citation, type SourceView } from "../api";

type LoadState =
  | { kind: "loading"; chunkId: string }
  | { kind: "ready"; chunkId: string; source: SourceView }
  | { kind: "failed"; chunkId: string };

function SourceContent({ source }: { source: SourceView }) {
  switch (source.kind) {
    case "page":
      return (
        <img
          className="source-page"
          src={source.image_url}
          alt={`${source.title}, sayfa ${source.page}: vurgulu kaynak sayfa`}
        />
      );
    case "sheet":
      return (
        <div className="sheet-scroll">
          <table className="sheet">
            <caption>{source.sheet}</caption>
            <tbody>
              {source.rows.map((row) => (
                <tr
                  key={row.row}
                  className={row.row === source.highlight_row ? "is-highlighted" : undefined}
                >
                  <th scope="row">{row.row}</th>
                  <td>{row.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    case "text":
      return <p className="source-text">{source.text}</p>;
  }
}

export function SourcePanel({
  citation,
  onClose,
}: {
  citation: Citation;
  onClose: () => void;
}) {
  const chunkId = citation.chunk_id;
  const [state, setState] = useState<LoadState>({ kind: "loading", chunkId });

  useEffect(() => {
    let isCurrent = true;
    fetchSource(chunkId)
      .then((source) => {
        if (isCurrent) {
          setState({ kind: "ready", chunkId, source });
        }
      })
      .catch(() => {
        if (isCurrent) {
          setState({ kind: "failed", chunkId });
        }
      });
    return () => {
      isCurrent = false;
    };
  }, [chunkId]);

  const current = state.chunkId === chunkId ? state : ({ kind: "loading", chunkId } as const);
  return (
    <aside className="source-panel" aria-label="Kaynak">
      <header className="source-header">
        <h2>{citation.title}</h2>
        <button type="button" className="ghost" onClick={onClose}>
          Kapat
        </button>
      </header>
      {current.kind === "loading" && <p className="muted">Kaynak açılıyor</p>}
      {current.kind === "failed" && (
        <p className="notice is-bad" role="alert">
          Kaynak açılamadı.
        </p>
      )}
      {current.kind === "ready" && <SourceContent source={current.source} />}
    </aside>
  );
}
