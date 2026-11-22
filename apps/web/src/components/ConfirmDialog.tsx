import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";

import { Icon, type IconName } from "./Icon";

/** Kapanış animasyonunun süresi (confirm.css ile aynı); bitince karar üst bileşene bildirilir. */
export const CONFIRM_EXIT_MS = 180;

type Props = {
  title: string;
  body: string;
  confirmLabel: string;
  confirmIcon: IconName;
  /** Geri alınamayan işlem (silme): onay düğmesi uyarı renginde. */
  isDanger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

/**
 * Geri dönüşü pahalı işlemler için onay penceresi; dar ekranda alttan açılan sayfa. Sayfanın
 * köküne çizilir (çekmecenin kayma dönüşümü içindeki sabit konumlu öğeyi kendi kutusuna
 * hapsederdi). Odak "Vazgeç"te başlar: Enter'a yanlışlıkla basmak işlemi başlatmaz. Karar,
 * kapanış animasyonu bittikten sonra bildirilir; kapanınca odak açan düğmeye döner.
 */
export function ConfirmDialog({
  title,
  body,
  confirmLabel,
  confirmIcon,
  isDanger,
  onConfirm,
  onCancel,
}: Props) {
  const titleId = useId();
  const bodyId = useId();
  const cancel = useRef<HTMLButtonElement>(null);
  const confirm = useRef<HTMLButtonElement>(null);
  const [isClosing, setIsClosing] = useState(false);
  const exitTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    cancel.current?.focus();
    return () => {
      window.clearTimeout(exitTimer.current);
      if (opener?.isConnected) {
        opener.focus();
      }
    };
  }, []);

  function close(decide: () => void) {
    if (isClosing) {
      return;
    }
    setIsClosing(true);
    exitTimer.current = window.setTimeout(decide, CONFIRM_EXIT_MS);
  }

  // Tuşlar pencerede kalır: Escape arkadaki çekmeceyi kapatmaz, Tab iki düğme arasında döner.
  function handleKey(event: KeyboardEvent<HTMLDivElement>) {
    event.stopPropagation();
    if (event.key === "Escape") {
      close(onCancel);
    } else if (event.key === "Tab") {
      event.preventDefault();
      const next = document.activeElement === cancel.current ? confirm.current : cancel.current;
      next?.focus();
    }
  }

  return createPortal(
    <div
      className={`confirm-backdrop ${isClosing ? "is-closing" : ""}`}
      data-testid="confirm-backdrop"
      onClick={() => close(onCancel)}
    >
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
          <button
            ref={cancel}
            type="button"
            className="confirm-cancel"
            onClick={() => close(onCancel)}
          >
            <Icon name="close" />
            Vazgeç
          </button>
          <button
            ref={confirm}
            type="button"
            className={`confirm-accept ${isDanger ? "is-danger" : ""}`}
            onClick={() => close(onConfirm)}
          >
            <Icon name={confirmIcon} />
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
