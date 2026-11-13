import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { WAITING_DELAY_MS } from "./components/ConversationMode";
import { citationDetail, citationLabel } from "./components/TurnView";
import { applyEvent, newTurn } from "./turn";

const listening = vi.hoisted(() => ({
  open: vi.fn(),
  listen: vi.fn(),
  barge: vi.fn(),
  close: vi.fn(),
}));

vi.mock("./listening", async (original) => ({
  ...(await original<typeof import("./listening")>()),
  openMicrophone: listening.open,
  listenForUtterance: listening.listen,
  listenForBargeIn: listening.barge,
}));

const CITATION = {
  chunk_id: "d1:0",
  doc_id: "d1",
  title: "PNT-4417 ölçü föyü",
  location: { page: 2, boxes: [], sheet: null, row: null },
};

function sse(events: object[]): Response {
  const body = events.map((event) => `data: ${JSON.stringify(event)}\n\n`).join("");
  return new Response(body, { headers: { "Content-Type": "text/event-stream" } });
}

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

type Route = (url: string, init?: RequestInit) => Response;

function stubApi(routes: Record<string, Route>) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const key = Object.keys(routes).find((route) => url.startsWith(route));
    return key ? routes[key](url, init) : jsonResponse({}, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function stubBrowserRecording() {
  const stopTrack = vi.fn();
  class FakeRecorder {
    mimeType = "audio/webm";
    ondataavailable: ((event: { data: Blob }) => void) | null = null;
    onstop: (() => void) | null = null;
    start() {}
    stop() {
      this.ondataavailable?.({ data: new Blob(["ses"], { type: "audio/webm" }) });
      this.onstop?.();
    }
  }
  vi.stubGlobal("MediaRecorder", FakeRecorder);
  Object.defineProperty(navigator, "mediaDevices", {
    configurable: true,
    value: {
      getUserMedia: vi.fn(async () => ({ getTracks: () => [{ stop: stopTrack }] })),
    },
  });
  return stopTrack;
}

const answered = {
  type: "done",
  timings: {},
  question: "soru",
  scope_inherited: false,
  context: null,
  result: {
    kind: "answered",
    status: "verified",
    has_conflict: false,
    problems: [],
    items: [
      {
        text: "İç paça 76,5 cm.",
        citations: [CITATION],
        verified: true,
        from_ocr: false,
        code: null,
        problems: [],
      },
    ],
  },
};

async function ask(question: string) {
  fireEvent.change(screen.getByLabelText("Sorunuz"), { target: { value: question } });
  fireEvent.click(screen.getByRole("button", { name: "Sor" }));
}

function openDocuments() {
  fireEvent.click(screen.getByRole("button", { name: /^Belgeler/ }));
}

describe("applyEvent", () => {
  it("keeps streamed text masked until the item is verified", () => {
    let turn = newTurn("1", "soru");
    turn = applyEvent(turn, { type: "item_stream", index: 0, text: "İç paça ▒▒▒" });

    expect(turn.items[0]).toMatchObject({ state: "streaming", text: "İç paça ▒▒▒" });

    turn = applyEvent(turn, {
      type: "item_verified",
      index: 0,
      text: "İç paça 76,5 cm.",
      source_numbers: [1],
      from_ocr: false, has_code: false,
    });

    expect(turn.items[0]).toMatchObject({ state: "verified", text: "İç paça 76,5 cm." });
  });

  it("does not let a late stream event overwrite a verified item", () => {
    let turn = newTurn("1", "soru");
    turn = applyEvent(turn, {
      type: "item_verified",
      index: 0,
      text: "76,5",
      source_numbers: [],
      from_ocr: false, has_code: false,
    });
    turn = applyEvent(turn, { type: "item_stream", index: 0, text: "▒▒▒" });

    expect(turn.items[0].text).toBe("76,5");
  });

  it("clears streamed items when the provider is switched", () => {
    let turn = newTurn("1", "soru");
    turn = applyEvent(turn, { type: "item_stream", index: 0, text: "Metin" });

    expect(applyEvent(turn, { type: "reset" }).items).toEqual({});
  });

  it("keeps a received answer when an error arrives after it", () => {
    let turn = applyEvent(newTurn("1", "soru"), answered as never);
    turn = applyEvent(turn, { type: "error", message: "Bağlantı koptu." });

    expect(turn.result).not.toBeNull();
    expect(turn.error).toBeNull();
    expect(turn.notice).toBe("Bağlantı koptu.");
  });

  it("does not mutate the previous turn", () => {
    const turn = newTurn("1", "soru");
    applyEvent(turn, { type: "item_stream", index: 0, text: "Metin" });

    expect(turn.items).toEqual({});
  });
});

describe("App", () => {
  it("shows a verified answer with its badge and masks values while streaming", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          { type: "status", stage: "retrieve" },
          { type: "sources", sources: [CITATION] },
          { type: "item_stream", index: 0, text: "İç paça ▒▒▒" },
          {
            type: "item_verified",
            index: 0,
            text: "İç paça 76,5 cm.",
            source_numbers: [1],
            from_ocr: false, has_code: false,
          },
          answered,
        ]),
    });
    render(<App />);

    await ask("İç paça kaç?");

    expect(await screen.findByText("Doğrulandı")).toBeInTheDocument();
    expect(screen.getByText("İç paça 76,5 cm.")).toBeInTheDocument();
    expect(screen.queryByText(/▒/)).not.toBeInTheDocument();
  });

  it("opens the highlighted page of a citation", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ type: "sources", sources: [CITATION] }, answered]),
      "/api/chunks/d1%3A0/source": () =>
        jsonResponse({
          kind: "page",
          page: 2,
          title: "PNT-4417 ölçü föyü",
          image_url: "/api/chunks/d1:0/preview.png",
        }),
    });
    render(<App />);
    await ask("soru");

    fireEvent.click(await screen.findByRole("button", { name: /PNT-4417 ölçü föyü · s\.2/ }));

    const image = await screen.findByRole("img", { name: /vurgulu kaynak sayfa/i });
    expect(image).toHaveAttribute("src", "/api/chunks/d1:0/preview.png");
  });

  it("highlights the source row of a spreadsheet", async () => {
    const citation = { ...CITATION, location: { page: null, boxes: [], sheet: "Ölçüler", row: 5 } };
    const result = { ...answered.result, items: [{ ...answered.result.items[0], citations: [citation] }] };
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ ...answered, result }]),
      "/api/chunks/d1%3A0/source": () =>
        jsonResponse({
          kind: "sheet",
          sheet: "Ölçüler",
          title: "Föy",
          highlight_row: 5,
          rows: [
            { row: 4, text: "Beden: S" },
            { row: 5, text: "Beden: M" },
          ],
        }),
    });
    render(<App />);
    await ask("soru");

    fireEvent.click(await screen.findByRole("button", { name: "PNT-4417 ölçü föyü · satır 5" }));

    const row = (await screen.findByText("Beden: M")).closest("tr");
    expect(row).toHaveClass("is-highlighted");
  });

  it("offers document choices when clarification is needed and asks again", async () => {
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          {
            type: "done",
            timings: {},
            question: "soru",
            scope_inherited: false,
            context: null,
            result: {
              kind: "clarify",
              question: "Hangi model?",
              options: [{ doc_id: "a", label: "Model A" }],
            },
          },
        ]),
    });
    render(<App />);
    await ask("iç paça kaç");

    fireEvent.click(await screen.findByRole("button", { name: "Model A" }));

    await waitFor(() => {
      const asks = fetchMock.mock.calls.filter(([url]) => String(url) === "/api/ask");
      expect(asks).toHaveLength(2);
      expect(JSON.parse(String(asks[1][1]?.body))).toEqual({
        question: "iç paça kaç",
        doc_ids: ["a"],
      });
    });
  });

  it("locks the choices of earlier turns while another question is being answered", async () => {
    let asks = 0;
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => {
        asks += 1;
        if (asks === 1) {
          return sse([
            {
              type: "done",
              timings: {},
              question: "soru",
              scope_inherited: false,
              context: null,
              result: { kind: "clarify", question: "Hangi model?", options: [{ doc_id: "a", label: "Model A" }] },
            },
          ]);
        }
        // İkinci cevap akmaya devam ediyor: akış kapanmıyor.
        return new Response(new ReadableStream({ start() {} }), {
          headers: { "Content-Type": "text/event-stream" },
        });
      },
    });
    render(<App />);
    await ask("iç paça kaç");
    const choice = await screen.findByRole("button", { name: "Model A" });
    expect(choice).toBeEnabled();

    await ask("başka soru");

    await waitFor(() => expect(choice).toBeDisabled());
  });

  it("scrolls each new question to the top of the conversation", async () => {
    const scrolled: Element[] = [];
    const scrollIntoView = vi.fn(function (this: Element) {
      scrolled.push(this);
    });
    Element.prototype.scrollIntoView = scrollIntoView;
    stubApi({ "/api/documents": () => jsonResponse([]), "/api/ask": () => sse([answered]) });
    render(<App />);

    await ask("ilk soru");
    await screen.findByText("Doğrulandı");
    await ask("ikinci soru");
    await waitFor(() => expect(screen.getAllByText("Doğrulandı")).toHaveLength(2));

    expect(scrollIntoView).toHaveBeenCalledTimes(2);
    expect(scrollIntoView).toHaveBeenLastCalledWith({ block: "start", behavior: "smooth" });
    expect(scrolled.map((turn) => turn.querySelector(".question")?.textContent)).toEqual([
      "ilk soru",
      "ikinci soru",
    ]);
  });

  it("says a sentence was hidden, without claiming there was a value", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          { type: "item_unverified", index: 0, source_numbers: [] },
          {
            ...answered,
            result: {
              ...answered.result,
              status: "failed",
              items: [
                { ...answered.result.items[0], verified: false, citations: [] },
                { ...answered.result.items[0], verified: false },
              ],
            },
          },
        ]),
    });
    render(<App />);
    await ask("soru");

    expect(
      await screen.findByText("Bu cümle kaynakla doğrulanamadığı için gösterilmiyor."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Bu cümle kaynakla doğrulanamadığı için gösterilmiyor. Kaynağa bakın."),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Değer doğrulanamadı/)).not.toBeInTheDocument();
  });

  it("shows the source quote of a unit-hidden sentence but does not read it aloud", async () => {
    URL.createObjectURL = vi.fn(() => "blob:ses");
    URL.revokeObjectURL = vi.fn();
    const quoted = {
      ...answered.result.items[0],
      text: "L beden bel 42,5 cm.",
      verified: false,
      source_quote: "L: 42,5",
    };
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          { type: "item_unverified", index: 0, source_numbers: [1], quote: "L: 42,5" },
          { ...answered, result: { ...answered.result, status: "failed", items: [quoted] } },
        ]),
      "/api/speak": () => jsonResponse({ audios: [{ audio: btoa("ses"), mime: "audio/wav" }] }),
    });
    render(<App />);
    await ask("soru");

    expect(await screen.findByText('Kaynakta yazan: "L: 42,5"')).toBeInTheDocument();
    expect(screen.queryByText(/42,5 cm/)).not.toBeInTheDocument();
    fireEvent.click(await screen.findByRole("button", { name: "Cevabı seslendir" }));
    await screen.findByRole("button", { name: "Seslendirmeyi durdur" });
    const body = fetchMock.mock.calls.find(([url]) => String(url) === "/api/speak")?.[1]?.body;
    expect(JSON.parse(String(body))).toEqual({
      items: [{ text: "Kaynaktaki satır ekranda gösteriliyor.", has_code: false }],
    });
  });

  it("states clearly when the answer is not in the documents", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          {
            type: "done",
            timings: {},
            question: "soru",
            scope_inherited: false,
            context: null,
            result: { kind: "not_found", reason: "", suggestions: [] },
          },
        ]),
    });
    render(<App />);
    await ask("soru");

    expect(await screen.findByText("Bu bilgi belgelerde bulunamadı.")).toBeInTheDocument();
    expect(screen.queryByText(/model/i)).not.toBeInTheDocument();
  });

  it("shows an error when the answer stream fails", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => new Response("", { status: 500 }),
    });
    render(<App />);
    await ask("soru");

    expect(await screen.findByRole("alert")).toHaveTextContent("Cevap alınamadı");
  });

  it("lists documents with their processing state", async () => {
    stubApi({
      "/api/documents": () =>
        jsonResponse([
          { doc_id: "a", title: "Kılavuz", filename: "a.pdf", status: "processing", error: null, report: null },
          { doc_id: "b", title: "Bozuk", filename: "b.pdf", status: "failed", error: "Belge işlenemedi.", report: null },
        ]),
    });
    render(<App />);
    openDocuments();

    const list = await screen.findByRole("list", { name: "Belgeler" });
    expect(within(list).getByText("İşleniyor")).toBeInTheDocument();
    expect(within(list).getByText("Belge işlenemedi.")).toBeInTheDocument();
  });

  it("clears the list error once the list loads again and notices documents added elsewhere", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    try {
      let calls = 0;
      stubApi({
        "/api/documents": () => {
          calls += 1;
          return calls === 1
            ? jsonResponse({ detail: "yok" }, 503)
            : jsonResponse([{ doc_id: "a", title: "Yeni föy", filename: "a.pdf", status: "ready", error: null, report: null }]);
        },
      });
      render(<App />);
      expect(await screen.findByText("Belge listesi alınamadı.")).toBeInTheDocument();

      await vi.advanceTimersByTimeAsync(30_000);

      expect(await screen.findByText("Yeni föy")).toBeInTheDocument();
      expect(screen.queryByText("Belge listesi alınamadı.")).not.toBeInTheDocument();
    } finally {
      vi.useRealTimers();
    }
  });

  it("keeps an action error after the list is refreshed", async () => {
    stubDocumentActions(404);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<App />);
    openDocuments();

    fireEvent.click(await screen.findByRole("button", { name: "Föy belgesini sil" }));

    expect(await screen.findByText("Belge bulunamadı.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("Belge bulunamadı.")).toBeInTheDocument());
  });

  const READY_DOCUMENT = {
    doc_id: "d1",
    title: "Föy",
    filename: "foy.pdf",
    status: "ready",
    error: null,
    report: null,
  };

  function stubDocumentActions(deleteStatus = 204) {
    let documents: unknown[] = [READY_DOCUMENT];
    return stubApi({
      "/api/documents": (url, init) => {
        if (init?.method === "DELETE") {
          if (deleteStatus === 204) {
            documents = [];
            return new Response(null, { status: 204 });
          }
          return jsonResponse({ detail: "Belge bulunamadı." }, deleteStatus);
        }
        if (url.endsWith("/reprocess")) {
          documents = [{ ...READY_DOCUMENT, status: "queued" }];
          return jsonResponse(documents[0]);
        }
        return jsonResponse(documents);
      },
    });
  }

  const methodCalls = (fetchMock: ReturnType<typeof stubApi>, method: string) =>
    fetchMock.mock.calls.filter(([, init]) => init?.method === method).map(([url]) => String(url));

  it("deletes a document only after the user confirms", async () => {
    const fetchMock = stubDocumentActions();
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<App />);
    openDocuments();

    fireEvent.click(await screen.findByRole("button", { name: "Föy belgesini sil" }));

    await waitFor(() => expect(screen.queryByText("Föy")).not.toBeInTheDocument());
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('"Föy" silinsin mi?'));
    expect(methodCalls(fetchMock, "DELETE")).toEqual(["/api/documents/d1"]);
  });

  it("keeps the document when the user cancels the deletion", async () => {
    const fetchMock = stubDocumentActions();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<App />);
    openDocuments();

    fireEvent.click(await screen.findByRole("button", { name: "Föy belgesini sil" }));

    expect(screen.getByText("Föy")).toBeInTheDocument();
    expect(methodCalls(fetchMock, "DELETE")).toEqual([]);
  });

  it("shows why a deletion failed", async () => {
    stubDocumentActions(404);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<App />);
    openDocuments();

    fireEvent.click(await screen.findByRole("button", { name: "Föy belgesini sil" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Belge bulunamadı.");
  });

  it("queues a ready document for processing again", async () => {
    const fetchMock = stubDocumentActions();
    render(<App />);
    openDocuments();

    fireEvent.click(await screen.findByRole("button", { name: "Föy belgesini yeniden işle" }));

    expect(await screen.findByText("Kuyrukta")).toBeInTheDocument();
    expect(methodCalls(fetchMock, "POST")).toEqual(["/api/documents/d1/reprocess"]);
    expect(
      screen.queryByRole("button", { name: "Föy belgesini yeniden işle" }),
    ).not.toBeInTheDocument();
  });

  it("shows skipped images and uncertain OCR values of a document", async () => {
    const warning = "Sayfa 1: görsel okunmadı (kısa kenarı 17 pt, en az 50 pt gerekir).";
    stubApi({
      "/api/documents": () =>
        jsonResponse([
          {
            doc_id: "a",
            title: "Föy",
            filename: "a.docx",
            status: "ready",
            error: null,
            report: { warnings: [warning], uncertain_values: 6 },
          },
        ]),
    });
    render(<App />);
    openDocuments();

    const notes = await screen.findByRole("list", { name: "Föy uyarıları" });
    expect(within(notes).getByText(warning)).toBeInTheDocument();
    expect(within(notes).getByText(/6 değer net okunamadı/)).toBeInTheDocument();
  });

  it("tells which documents were read with older rules", async () => {
    stubApi({
      "/api/documents": () =>
        jsonResponse([
          {
            doc_id: "a",
            title: "Kılavuz",
            filename: "a.md",
            status: "ready",
            error: null,
            report: { warnings: [], uncertain_values: 0 },
            outdated: true,
          },
        ]),
    });
    render(<App />);

    expect(await screen.findByText(/Eski okuma kuralıyla işlendi/)).toBeInTheDocument();
  });

  it("shows no warning list for a cleanly read document", async () => {
    stubApi({
      "/api/documents": () =>
        jsonResponse([
          {
            doc_id: "a",
            title: "Föy",
            filename: "a.pdf",
            status: "ready",
            error: null,
            report: { warnings: [], uncertain_values: 0 },
          },
        ]),
    });
    render(<App />);
    openDocuments();

    await screen.findByText("Föy");
    expect(screen.queryByRole("list", { name: "Föy uyarıları" })).not.toBeInTheDocument();
    expect(screen.queryByText("Hazır")).not.toBeInTheDocument(); // hazır belgede etiket yok
  });

  it("uploads a file and shows the server's rejection reason", async () => {
    const fetchMock = stubApi({
      "/api/documents": (_url, init) =>
        init?.method === "POST"
          ? jsonResponse({ detail: "virus.exe: bu dosya türü desteklenmiyor" }, 415)
          : jsonResponse([]),
    });
    render(<App />);
    openDocuments();

    const input = await screen.findByLabelText("Belge yükle");
    fireEvent.change(input, { target: { files: [new File(["MZ"], "virus.exe")] } });

    expect(await screen.findByRole("alert")).toHaveTextContent("desteklenmiyor");
    expect(fetchMock.mock.calls.some(([, init]) => init?.method === "POST")).toBe(true);
  });

  const CONTEXT = {
    question: "PNT-4417 M beden iç paça kaç?",
    doc_ids: ["d1"],
    titles: ["PNT-4417 ölçü föyü"],
  };
  const askBodies = (fetchMock: ReturnType<typeof stubApi>) =>
    fetchMock.mock.calls
      .filter(([url]) => String(url) === "/api/ask")
      .map(([, init]) => JSON.parse(String(init?.body)));

  it("sends the last context with the next question and shows how it was understood", async () => {
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          { type: "resolved", question: "PNT-4417 M beden dış paça kaç?" },
          { ...answered, context: CONTEXT },
        ]),
    });
    render(<App />);
    await ask("PNT-4417 M beden iç paça kaç?");
    expect(await screen.findByRole("status")).toHaveTextContent("PNT-4417 ölçü föyü");

    await ask("Peki dış paça?");

    await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(2));
    expect(askBodies(fetchMock)[0]).toEqual({ question: "PNT-4417 M beden iç paça kaç?" });
    expect(askBodies(fetchMock)[1]).toEqual({ question: "Peki dış paça?", context: CONTEXT });
    expect(
      (await screen.findAllByText("Anlaşılan soru: PNT-4417 M beden dış paça kaç?")).length,
    ).toBeGreaterThan(0);
  });

  it("starts a new topic without the previous context", async () => {
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ ...answered, context: CONTEXT }]),
    });
    render(<App />);
    await ask("ilk soru");
    fireEvent.click(await screen.findByRole("button", { name: "Yeni konu" }));
    expect(screen.queryByRole("status")).not.toBeInTheDocument();

    await ask("ikinci soru");

    await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(2));
    expect(askBodies(fetchMock)[1]).toEqual({ question: "ikinci soru" });
  });

  it("offers a wider search when a follow-up is not in the active document", async () => {
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          { type: "resolved", question: "PNT-4417 kordon boyu kaç?" },
          {
            type: "done",
            timings: {},
            question: "PNT-4417 kordon boyu kaç?",
            scope_inherited: true,
            context: CONTEXT,
            result: { kind: "not_found", reason: "", suggestions: [] },
          },
        ]),
    });
    render(<App />);
    await ask("Peki kordon boyu?");
    expect(await screen.findByText("Bu bilgi bu belgede yok.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Tüm belgelerde ara" }));

    await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(2));
    expect(askBodies(fetchMock)[1]).toEqual({ question: "PNT-4417 kordon boyu kaç?" });
  });

  it("offers the documents that contain the asked code as choices", async () => {
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          {
            type: "done",
            timings: {},
            question: "E050 nedir?",
            scope_inherited: false,
            context: null,
            result: {
              kind: "not_found",
              reason: "E050 seçilen belgelerde geçmiyor.",
              suggestions: [{ doc_id: "b", label: "Kılavuz" }],
            },
          },
        ]),
    });
    render(<App />);
    await ask("E050 nedir?");

    fireEvent.click(await screen.findByRole("button", { name: "Kılavuz" }));

    await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(2));
    expect(askBodies(fetchMock)[1]).toEqual({ question: "E050 nedir?", doc_ids: ["b"] });
  });

  it("shows a command once when the sentence is only the command", async () => {
    const command = "ALTER TABLE T RENAME COLUMN A TO B;";
    const item = { ...answered.result.items[0], text: command, code: command };
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ ...answered, result: { ...answered.result, items: [item] } }]),
    });
    render(<App />);
    await ask("komut ne");

    expect(await screen.findAllByText(command)).toHaveLength(1);
  });

  it("reads an answer aloud from the button beside it and stops on a second press", async () => {
    URL.createObjectURL = vi.fn(() => "blob:ses");
    URL.revokeObjectURL = vi.fn();
    const pause = vi.spyOn(window.HTMLMediaElement.prototype, "pause");
    const fetchMock = stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([answered]),
      "/api/speak": () => jsonResponse({ audios: [{ audio: btoa("ses"), mime: "audio/wav" }] }),
    });
    render(<App />);
    await ask("soru");

    fireEvent.click(await screen.findByRole("button", { name: "Cevabı seslendir" }));

    const stop = await screen.findByRole("button", { name: "Seslendirmeyi durdur" });
    const body = fetchMock.mock.calls.find(([url]) => String(url) === "/api/speak")?.[1]?.body;
    expect(JSON.parse(String(body))).toEqual({
      items: [{ text: "İç paça 76,5 cm.", has_code: false }],
    });
    expect(URL.createObjectURL).toHaveBeenCalledTimes(1);

    pause.mockClear();
    fireEvent.click(stop);

    expect(await screen.findByRole("button", { name: "Cevabı seslendir" })).toBeInTheDocument();
    expect(pause).toHaveBeenCalled();
    pause.mockRestore();
  });

  it("offers no read-aloud when nothing was verified", async () => {
    const item = { ...answered.result.items[0], verified: false };
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([{ ...answered, result: { ...answered.result, status: "failed", items: [item] } }]),
    });
    render(<App />);
    await ask("soru");

    await screen.findByText("Doğrulanamadı");
    expect(screen.queryByRole("button", { name: "Cevabı seslendir" })).not.toBeInTheDocument();
  });

  it("explains a failed read-aloud", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([answered]),
      "/api/speak": () => jsonResponse({ detail: "x" }, 502),
    });
    render(<App />);
    await ask("soru");

    fireEvent.click(await screen.findByRole("button", { name: "Cevabı seslendir" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("seslendirilemedi");
    expect(await screen.findByRole("button", { name: "Cevabı seslendir" })).toBeEnabled();
  });

  it("tells the user when speech is unavailable and keeps the answer", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ type: "audio_unavailable" }, answered]),
    });
    render(<App />);
    await ask("soru");

    expect(await screen.findByText("İç paça 76,5 cm.")).toBeInTheDocument();
    expect(screen.getByText(/Sesli okuma şu an kullanılamıyor/)).toBeInTheDocument();
  });

  it("lists what the assistant holds and asks which one is meant", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          {
            type: "done",
            timings: {},
            question: "soru",
            scope_inherited: false,
            context: null,
            result: {
              kind: "inventory",
              document_count: 1,
              code_count: 205,
              documents: [{ doc_id: "a", title: "Föy", codes: ["PNT-1", "PNT-2"], code_count: 205 }],
            },
          },
        ]),
    });
    render(<App />);
    await ask("kaç belge var");

    expect(await screen.findByText("1 belge, 205 kod")).toBeInTheDocument();
    expect(screen.getByText("PNT-1, PNT-2 ve 203 kod daha")).toBeInTheDocument();
    expect(screen.getByText("Hangisini soruyorsunuz?")).toBeInTheDocument();
  });

  it("gives only the count when too many documents would be listed", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () =>
        sse([
          {
            type: "done",
            timings: {},
            question: "soru",
            scope_inherited: false,
            context: null,
            result: { kind: "inventory", document_count: 377, code_count: 0, documents: [] },
          },
        ]),
    });
    render(<App />);
    await ask("neler var");

    expect(await screen.findByText("377 belge, 0 kod")).toBeInTheDocument();
    expect(screen.getByText(/Bir konu ya da belge adı yazarsanız/)).toBeInTheDocument();
    expect(screen.queryByText("Hangisini soruyorsunuz?")).not.toBeInTheDocument();
  });

  describe("conversation mode", () => {
    const phrase = (name: string) => ({ audio: btoa(name), mime: "audio/wav" });
    const PHRASES = { greeting: phrase("merhaba"), waiting: [phrase("bir")] };
    const NEXT = { question: "Tam soru?", doc_ids: ["d1"], titles: ["Föy"] };

    function stubAudio(endsByItself = true) {
      const create = vi.fn(() => "blob:ses");
      URL.createObjectURL = create as unknown as typeof URL.createObjectURL;
      URL.revokeObjectURL = vi.fn();
      vi.spyOn(window.HTMLMediaElement.prototype, "play").mockImplementation(async function (
        this: HTMLMediaElement,
      ) {
        if (endsByItself) {
          setTimeout(() => this.onended?.(new Event("ended")));
        }
      });
      return create;
    }

    function hearInTurn(...recordings: string[]) {
      const queue = [...recordings];
      listening.listen.mockImplementation(
        (_mic: unknown, _level: unknown, signal: AbortSignal) =>
          new Promise((resolve) => {
            const next = queue.shift();
            if (next !== undefined) {
              resolve(new Blob([next], { type: "audio/webm" }));
            } else {
              signal.addEventListener("abort", () => resolve(null));
            }
          }),
      );
    }

    const askBodiesOf = (fetchMock: ReturnType<typeof stubApi>) =>
      fetchMock.mock.calls
        .filter(([url]) => String(url) === "/api/ask")
        .map(([, init]) => JSON.parse(String(init?.body)));

    async function open(fetchMock: ReturnType<typeof stubApi>) {
      render(<App />);
      await waitFor(() =>
        expect(fetchMock.mock.calls.some(([url]) => String(url) === "/api/voice/phrases")).toBe(true),
      );
      await new Promise((resolve) => setTimeout(resolve));
      fireEvent.click(screen.getByRole("button", { name: "Konuşma modu" }));
    }

    function conversationApi(transcripts: string[]) {
      const queue = [...transcripts];
      return stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse(PHRASES),
        "/api/transcribe": () => jsonResponse({ text: queue.shift() ?? "" }),
        "/api/ask": () =>
          sse([
            { type: "item_audio", index: 0, audio: btoa("ses"), mime: "audio/wav" },
            { ...answered, context: NEXT },
          ]),
      });
    }

    beforeEach(() => {
      stubBrowserRecording();
      listening.close.mockClear();
      listening.open.mockReset();
      listening.open.mockResolvedValue({ stream: {}, level: () => 0, close: listening.close });
      listening.listen.mockReset();
      listening.barge.mockReset();
      listening.barge.mockImplementation(
        (_mic: unknown, _session: unknown, turnDone: AbortSignal) =>
          new Promise((resolve) => {
            turnDone.addEventListener("abort", () => resolve(null));
          }),
      );
    });

    it("hears, asks by itself with speech on, answers and listens again", async () => {
      stubAudio();
      hearInTurn("birinci", "ikinci");
      const fetchMock = conversationApi(["PNT-1162 bel kaç", "peki dış paça"]);

      await open(fetchMock);

      await waitFor(() => expect(askBodiesOf(fetchMock)).toHaveLength(2));
      expect(askBodiesOf(fetchMock)).toEqual([
        { question: "PNT-1162 bel kaç", speak: true },
        { question: "peki dış paça", speak: true, context: NEXT },
      ]);
      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(3));
      expect(await screen.findByText("Dinliyorum")).toBeInTheDocument();
    });

    it("greets only the first time and releases the microphone when finished", async () => {
      const create = stubAudio();
      hearInTurn();
      const fetchMock = conversationApi([]);

      await open(fetchMock);
      await screen.findByText("Dinliyorum");
      expect(create).toHaveBeenCalledTimes(1);
      fireEvent.click(screen.getByRole("button", { name: "Bitir" }));
      await waitFor(() => expect(listening.close).toHaveBeenCalled());
      expect(screen.queryByText("Dinliyorum")).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: "Konuşma modu" }));
      await screen.findByText("Dinliyorum");
      expect(create).toHaveBeenCalledTimes(1);
    });

    function replyApi(events: object[]) {
      return stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse(PHRASES),
        "/api/transcribe": () => jsonResponse({ text: "merhaba" }),
        "/api/ask": () => sse(events),
      });
    }

    function pausedSse(first: object[], rest: object[], pauseMs: number) {
      const encode = (events: object[]) =>
        new TextEncoder().encode(events.map((event) => `data: ${JSON.stringify(event)}\n\n`).join(""));
      const body = new ReadableStream({
        start(controller) {
          controller.enqueue(encode(first));
          setTimeout(() => {
            controller.enqueue(encode(rest));
            controller.close();
          }, pauseMs);
        },
      });
      return new Response(body, { status: 200, headers: { "content-type": "text/event-stream" } });
    }

    function pausedApi(first: object[], rest: object[]) {
      return stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse(PHRASES),
        "/api/transcribe": () => jsonResponse({ text: "merhaba" }),
        "/api/ask": () => pausedSse(first, rest, WAITING_DELAY_MS + 200),
      });
    }

    it("plays a waiting phrase when the answer is late", async () => {
      const create = stubAudio();
      hearInTurn("birinci");
      const fetchMock = pausedApi([{ type: "searching" }], [{ ...answered, context: NEXT }]);

      await open(fetchMock);

      await waitFor(() => expect(create).toHaveBeenCalledTimes(2), {
        timeout: WAITING_DELAY_MS + 1000,
      });
    });

    it("skips the waiting phrase when the answer is quick", async () => {
      const create = stubAudio();
      hearInTurn("birinci");
      const fetchMock = replyApi([{ type: "searching" }, { ...answered, context: NEXT }]);

      await open(fetchMock);

      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(2));
      await new Promise((resolve) => setTimeout(resolve, WAITING_DELAY_MS + 200));
      expect(create).toHaveBeenCalledTimes(1);
    });

    it("skips the waiting phrase once the answer has started to play", async () => {
      const create = stubAudio();
      hearInTurn("birinci");
      const fetchMock = pausedApi(
        [{ type: "searching" }, { type: "item_audio", index: 0, audio: btoa("ses"), mime: "audio/wav" }],
        [{ ...answered, context: NEXT }],
      );

      await open(fetchMock);

      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(2), {
        timeout: WAITING_DELAY_MS + 1500,
      });
      expect(create).toHaveBeenCalledTimes(2);
    });

    it("answers a greeting without a waiting phrase", async () => {
      const create = stubAudio();
      hearInTurn("birinci");
      const smallTalk = { ...answered, result: { kind: "small_talk", text: "Merhaba!" } };
      const fetchMock = replyApi([
        { type: "item_audio", index: -1, audio: btoa("ses"), mime: "audio/wav" },
        smallTalk,
      ]);

      await open(fetchMock);

      expect((await screen.findAllByText("Merhaba!")).length).toBeGreaterThan(0);
      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(2));
      expect(create).toHaveBeenCalledTimes(2);
    });

    it("asks again with speech when a clarification choice is pressed in conversation", async () => {
      stubAudio();
      hearInTurn("birinci");
      let asks = 0;
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse(PHRASES),
        "/api/transcribe": () => jsonResponse({ text: "iç paça kaç" }),
        "/api/ask": () => {
          asks += 1;
          return asks === 1
            ? sse([
                {
                  type: "done",
                  timings: {},
                  question: "iç paça kaç",
                  scope_inherited: false,
                  context: null,
                  result: { kind: "clarify", question: "Hangi model?", options: [{ doc_id: "a", label: "Model A" }] },
                },
              ])
            : sse([{ type: "item_audio", index: 0, audio: btoa("ses"), mime: "audio/wav" }, answered]);
        },
      });

      await open(fetchMock);
      const talk = screen.getByRole("region", { name: "Konuşma modu" });
      const choice = await within(talk).findByRole("button", { name: "Model A" });
      await waitFor(() => expect(choice).toBeEnabled());
      fireEvent.click(choice);

      await waitFor(() => expect(askBodiesOf(fetchMock)).toHaveLength(2));
      expect(askBodiesOf(fetchMock)[1]).toEqual({ question: "iç paça kaç", doc_ids: ["a"], speak: true });
      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(3));
    });

    it("shows a voice service failure instead of asking to repeat", async () => {
      stubAudio();
      hearInTurn("birinci", "ikinci");
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse(PHRASES),
        "/api/transcribe": () => jsonResponse({ detail: "Ses servisi yapılandırılmamış." }, 503),
      });

      await open(fetchMock);

      expect(await screen.findByRole("alert")).toHaveTextContent("Ses servisine ulaşılamadı");
      expect(listening.close).toHaveBeenCalled();
      expect(screen.queryByText("Anlayamadım, tekrar söyler misiniz?")).not.toBeInTheDocument();
      expect(listening.listen).toHaveBeenCalledTimes(1);
      expect(askBodiesOf(fetchMock)).toHaveLength(0);
    });

    it("hides conversation mode only when the server has no voice service", async () => {
      stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse({ detail: "Ses servisi yapılandırılmamış." }, 503),
      });
      render(<App />);

      await waitFor(() =>
        expect(screen.queryByRole("button", { name: "Konuşma modu" })).not.toBeInTheDocument(),
      );
    });

    it("keeps conversation mode when the phrases cannot be loaded for a passing reason", async () => {
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => {
          throw new TypeError("ağ hatası");
        },
      });
      render(<App />);

      await waitFor(() =>
        expect(fetchMock.mock.calls.some(([url]) => String(url) === "/api/voice/phrases")).toBe(true),
      );
      await new Promise((resolve) => setTimeout(resolve));
      expect(screen.getByRole("button", { name: "Konuşma modu" })).toBeInTheDocument();
    });

    it("asks to repeat instead of sending an empty transcript", async () => {
      stubAudio();
      hearInTurn("gurultu");
      const fetchMock = conversationApi([""]);

      await open(fetchMock);

      expect(await screen.findByText("Anlayamadım, tekrar söyler misiniz?")).toBeInTheDocument();
      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(2));
      expect(askBodiesOf(fetchMock)).toHaveLength(0);
    });

    it("stops talking and listens again when interrupted", async () => {
      stubAudio(false);
      hearInTurn("birinci");
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse({ detail: "x" }, 502),
        "/api/transcribe": () => jsonResponse({ text: "soru" }),
        "/api/ask": () =>
          sse([{ type: "item_audio", index: 0, audio: btoa("ses"), mime: "audio/wav" }, answered]),
      });
      await open(fetchMock);

      fireEvent.click(await screen.findByRole("button", { name: "Sözünü kes" }));

      await waitFor(() => expect(listening.listen).toHaveBeenCalledTimes(2));
    });

    it("stops speaking and takes the new question when the user talks over it", async () => {
      stubAudio(false);
      hearInTurn("birinci");
      const pause = vi.spyOn(window.HTMLMediaElement.prototype, "pause");
      let bargeIn: () => void = () => undefined;
      let finishRecording: (audio: Blob) => void = () => undefined;
      listening.barge.mockImplementationOnce(
        (_mic: unknown, _session: unknown, _done: unknown, onBargeIn: () => void) =>
          new Promise((resolve) => {
            bargeIn = onBargeIn;
            finishRecording = resolve;
          }),
      );
      const transcripts = ["ilk soru", "araya giren soru"];
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/voice/phrases": () => jsonResponse({ detail: "x" }, 502),
        "/api/transcribe": () => jsonResponse({ text: transcripts.shift() ?? "" }),
        "/api/ask": () =>
          sse([{ type: "item_audio", index: 0, audio: btoa("ses"), mime: "audio/wav" }, answered]),
      });
      await open(fetchMock);
      await waitFor(() => expect(askBodiesOf(fetchMock)).toHaveLength(1));
      await screen.findByText("Konuşuyorum");
      pause.mockClear();

      bargeIn();
      expect(pause).toHaveBeenCalled();
      expect(await screen.findByText("Dinliyorum")).toBeInTheDocument();
      finishRecording(new Blob(["araya"], { type: "audio/webm" }));

      await waitFor(() => expect(askBodiesOf(fetchMock)).toHaveLength(2));
      expect(askBodiesOf(fetchMock)[1].question).toBe("araya giren soru");
      expect(listening.listen).toHaveBeenCalledTimes(1);
      pause.mockRestore();
    });

    it("releases a microphone that opens after the user has already left", async () => {
      stubAudio();
      let finishOpening: (mic: object) => void = () => undefined;
      listening.open.mockReturnValue(
        new Promise((resolve) => {
          finishOpening = resolve;
        }),
      );
      await open(conversationApi([]));

      fireEvent.click(screen.getByRole("button", { name: "Bitir" }));
      finishOpening({ stream: {}, level: () => 0, close: listening.close });

      await waitFor(() => expect(listening.close).toHaveBeenCalled());
      expect(listening.listen).not.toHaveBeenCalled();
    });

    it("explains when the microphone cannot be opened", async () => {
      stubAudio();
      listening.open.mockRejectedValue(new Error("izin yok"));
      const fetchMock = conversationApi([]);

      await open(fetchMock);

      expect(await screen.findByRole("alert")).toHaveTextContent("Mikrofona erişilemedi");
      expect(listening.listen).not.toHaveBeenCalled();
    });
  });

  describe("microphone", () => {
    it("puts the transcript in the box and does not send it", async () => {
      const stopTrack = stubBrowserRecording();
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/transcribe": () => jsonResponse({ text: "NT1162 bel kaç" }),
      });
      render(<App />);

      fireEvent.click(screen.getByRole("button", { name: "Konuşarak sor" }));
      fireEvent.click(await screen.findByRole("button", { name: "Kaydı bitir" }));

      await waitFor(() => expect(screen.getByLabelText("Sorunuz")).toHaveValue("NT1162 bel kaç"));
      expect(stopTrack).toHaveBeenCalled();
      expect(fetchMock.mock.calls.some(([url]) => String(url) === "/api/ask")).toBe(false);
    });

    it("marks a dictated question as spoken, and the next typed one as written", async () => {
      stubBrowserRecording();
      const fetchMock = stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/transcribe": () => jsonResponse({ text: "PNT-1162 bel kaç" }),
        "/api/ask": () => sse([answered]),
      });
      const askBodies = (mock: typeof fetchMock) =>
        mock.mock.calls
          .filter(([url]) => String(url) === "/api/ask")
          .map(([, init]) => JSON.parse(String(init?.body)));
      render(<App />);

      fireEvent.click(screen.getByRole("button", { name: "Konuşarak sor" }));
      fireEvent.click(await screen.findByRole("button", { name: "Kaydı bitir" }));
      await waitFor(() => expect(screen.getByLabelText("Sorunuz")).toHaveValue("PNT-1162 bel kaç"));
      fireEvent.click(screen.getByRole("button", { name: "Sor" }));
      await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(1));
      fireEvent.change(screen.getByLabelText("Sorunuz"), { target: { value: "elle yazılan" } });
      fireEvent.click(await screen.findByRole("button", { name: "Sor" }));

      await waitFor(() => expect(askBodies(fetchMock)).toHaveLength(2));
      expect(askBodies(fetchMock)[0]).toEqual({ question: "PNT-1162 bel kaç", input_mode: "voice" });
      expect(askBodies(fetchMock)[1]).toEqual({ question: "elle yazılan" });
    });

    it("explains a failed transcription", async () => {
      stubBrowserRecording();
      stubApi({
        "/api/documents": () => jsonResponse([]),
        "/api/transcribe": () => jsonResponse({ detail: "x" }, 502),
      });
      render(<App />);

      fireEvent.click(screen.getByRole("button", { name: "Konuşarak sor" }));
      fireEvent.click(await screen.findByRole("button", { name: "Kaydı bitir" }));

      expect(await screen.findByRole("alert")).toHaveTextContent("yazıya çevrilemedi");
    });

    it("hides the button where the browser cannot record", async () => {
      vi.stubGlobal("MediaRecorder", undefined);
      stubApi({ "/api/documents": () => jsonResponse([]) });
      render(<App />);

      expect(await screen.findByRole("button", { name: "Sor" })).toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Konuşarak sor" })).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Konuşma modu" })).not.toBeInTheDocument();
    });
  });
});

