import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { DocumentInfo } from "../api";
import { MAX_UPLOAD_BYTES } from "../limits";
import { CONFIRM_EXIT_MS } from "./ConfirmDialog";
import { DocumentsPanel } from "./DocumentsPanel";
import { Drawer } from "./Drawer";

describe("DocumentsPanel", () => {
  it("rejects a file over the upload limit without sending it", async () => {
    const fetchMock = vi.fn(async () => new Response("[]", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DocumentsPanel onClose={() => undefined} />);
    const big = new File(["x"], "buyuk.pdf", { type: "application/pdf" });
    Object.defineProperty(big, "size", { value: MAX_UPLOAD_BYTES + 1 });

    fireEvent.change(screen.getByLabelText("Belge Yükle"), { target: { files: [big] } });

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
      expect(buttons.map((button) => button.textContent)).toEqual(["Yeniden İşle", "Sil"]);
      // Düğmeler uyarı ve hatalardan önce gelir; uyarı çıkınca aşağı kaymaz.
      const actions = row.querySelector(".document-actions") as HTMLElement;
      for (const note of row.querySelectorAll(".document-error, .document-notes")) {
        expect(actions.compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
      }
    }
    const pendingRow = screen.getByText("isleniyor").closest("li") as HTMLElement;
    expect(within(pendingRow).getByRole("button", { name: /Yeniden İşle/ })).toBeDisabled();
    expect(within(pendingRow).getByRole("button", { name: /Sil/ })).toBeEnabled();
  });
  it("shows the processing steps only while the document is processed", async () => {
    const base = { filename: "x.pdf", error: null, report: null };
    const documents: DocumentInfo[] = [
      {
        ...base,
        doc_id: "p",
        title: "okunuyor",
        status: "processing",
        progress: { step: "images", done: 12, total: 54 },
      },
      {
        ...base,
        doc_id: "i",
        title: "indeksleniyor",
        status: "processing",
        progress: { step: "index", done: 0, total: 0 },
      },
      { ...base, doc_id: "s", title: "sirada", status: "queued", progress: null },
      {
        ...base,
        doc_id: "r",
        title: "hazir",
        status: "ready",
        progress: { step: "pages", done: 3, total: 3 },
      },
    ];
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(documents))));
    render(<DocumentsPanel onClose={() => undefined} />);

    const reading = (await screen.findByText("okunuyor")).closest("li") as HTMLElement;
    const bar = within(reading).getByRole("progressbar", { name: "İşleme ilerlemesi" });
    // Okuma ikinci bölüm: (1 + 12/54) / 4.
    expect(bar).toHaveAttribute("aria-valuenow", "31");
    expect(bar).toHaveAttribute("aria-valuetext", "Okunuyor · Görsel 12 / 54");
    expect(within(reading).getByText("Okunuyor · Görsel 12 / 54")).toBeInTheDocument();
    expect(bar.querySelectorAll(".progress-phase.is-done")).toHaveLength(1);

    const indexing = screen.getByText("indeksleniyor").closest("li") as HTMLElement;
    const last = within(indexing).getByRole("progressbar");
    expect(last).toHaveAttribute("aria-valuetext", "İndeksleniyor");
    expect(last).toHaveAttribute("aria-valuenow", "75");
    expect(last.querySelectorAll(".progress-phase.is-waiting")).toHaveLength(1);

    for (const title of ["sirada", "hazir"]) {
      const row = screen.getByText(title).closest("li") as HTMLElement;
      expect(within(row).queryByRole("progressbar")).toBeNull();
    }
  });
  it("warns before leaving the page only while a file is uploading", async () => {
    let finish: (response: Response) => void = () => undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init?: RequestInit) =>
        init?.method === "POST"
          ? new Promise<Response>((resolve) => (finish = resolve))
          : Promise.resolve(new Response("[]")),
      ),
    );
    render(<DocumentsPanel onClose={() => undefined} />);
    const leave = () => {
      const event = new Event("beforeunload", { cancelable: true });
      window.dispatchEvent(event);
      return event.defaultPrevented;
    };
    await act(async () => new Promise((resolve) => setTimeout(resolve, 0)));
    expect(leave()).toBe(false);

    const file = new File(["x"], "yeni.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Belge Yükle"), { target: { files: [file] } });
    await screen.findByText(/Yükleniyor/);
    expect(leave()).toBe(true);

    const uploaded = { doc_id: "n", title: "yeni", filename: "yeni.pdf", status: "queued" };
    await act(async () => finish(new Response(JSON.stringify(uploaded), { status: 201 })));
    expect(leave()).toBe(false);
  });
  it("shows a document waiting for the page reader and lets it be reprocessed", async () => {
    const waiting: DocumentInfo = {
      doc_id: "w",
      title: "tarama",
      filename: "tarama.pdf",
      status: "waiting_reader",
      error: "Taranmış sayfaların okuyucusuna ulaşılamadı; belge okuyucuyu bekliyor.",
      report: null,
    };
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify([waiting]))));
    render(<DocumentsPanel onClose={() => undefined} />);

    const row = (await screen.findByText("tarama")).closest("li") as HTMLElement;
    expect(within(row).getByText("Okuyucu bekleniyor")).toBeInTheDocument();
    expect(within(row).getByText(/okuyucuyu bekliyor/)).toBeInTheDocument();
    expect(within(row).getByRole("button", { name: /Yeniden İşle/ })).toBeEnabled();
  });
});

