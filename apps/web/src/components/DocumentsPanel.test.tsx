import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MAX_UPLOAD_BYTES } from "../limits";
import { DocumentsPanel } from "./DocumentsPanel";

describe("DocumentsPanel", () => {
  it("rejects a file over the upload limit without sending it", async () => {
    const fetchMock = vi.fn(async () => new Response("[]", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DocumentsPanel />);
    const big = new File(["x"], "buyuk.pdf", { type: "application/pdf" });
    Object.defineProperty(big, "size", { value: MAX_UPLOAD_BYTES + 1 });

    fireEvent.change(screen.getByLabelText("Belge yükle"), { target: { files: [big] } });

    expect(await screen.findByRole("alert")).toHaveTextContent("100 MB sınırını aşıyor");
    const posts = fetchMock.mock.calls.filter(
      (call: unknown[]) => (call[1] as RequestInit | undefined)?.method === "POST",
    );
    expect(posts).toHaveLength(0);
  });
});