describe("citationLabel", () => {
  const pageless = { page: null, boxes: [], sheet: null, row: null };

  it("is the readable name from the server with the page", () => {
    expect(citationLabel(CITATION)).toBe("PNT-4417 ölçü föyü · s.2");
  });

  it("gives the row of a spreadsheet source", () => {
    const location = { ...pageless, sheet: "Ölçüler", row: 5 };

    expect(citationLabel({ ...CITATION, title: "Ölçü föyü", location })).toBe(
      "Ölçü föyü · satır 5",
    );
    expect(citationDetail({ ...CITATION, title: "Ölçü föyü", location })).toBe(
      "Ölçü föyü · Ölçüler · satır 5",
    );
  });

  it("leaves the section path to the detail", () => {
    const citation = {
      ...CITATION,
      title: "Ayarlar",
      location: { ...pageless, section: "Ayarlar · Genel · Hafta numaraları" },
    };

    expect(citationLabel(citation)).toBe("Ayarlar");
    expect(citationDetail(citation)).toBe("Ayarlar · Genel · Hafta numaraları");
  });

  it("keeps a section path that starts with another name in the detail", () => {
    const citation = { ...CITATION, title: "Kılavuz", location: { ...pageless, section: "Genel" } };

    expect(citationDetail(citation)).toBe("Kılavuz · Genel");
  });

  it("shows only the title when there is no location", () => {
    expect(citationLabel({ ...CITATION, title: "Notlar", location: pageless })).toBe("Notlar");
    expect(citationDetail({ ...CITATION, title: "Notlar", location: pageless })).toBe("Notlar");
  });
});

