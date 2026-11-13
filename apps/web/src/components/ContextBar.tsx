import type { ConversationContext } from "../api";
import { readableName } from "../documentGroups";

type Props = {
  context: ConversationContext;
  onClear: () => void;
};

export function ContextBar({ context, onClear }: Props) {
  const documents = context.titles.map(readableName).join(", ");
  return (
    <div className="context-bar" role="status">
      <p>
        <span className="context-label">Bağlam</span>
        {documents && <strong>{documents}</strong>}
        <span className="context-question">{context.question}</span>
      </p>
      <button type="button" className="ghost" onClick={onClear}>
        Yeni konu
      </button>
    </div>
  );
}
