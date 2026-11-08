import { useEffect, useState } from "react";

import "./App.css";

type Health = { status: "ok"; auth_enabled: boolean };
type ConnectionState =
  | { kind: "checking" }
  | { kind: "connected"; health: Health }
  | { kind: "failed" };

async function fetchHealth(signal: AbortSignal): Promise<Health> {
  const response = await fetch("/api/health", { signal });
  if (!response.ok) {
    throw new Error(`Sağlık kontrolü başarısız: ${response.status}`);
  }
  return (await response.json()) as Health;
}

export function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    fetchHealth(controller.signal)
      .then((health) => setConnection({ kind: "connected", health }))
      .catch(() => {
        if (!controller.signal.aborted) {
          setConnection({ kind: "failed" });
        }
      });
    return () => controller.abort();
  }, []);

  return (
    <main className="shell">
      <h1>Visual Agent</h1>
      <p className="lede">Belgelerinize sorun, cevabı kaynağıyla görün.</p>
      {connection.kind === "checking" && <p className="status">Servis kontrol ediliyor</p>}
      {connection.kind === "connected" && (
        <p className="status status-ok">
          <span>Servis bağlı</span>
          <span>{connection.health.auth_enabled ? "Giriş açık" : "Giriş kapalı"}</span>
        </p>
      )}
      {connection.kind === "failed" && (
        <p className="status status-error" role="alert">
          Servise ulaşılamadı. API çalışıyor mu kontrol edin.
        </p>
      )}
    </main>
  );
}
