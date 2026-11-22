import { Icon } from "./Icon";

type Props = {
  isLanding: boolean;
  documentCount: number | null;
  isLibraryOpen: boolean;
  onHome: () => void;
  onOpenLibrary: () => void;
};

/** Üst çubuk: açılışta marka, sohbette ana sayfaya dönüş; sağda belgeler ve sayısı. */
export function TopBar({ isLanding, documentCount, isLibraryOpen, onHome, onOpenLibrary }: Props) {
  return (
    <header className="topbar">
      {isLanding ? (
        <span className="brand">
          <svg className="brand-mark" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M12 1.5c.9 6.3 4.2 9.6 10.5 10.5-6.3.9-9.6 4.2-10.5 10.5C11.1 16.2 7.8 12.9 1.5 12 7.8 11.1 11.1 7.8 12 1.5Z" />
          </svg>
          <span>
            Visual <span className="brand-soft">Agent</span>
          </span>
        </span>
      ) : (
        <button
          type="button"
          className="home-button"
          aria-label="Ana Sayfaya Dön"
          title="Ana Sayfaya Dön"
          onClick={onHome}
        >
          <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
            <path fill="currentColor" d="M12 3 2 11.5h3V21h5.5v-6h3v6H19v-9.5h3L12 3Z" />
          </svg>
          Ana Sayfa
        </button>
      )}
      <button
        type="button"
        className="library-button"
        aria-label={documentCount === null ? "Belgeler" : `Belgeler (${documentCount})`}
        aria-expanded={isLibraryOpen}
        onClick={onOpenLibrary}
      >
        <Icon name="folder" />
        Belgeler{documentCount !== null && <span className="count">{documentCount}</span>}
      </button>
    </header>
  );
}
