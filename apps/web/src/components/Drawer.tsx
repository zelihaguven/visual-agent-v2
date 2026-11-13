import { useEffect, useRef, type ReactNode } from "react";

// Açık çekmeceler açılış sırasıyla; Escape yalnız en üsttekini kapatır.
const openDrawers: symbol[] = [];

type Props = {
  isOpen: boolean;
  side: "left" | "right";
  label: string;
  onClose: () => void;
  children: ReactNode;
};

/**
 * Yandan açılan panel. Açılınca odak panele geçer; dışına tıklayınca ya da Escape ile kapanır
 * ve odak açan öğeye döner. Kapalıyken içerik DOM'da kalır (gizli): içindeki yoklama sürer.
 */
export function Drawer({ isOpen, side, label, onClose, children }: Props) {
  const panel = useRef<HTMLElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  const close = useRef(onClose);
  close.current = onClose;
  const key = useRef(Symbol("drawer"));

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const self = key.current;
    openDrawers.push(self);
    opener.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    panel.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && openDrawers.at(-1) === self) {
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

  return (
    <>
      {isOpen && <div className="drawer-backdrop" data-testid="drawer-backdrop" onClick={onClose} />}
      <aside
        ref={panel}
        className={`drawer is-${side}`}
        aria-label={label}
        tabIndex={-1}
        hidden={!isOpen}
      >
        {children}
      </aside>
    </>
  );
}
