import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CitationList } from "./Citations";

const CITATION = {
  chunk_id: "d1:0",
  doc_id: "d1",
  title: "PNT-4417 ölçü föyü",
  location: { page: 2, boxes: [], sheet: null, row: null },
};

describe("CitationList", () => {
  it("lists each source as a button that opens it", () => {
    const onOpenSource = vi.fn();
    render(<CitationList citations={[CITATION]} onOpenSource={onOpenSource} />);

    const list = screen.getByRole("list", { name: "Kaynaklar" });
    const button = within(list).getByRole("button", { name: "PNT-4417 ölçü föyü · s.2" });
    fireEvent.click(button);

    expect(within(list).getAllByRole("listitem")).toHaveLength(1);
    expect(button).toHaveAttribute("title", "PNT-4417 ölçü föyü · Sayfa 2");
    expect(onOpenSource).toHaveBeenCalledWith(CITATION);
  });

  it("draws no empty list when there is no source", () => {
    render(<CitationList citations={[]} onOpenSource={() => undefined} />);

    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });
});
