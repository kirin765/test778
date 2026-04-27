import Clock from "./Clock";

export default function Footer() {
  return (
    <footer className="flex flex-col items-start justify-between gap-3 border-t border-ink/15 px-6 py-6 font-mono text-[10px] uppercase tracking-[0.22em] text-ink/55 md:flex-row md:items-center md:px-10">
      <div>
        © MMXXVI Atelier Oblique — A demo build, not a real studio.
      </div>
      <div className="flex flex-wrap items-center gap-6">
        <span>Status: 2 / 4 slots open</span>
        <span className="hidden md:inline">·</span>
        <span className="flex items-center gap-2">
          <span className="size-1.5 animate-pulse rounded-full bg-clay" />
          <Clock />
        </span>
      </div>
    </footer>
  );
}