describe("layout", () => {
  const DOCUMENTS = [
    { doc_id: "p", title: "Föy", filename: "foy.pdf", status: "ready", error: null, report: null },
    { doc_id: "w", title: "Notlar", filename: "notlar.docx", status: "ready", error: null, report: null },
    { doc_id: "g", title: "Foto", filename: "foto.jpg", status: "queued", error: null, report: null },
    ...Array.from({ length: 12 }, (_, index) => ({
      doc_id: `m${index}`,
      title: `Kılavuz ${index}`,
      filename: `k${index}.md`,
      status: "ready",
      error: null,
      report: null,
    })),
  ];

  it("starts on the landing screen and moves to the conversation with the first question", async () => {
    stubApi({ "/api/documents": () => jsonResponse([]), "/api/ask": () => sse([answered]) });
    render(<App />);

    expect(screen.getByRole("heading", { name: "Belgelerinize sorun." })).toBeInTheDocument();
    await ask("PNT-4417 iç paça kaç?");

    expect(await screen.findByText("İç paça 76,5 cm.")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Belgelerinize sorun." })).not.toBeInTheDocument();
    expect(screen.getByText("PNT-4417 iç paça kaç?")).toBeInTheDocument();
  });

  it("keeps the documents drawer closed until asked, then closes it with Escape", async () => {
    stubApi({ "/api/documents": () => jsonResponse(DOCUMENTS) });
    render(<App />);
    const opener = await screen.findByRole("button", { name: "Belgeler (15)" });

    expect(screen.queryByRole("list", { name: "Belgeler" })).not.toBeInTheDocument();
    opener.focus();
    fireEvent.click(opener);
    const drawer = screen.getByRole("complementary", { name: "Belgeler" });
    expect(drawer).toHaveFocus();
    expect(screen.getByRole("list", { name: "Belgeler" })).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });

    expect(screen.queryByRole("list", { name: "Belgeler" })).not.toBeInTheDocument();
    expect(opener).toHaveFocus();
  });

  it("closes the documents drawer on a click outside it", async () => {
    stubApi({ "/api/documents": () => jsonResponse(DOCUMENTS) });
    render(<App />);
    openDocuments();

    fireEvent.click(screen.getByTestId("drawer-backdrop"));

    expect(screen.queryByRole("list", { name: "Belgeler" })).not.toBeInTheDocument();
  });

  it("groups documents by file type and folds the crowded group", async () => {
    stubApi({ "/api/documents": () => jsonResponse(DOCUMENTS) });
    render(<App />);
    openDocuments();

    await screen.findByRole("button", { name: "PDF (1)" });
    const list = screen.getByRole("list", { name: "Belgeler" });
    const open = within(list).getAllByRole("button", { expanded: true });
    expect(open.map((button) => button.getAttribute("aria-label"))).toEqual([
      "PDF (1)",
      "Word (1)",
      "Görsel (1)",
    ]);
    const markdown = screen.getByRole("button", { name: "Markdown (12)" });
    expect(markdown).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("list", { name: "Markdown" })).not.toBeInTheDocument();

    fireEvent.click(markdown);

    expect(within(screen.getByRole("list", { name: "Markdown" })).getAllByRole("listitem")).toHaveLength(12);
  });

  it("labels only documents that need attention", async () => {
    stubApi({ "/api/documents": () => jsonResponse(DOCUMENTS) });
    render(<App />);
    openDocuments();

    expect(await screen.findByText("Kuyrukta")).toBeInTheDocument();
    expect(screen.queryByText("Hazır")).not.toBeInTheDocument();
  });

  it("stops a running question with the stop button", async () => {
    let aborted = false;
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": (_url, init) =>
        new Response(
          new ReadableStream({
            start(controller) {
              init?.signal?.addEventListener("abort", () => {
                aborted = true;
                controller.error(new DOMException("Durduruldu", "AbortError"));
              });
            },
          }),
          { headers: { "Content-Type": "text/event-stream" } },
        ),
    });
    render(<App />);
    await ask("uzun soru");

    fireEvent.click(await screen.findByRole("button", { name: "Durdur" }));

    expect(await screen.findByText("Soru durduruldu.")).toBeInTheDocument();
    expect(aborted).toBe(true);
    expect(screen.getByRole("button", { name: "Sor" })).toBeInTheDocument();
  });

  it("shows how a question was understood only when it differs from what was typed", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([{ type: "resolved", question: "PNT-4417 iç paça kaç?" }, answered]),
    });
    render(<App />);
    await ask("PNT-4417 iç paça kaç?");

    await screen.findByText("İç paça 76,5 cm.");
    expect(screen.queryByText(/Anlaşılan soru/)).not.toBeInTheDocument();
  });

  it("closes only the drawer opened last with Escape", async () => {
    stubApi({
      "/api/documents": () => jsonResponse(DOCUMENTS),
      "/api/ask": () => sse([answered]),
      "/api/chunks/d1%3A0/source": () =>
        jsonResponse({ kind: "text", text: "Beden: M", section: null }),
    });
    render(<App />);
    await ask("soru");
    fireEvent.click(await screen.findByRole("button", { name: "PNT-4417 ölçü föyü · s.2" }));
    await screen.findByText("Beden: M");
    openDocuments();

    fireEvent.keyDown(document, { key: "Escape" });

    expect(screen.queryByRole("list", { name: "Belgeler" })).not.toBeInTheDocument();
    expect(screen.getByText("Beden: M")).toBeInTheDocument();
  });

  it("closes the source drawer with Escape", async () => {
    stubApi({
      "/api/documents": () => jsonResponse([]),
      "/api/ask": () => sse([answered]),
      "/api/chunks/d1%3A0/source": () =>
        jsonResponse({ kind: "text", text: "Beden: M", section: null }),
    });
    render(<App />);
    await ask("soru");
    fireEvent.click(await screen.findByRole("button", { name: "PNT-4417 ölçü föyü · s.2" }));
    expect(await screen.findByText("Beden: M")).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });

    expect(screen.queryByText("Beden: M")).not.toBeInTheDocument();
  });
});

