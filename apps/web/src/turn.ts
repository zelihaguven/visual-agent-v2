import type { AskEvent, AskResult, Citation } from "./api";

export type ItemState = "streaming" | "verified" | "unverified";

export type TurnItem = {
  state: ItemState;
  text: string;
  sourceNumbers: number[];
  fromFigure: boolean;
};

export type Turn = {
  id: string;
  question: string;
  docIds: string[] | null;
  stage: string | null;
  sources: Citation[];
  items: Record<number, TurnItem>;
  result: AskResult | null;
  notice: string | null;
  error: string | null;
};

export function newTurn(id: string, question: string, docIds: string[] | null = null): Turn {
  return {
    id,
    question,
    docIds,
    stage: null,
    sources: [],
    items: {},
    result: null,
    notice: null,
    error: null,
  };
}

function withItem(turn: Turn, index: number, item: TurnItem): Turn {
  return { ...turn, items: { ...turn.items, [index]: item } };
}

export function applyEvent(turn: Turn, event: AskEvent): Turn {
  switch (event.type) {
    case "status":
      return { ...turn, stage: event.stage };
    case "sources":
      return { ...turn, sources: event.sources };
    case "item_stream":
      if (turn.items[event.index]?.state === "verified") {
        return turn;
      }
      return withItem(turn, event.index, {
        state: "streaming",
        text: event.text,
        sourceNumbers: [],
        fromFigure: false,
      });
    case "item_verified":
      return withItem(turn, event.index, {
        state: "verified",
        text: event.text,
        sourceNumbers: event.source_numbers,
        fromFigure: event.from_figure,
      });
    case "item_unverified":
      return withItem(turn, event.index, {
        state: "unverified",
        text: event.message,
        sourceNumbers: event.source_numbers,
        fromFigure: false,
      });
    case "reset":
      return { ...turn, items: {} };
    case "incomplete":
      return { ...turn, notice: event.message };
    case "done":
      return { ...turn, result: event.result, stage: null };
    case "error":
      return { ...turn, error: event.message, stage: null };
  }
}