describe("DocumentsPanel duplicate name", () => {
  const existing: DocumentInfo = {
    doc_id: "a",
    title: "Föy",
    filename: "Olcu Foyu.pdf",
    status: "ready",
    error: null,
    report: null,
  };

  function setup() {
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) =>
      init?.method === "POST"
        ? new Response(JSON.stringify(existing), { status: 201 })
        : new Response(JSON.stringify([existing])),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<DocumentsPanel onClose={() => undefined} />);
    const posts = () =>
      fetchMock.mock.calls.filter((call: unknown[]) => (call[1] as RequestInit)?.method === "POST");
    return { posts };
  }

  async function choose(name: string) {
    await screen.findByText("Föy");
    const file = new File(["x"], name, { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Belge Yükle"), { target: { files: [file] } });
  }

  it("asks before uploading a file whose name is already loaded", async () => {
    const { posts } = setup();

    await choose("  olcu foyu.PDF ");

    const question = "Bu adla bir belge zaten var. Yine de eklensin mi?";
    expect(await screen.findByText(question)).toBeInTheDocument();
    expect(posts()).toHaveLength(0);
  });

  it("does not upload when the question is cancelled", async () => {
    const { posts } = setup();
    await choose("Olcu Foyu.pdf");

    fireEvent.click(await screen.findByRole("button", { name: /Vazgeç/ }));

    await act(async () => new Promise((resolve) => setTimeout(resolve, CONFIRM_EXIT_MS + 50)));
    expect(screen.queryByText(/Bu adla bir belge zaten var/)).not.toBeInTheDocument();
    expect(posts()).toHaveLength(0);
  });

  it("uploads when the question is confirmed", async () => {
    const { posts } = setup();
    await choose("Olcu Foyu.pdf");

    fireEvent.click(await screen.findByRole("button", { name: /Yine de Ekle/ }));

    await act(async () => new Promise((resolve) => setTimeout(resolve, CONFIRM_EXIT_MS + 50)));
    expect(posts()).toHaveLength(1);
  });

  it("treats upper and lower case the same in both Turkish and general rules", async () => {
    const { posts } = setup();

    await choose("OLCU FOYU.PDF");

    expect(await screen.findByText(/Bu adla bir belge zaten var/)).toBeInTheDocument();
    expect(posts()).toHaveLength(0);
  });

  it("uploads a file with a different name without asking", async () => {
    const { posts } = setup();

    await choose("baska.pdf");

    await act(async () => new Promise((resolve) => setTimeout(resolve, 0)));
    expect(screen.queryByText(/Bu adla bir belge zaten var/)).not.toBeInTheDocument();
    expect(posts()).toHaveLength(1);
  });
});

describe("documents drawer", () => {
  const ready: DocumentInfo = {
    doc_id: "a",
    title: "Föy",
    filename: "foy.pdf",
    status: "ready",
    error: null,
    report: null,
  };

  function stubWorkspace(matches: boolean) {
    vi.stubGlobal("matchMedia", (query: string) => ({
      matches,
      media: query,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
    }));
  }

  function renderDrawer(onClose = () => undefined) {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify([ready]))));
    return render(
      <Drawer isOpen side="left" label="Belgeler" onClose={onClose}>
        <DocumentsPanel onClose={onClose} />
      </Drawer>,
    );
  }

  it("keeps Tab inside the modal drawer on a narrow screen", async () => {
    renderDrawer();
    const drawer = screen.getByRole("dialog", { name: "Belgeler" });
    const close = screen.getByRole("button", { name: "Kapat" });
    const remove = await screen.findByRole("button", { name: "Föy Belgesini Sil" });
    expect(drawer).toHaveFocus();

    fireEvent.keyDown(drawer, { key: "Tab", shiftKey: true });
    expect(remove).toHaveFocus();

    fireEvent.keyDown(remove, { key: "Tab" });
    expect(close).toHaveFocus();
  });

  it("is part of the page on a wide screen: no scrim, no stolen focus, Escape only from inside", async () => {
    stubWorkspace(true);
    const onClose = vi.fn();
    renderDrawer(onClose);

    const drawer = screen.getByRole("complementary", { name: "Belgeler" });
    expect(drawer).not.toHaveAttribute("aria-modal");
    expect(screen.queryByTestId("drawer-backdrop")).not.toBeInTheDocument();
    expect(drawer).not.toHaveFocus();

    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).not.toHaveBeenCalled();

    (await screen.findByRole("button", { name: "Föy Belgesini Sil" })).focus();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("marks only the opening moment for the entrance animation", () => {
    vi.useFakeTimers();
    try {
      const { rerender } = render(
        <Drawer isOpen side="left" label="Belgeler" onClose={() => undefined}>
          <p>içerik</p>
        </Drawer>,
      );
      const drawer = screen.getByRole("dialog", { name: "Belgeler" });
      expect(drawer).toHaveAttribute("data-opening");

      act(() => vi.advanceTimersByTime(400));
      expect(drawer).not.toHaveAttribute("data-opening");

      // Yeniden çizim (ör. yoklama) girişi tekrarlamaz.
      rerender(
        <Drawer isOpen side="left" label="Belgeler" onClose={() => undefined}>
          <p>yeni içerik</p>
        </Drawer>,
      );
      expect(drawer).not.toHaveAttribute("data-opening");
    } finally {
      vi.useRealTimers();
    }
  });
});
