import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { applyEvent, newTurn } from "./turn";

const listening = vi.hoisted(() => ({
  open: vi.fn(),
  listen: vi.fn(),
  close: vi.fn(),
}));

vi.mock("./listening", async (original) => ({
  ...(await original<typeof import("./listening")>()),
  openMicrophone: listening.open,
  listenForUtterance: listening.listen,
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
        from_figure: false,
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
      from_figure: false, has_code: false,
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
      from_figure: false, has_code: false,
    });
    turn = applyEvent(turn, { type: "item_stream", index: 0, text: "▒▒▒" });

    expect(turn.items[0].text).toBe("76,5");
  });

  it("clears streamed items when the provider is switched", () => {
    let turn = newTurn("1", "soru");
    turn = applyEvent(turn, { type: "item_stream", index: 0, text: "Metin" });

    expect(applyEvent(turn, { type: "reset" }).items).toEqual({});
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
            from_figure: false, has_code: false,
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

    fireEvent.click(await screen.findByRole("button", { name: /Ölçüler · satır 5/ }));

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
            result: { kind: "not_found", reason: "", suggested_doc_ids: [] },
          },
        ]),
    });
    render(<App />);
    await ask("soru");

    expect(await screen.findByText("Bu bilgi belgelerde bulunamadı.")).toBeInTheDocument();
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

    const list = await screen.findByRole("list", { name: "Belgeler" });
    expect(within(list).getByText("İşleniyor")).toBeInTheDocument();
    expect(within(list).getByText("Belge işlenemedi.")).toBeInTheDocument();
  });

  it("uploads a file and shows the server's rejection reason", async () => {
    const fetchMock = stubApi({
      "/api/documents": (_url, init) =>
        init?.method === "POST"
          ? jsonResponse({ detail: "virus.exe: bu dosya türü desteklenmiyor" }, 415)
          : jsonResponse([]),
    });
    render(<App />);

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
            result: { kind: "not_found", reason: "", suggested_doc_ids: [] },
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

    it("plays a waiting phrase right after the user stops talking", async () => {
      const create = stubAudio();
      hearInTurn("birinci");
      const fetchMock = conversationApi(["soru"]);

      await open(fetchMock);

      await waitFor(() => expect(askBodiesOf(fetchMock)).toHaveLength(1));
      await waitFor(() => expect(create.mock.calls.length).toBeGreaterThanOrEqual(3));
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
