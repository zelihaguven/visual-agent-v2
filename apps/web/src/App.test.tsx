import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

function stubHealth(response: Partial<Response> | Error) {
  const fetchMock =
    response instanceof Error
      ? vi.fn().mockRejectedValue(response)
      : vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("App", () => {
  it("shows that the service is connected and login is off", async () => {
    const fetchMock = stubHealth({
      ok: true,
      json: async () => ({ status: "ok", auth_enabled: false }),
    });

    render(<App />);

    expect(await screen.findByText("Servis bağlı")).toBeInTheDocument();
    expect(screen.getByText("Giriş kapalı")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/health", expect.anything());
  });

  it("explains what to do when the service returns an error", async () => {
    stubHealth({ ok: false, status: 503 });

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Servise ulaşılamadı. API çalışıyor mu kontrol edin.",
    );
  });

  it("explains what to do when the network request fails", async () => {
    stubHealth(new Error("network down"));

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Servise ulaşılamadı.");
  });
});
