import {
  useEffect,
  useLayoutEffect,
  useRef,
  useSyncExternalStore,
  type KeyboardEvent,
  type ReactNode,
} from "react";

// App.tsx'teki WORKSPACE_QUERY ile aynı: geniş ekranda çekmece sayfanın parçasıdır, modal değildir.
const WORKSPACE_QUERY = "(min-width: 1080px)";
// İçeriğin kademeli girişi (documents.css) bu süre boyunca açıktır; sonra yeniden çizimde tekrarlanmaz.
const OPENING_MS = 400;
const FOCUSABLE =
  'button:not(:disabled), input:not(:disabled), a[href], select, textarea, [tabindex]:not([tabindex="-1"])';

// Açık çekmeceler açılış sırasıyla; Escape yalnız en üsttekini kapatır.
const openDrawers: symbol[] = [];

function subscribeToWorkspace(onChange: () => void): () => void {
  const query = window.matchMedia?.(WORKSPACE_QUERY);
  query?.addEventListener("change", onChange);
  return () => query?.removeEventListener("change", onChange);
}

function isWorkspace(): boolean {
  return window.matchMedia?.(WORKSPACE_QUERY).matches ?? false;
}

type Props = {
  isOpen: boolean;
  side: "left" | "right";
  label: string;
  onClose: () => void;
  children: ReactNode;
};

/**
 * Yandan açılan panel. Dar ekranda modaldır: odak panele geçer, Tab panelin içinde döner,
 * dışına tıklayınca ya da Escape ile kapanır ve odak açan öğeye döner. Geniş ekranda sayfanın
 * parçasıdır: odağı yalnız kullanıcı açtıysa alır, Escape yalnız odak içindeyken kapatır.
 * Kapalıyken içerik DOM'da kalır (gizli): içindeki yoklama sürer.
 */
export function Drawer({ isOpen, side, label, onClose, children }: Props) {
  const panel = useRef<HTMLElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  const close = useRef(onClose);
  close.current = onClose;
  const key = useRef(Symbol("drawer"));
  const isModal = !useSyncExternalStore(subscribeToWorkspace, isWorkspace, () => false);
  const modal = useRef(isModal);
  modal.current = isModal;

  // Boyamadan önce işaretlenir: içerik bir kare görünüp sonra kaybolmaz.
  useLayoutEffect(() => {
    const element = panel.current;
    if (!isOpen || element === null) {
      return;
    }
    element.dataset.opening = "";
    const timer = window.setTimeout(() => delete element.dataset.opening, OPENING_MS);
    return () => {
      window.clearTimeout(timer);
      delete element.dataset.opening;
    };
  }, [isOpen]);

  useEffect(() => {
    const element = panel.current;
    if (!isOpen || element === null) {
      return;
    }
    const self = key.current;
    openDrawers.push(self);
    opener.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    // Geniş ekranda sayfa açılırken panel kendiliğinden açık gelir; odak soru akışından çalınmaz.
    if (modal.current || document.activeElement !== document.body) {
      element.focus();
    }
    const onKey = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") {
        return;
      }
      const isTarget = modal.current
        ? openDrawers.at(-1) === self
        : element.contains(document.activeElement);
      if (isTarget) {
        close.current();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      openDrawers.splice(openDrawers.indexOf(self), 1);
      // Açan öğe bu arada kalktıysa (yeni tur) odak soru kutusuna döner.
      const target = opener.current?.isConnected
        ? opener.current
        : document.getElementById("question");
      target?.focus();
    };
  }, [isOpen]);

  // Modal çekmecede Tab arkadaki sayfaya kaçmaz; uçlarda başa ya da sona döner.
  function keepFocusInside(event: KeyboardEvent<HTMLElement>) {
    if (!isModal || event.key !== "Tab" || panel.current === null) {
      return;
    }
    const items = [...panel.current.querySelectorAll<HTMLElement>(FOCUSABLE)].filter(
      (item) => item.closest("[hidden]") === null,
    );
    const first = items[0];
    const last = items.at(-1);
    if (first === undefined || last === undefined) {
      return;
    }
    const active = document.activeElement;
    if (event.shiftKey && (active === first || active === panel.current)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <>
      {isOpen && isModal && (
        <div className="drawer-backdrop" data-testid="drawer-backdrop" onClick={onClose} />
      )}
      <section
        ref={panel}
        className={`drawer is-${side}`}
        role={isModal ? "dialog" : "complementary"}
        aria-modal={isModal || undefined}
        aria-label={label}
        tabIndex={-1}
        hidden={!isOpen}
        onKeyDown={keepFocusInside}
      >
        {children}
      </section>
    </>
  );
}
