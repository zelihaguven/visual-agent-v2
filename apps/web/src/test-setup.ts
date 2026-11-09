import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

window.HTMLMediaElement.prototype.play = async () => undefined;
window.HTMLMediaElement.prototype.pause = () => undefined;
