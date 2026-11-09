const SILENCE =
  "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=";

function toObjectUrl(audio: string, mime: string): string {
  const bytes = Uint8Array.from(atob(audio), (character) => character.charCodeAt(0));
  return URL.createObjectURL(new Blob([bytes], { type: mime }));
}

/** Cümleler geldikleri sırayla, biri bitince diğeri çalınır. */
export class AudioQueue {
  private readonly player = new Audio();
  private pending: string[] = [];
  private current: string | null = null;
  private waiters: (() => void)[] = [];

  constructor() {
    this.player.onended = () => this.playNext();
    this.player.onerror = () => this.playNext();
  }

  /** Tablet tarayıcıları sesi yalnız kullanıcı dokunuşundan sonra açar. */
  unlock(): void {
    this.player.src = SILENCE;
    void this.player.play().catch(() => undefined);
  }

  enqueue(audio: string, mime: string): void {
    this.pending = [...this.pending, toObjectUrl(audio, mime)];
    if (this.current === null) {
      this.playNext();
    }
  }

  stop(): void {
    this.player.pause();
    this.pending.forEach((url) => URL.revokeObjectURL(url));
    this.pending = [];
    this.release();
    this.notifyIdle();
  }

  /** Sıradaki bütün sesler bitince ya da durdurulunca tamamlanır. */
  whenIdle(): Promise<void> {
    if (this.current === null && this.pending.length === 0) {
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      this.waiters = [...this.waiters, resolve];
    });
  }

  private notifyIdle(): void {
    const waiters = this.waiters;
    this.waiters = [];
    waiters.forEach((resolve) => resolve());
  }

  private release(): void {
    if (this.current !== null) {
      URL.revokeObjectURL(this.current);
      this.current = null;
    }
  }

  private playNext(): void {
    this.release();
    const [next, ...rest] = this.pending;
    if (next === undefined) {
      this.notifyIdle();
      return;
    }
    this.pending = rest;
    this.current = next;
    this.player.src = next;
    void this.player.play().catch(() => this.playNext());
  }
}
