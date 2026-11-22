const PATHS = {
  close: ["M6 6l12 12", "M18 6 6 18"],
  refresh: ["M20 11a8 8 0 1 0-2.3 5.7", "M20 4v7h-7"],
  trash: ["M4 7h16", "M9 7V4h6v3", "M6 7l1 13h10l1-13", "M10 11v6", "M14 11v6"],
  plus: ["M12 5v14", "M5 12h14"],
  folder: ["M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"],
  search: ["M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14Z", "M20 20l-3.5-3.5"],
};

export type IconName = keyof typeof PATHS;

/** Düğme yazısını destekleyen çizgi simge; renk metinden gelir, ekran okuyucuya okunmaz. */
export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
