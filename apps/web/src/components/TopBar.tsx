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
        <span className="brand">Visual Agent</span>
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
        Belgeler{documentCount !== null && <span className="count">{documentCount}</span>}
      </button>
    </header>
  );
}
