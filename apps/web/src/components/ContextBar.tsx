import type { ConversationContext } from "../api";
import { Icon } from "./Icon";

type Props = {
  context: ConversationContext;
  onClear: () => void;
};

export function ContextBar({ context, onClear }: Props) {
  const documents = context.titles.join(", ");
  return (
    <div className="context-bar" role="status">
      <p>
        <span className="context-label">Bağlam</span>
        {documents && <strong>{documents}</strong>}
        <span className="context-question">{context.question}</span>
      </p>
      <button type="button" className="ghost" onClick={onClear}>
        <Icon name="plus" />
        Yeni Konu
      </button>
    </div>
  );
}
