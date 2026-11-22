import { useEffect, useId, useRef, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";

type Props = {
  title: string;
  body: string;
  confirmLabel: string;
  /** Geri alınamayan işlem (silme): onay düğmesi uyarı renginde. */
  isDanger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

/**
 * Geri dönüşü pahalı işlemler için onay penceresi. Sayfanın köküne çizilir (çekmecenin kayma
 * dönüşümü içindeki sabit konumlu öğeyi kendi kutusuna hapsederdi). Odak "Vazgeç"te başlar:
 * Enter'a yanlışlıkla basmak işlemi başlatmaz. Kapanınca odak açan düğmeye döner.
 */
export function ConfirmDialog({ title, body, confirmLabel, isDanger, onConfirm, onCancel }: Props) {
  const titleId = useId();
  const bodyId = useId();
  const cancel = useRef<HTMLButtonElement>(null);
  const confirm = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    cancel.current?.focus();
    return () => {
      if (opener?.isConnected) {
        opener.focus();
      }
    };
  }, []);

  // Tuşlar pencerede kalır: Escape arkadaki çekmeceyi kapatmaz, Tab iki düğme arasında döner.
  function handleKey(event: KeyboardEvent<HTMLDivElement>) {
    event.stopPropagation();
    if (event.key === "Escape") {
      onCancel();
    } else if (event.key === "Tab") {
      event.preventDefault();
      const next = document.activeElement === cancel.current ? confirm.current : cancel.current;
      next?.focus();
    }
  }

  return createPortal(
    <div className="confirm-backdrop" data-testid="confirm-backdrop" onClick={onCancel}>
      <div
        className="confirm"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={bodyId}
        onClick={(event) => event.stopPropagation()}
        onKeyDown={handleKey}
      >
        <h2 id={titleId}>{title}</h2>
        <p id={bodyId}>{body}</p>
        <div className="confirm-actions">
          <button ref={cancel} type="button" className="confirm-cancel" onClick={onCancel}>
            Vazgeç
          </button>
          <button
            ref={confirm}
            type="button"
            className={`confirm-accept ${isDanger ? "is-danger" : ""}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
