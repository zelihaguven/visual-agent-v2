import { useEffect, useRef, type ReactNode } from "react";

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

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    opener.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    panel.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close.current();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      opener.current?.focus();
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
