import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { DocumentInfo } from "../api";
import { MAX_UPLOAD_BYTES } from "../limits";
import { DocumentsPanel } from "./DocumentsPanel";

describe("DocumentsPanel", () => {
  it("rejects a file over the upload limit without sending it", async () => {
    const fetchMock = vi.fn(async () => new Response("[]", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DocumentsPanel onClose={() => undefined} />);
    const big = new File(["x"], "buyuk.pdf", { type: "application/pdf" });
    Object.defineProperty(big, "size", { value: MAX_UPLOAD_BYTES + 1 });

    fireEvent.change(screen.getByLabelText("Belge yükle"), { target: { files: [big] } });

    expect(await screen.findByRole("alert")).toHaveTextContent("100 MB sınırını aşıyor");
    const posts = fetchMock.mock.calls.filter(
      (call: unknown[]) => (call[1] as RequestInit | undefined)?.method === "POST",
    );
    expect(posts).toHaveLength(0);
  });
  it("keeps row buttons in the same place whatever the document status", async () => {
    const base = { filename: "x.pdf", error: null, report: null };
    const documents: DocumentInfo[] = [
      { ...base, doc_id: "a", title: "hazir", status: "ready" },
      { ...base, doc_id: "b", title: "isleniyor", status: "processing" },
      {
        ...base,
        doc_id: "c",
        title: "hatali",
        status: "failed",
        error: "Okunamadı.",
        report: { warnings: ["Uyarı"], uncertain_values: 2 },
      },
    ];
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(documents))));
    render(<DocumentsPanel onClose={() => undefined} />);

    for (const title of ["hazir", "isleniyor", "hatali"]) {
      const row = (await screen.findByText(title)).closest("li") as HTMLElement;
      const buttons = within(row).getAllByRole("button");
      expect(buttons.map((button) => button.textContent)).toEqual(["Yeniden işle", "Sil"]);
      // Düğmeler uyarı ve hatalardan önce gelir; uyarı çıkınca aşağı kaymaz.
      const actions = row.querySelector(".document-actions") as HTMLElement;
      for (const note of row.querySelectorAll(".document-error, .document-notes")) {
        expect(actions.compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
      }
    }
    const pendingRow = screen.getByText("isleniyor").closest("li") as HTMLElement;
    expect(within(pendingRow).getByRole("button", { name: /yeniden işle/ })).toBeDisabled();
    expect(within(pendingRow).getByRole("button", { name: /sil/ })).toBeEnabled();
  });
});