describe("landing actions", () => {
  const ready = { title: "Föy", filename: "foy.pdf", status: "ready", error: null, report: null };

  it("focuses the question box from the write card", async () => {
    stubApi({ "/api/documents": () => jsonResponse([]) });
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /Yazarak sor/ }));

    expect(screen.getByLabelText("Sorunuz")).toHaveFocus();
  });

  it("opens the documents drawer and the file picker from the add card", async () => {
    stubApi({ "/api/documents": () => jsonResponse([]) });
    render(<App />);
    const picker = vi.spyOn(HTMLInputElement.prototype, "click");

    fireEvent.click(screen.getByRole("button", { name: /Belge ekle/ }));

    expect(screen.getByRole("list", { name: "Belgeler" })).toBeInTheDocument();
    expect(picker).toHaveBeenCalledTimes(1);
    expect(picker.mock.contexts[0]).toBe(screen.getByLabelText("Belge yükle"));
  });

  it("shows the document state and opens the drawer when something failed", async () => {
    stubApi({
      "/api/documents": () =>
        jsonResponse([
          { ...ready, doc_id: "a" },
          { ...ready, doc_id: "b" },
          { ...ready, doc_id: "c", status: "processing" },
          { ...ready, doc_id: "d", status: "failed", error: "Belge işlenemedi." },
        ]),
    });
    render(<App />);

    const card = await screen.findByRole("button", {
      name: "2 belge hazır, 1 işleniyor, 1 hata. Belgeleri aç",
    });
    fireEvent.click(card);

    expect(screen.getByRole("list", { name: "Belgeler" })).toBeInTheDocument();
  });

  it("shows a plain state line when nothing failed", async () => {
    stubApi({ "/api/documents": () => jsonResponse([{ ...ready, doc_id: "a" }]) });
    render(<App />);

    expect(await screen.findByRole("status")).toHaveTextContent("1 belge hazır");
    expect(screen.queryByText(/hata/)).not.toBeInTheDocument();
  });

  it("leaves the landing actions once a question is asked", async () => {
    stubApi({ "/api/documents": () => jsonResponse([]), "/api/ask": () => sse([answered]) });
    render(<App />);
    await ask("soru");

    await screen.findByText("İç paça 76,5 cm.");
    expect(screen.queryByRole("button", { name: /Yazarak sor/ })).not.toBeInTheDocument();
  });

  it("keeps the source quote of a hidden sentence apart from the hidden-sentence notice", async () => {
    const hidden = {
      ...answered,
      result: {
        ...answered.result,
        status: "failed",
        items: [
          { ...answered.result.items[0], verified: false, source_quote: "L: 42,5" },
          { ...answered.result.items[0], verified: false, source_quote: null },
        ],
      },
    };
    stubApi({ "/api/documents": () => jsonResponse([]), "/api/ask": () => sse([hidden]) });
    render(<App />);
    await ask("soru");

    expect(await screen.findByText("Doğrulanamadı")).toBeInTheDocument();
    expect(screen.getByText('Kaynakta yazan: "L: 42,5"')).toHaveClass("source-quote");
    expect(screen.getByText(/doğrulanamadığı için gösterilmiyor/)).toHaveClass("hidden-note");
  });
});
