import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  // API, `python -m apps.local` ile açılan adres: kök .env'deki WEB_PORT, yoksa 8080.
  const port = loadEnv(mode, "../..", "WEB_PORT").WEB_PORT || "8080";
  return {
    plugins: [react()],
    server: {
      proxy: { "/api": `http://127.0.0.1:${port}` },
    },
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test-setup.ts"],
    },
  };
});
