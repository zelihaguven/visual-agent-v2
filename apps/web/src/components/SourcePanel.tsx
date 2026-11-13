import { useEffect, useState } from "react";

import { fetchSource, type Citation, type SourceView } from "../api";
import { citationLocation } from "./TurnView";

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
      return (
        <>
          {source.section && <p className="muted source-section">{source.section}</p>}
          <p className="source-text">{source.text}</p>
        </>
      );
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
  const where = citationLocation(citation);
  return (
    <div className="source-panel">
      <header className="drawer-header">
        <div>
          <h2>{citation.title}</h2>
          {where && <p className="muted source-location">{where}</p>}
        </div>
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
    </div>
  );
}
