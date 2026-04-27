import Clock from "./Clock";

export default function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 mix-blend-difference">
      <div className="flex items-center justify-between px-6 py-5 md:px-10 text-cream">
        <a
          href="#top"
          data-cursor="Top"
          className="font-display text-2xl font-light tracking-tight"
        >
          Atelier&nbsp;Oblique
          <sup className="ml-0.5 font-mono text-[9px] tracking-widest">®</sup>
        </a>

        <nav className="hidden gap-9 font-mono text-[11px] uppercase tracking-[0.22em] md:flex">
          <a href="#work" data-cursor="Index">(Work)</a>
          <a href="#approach" data-cursor="Read">(Approach)</a>
          <a href="#contact" data-cursor="Send">(Contact)</a>
        </nav>

        <div className="hidden items-center gap-6 font-mono text-[11px] uppercase tracking-[0.22em] md:flex">
          <span>Lisbon ↔ Seoul</span>
          <Clock />
        </div>

        <button
          aria-label="Open menu"
          data-cursor="Menu"
          className="md:hidden font-mono text-[11px] uppercase tracking-[0.22em]"
        >
          Menu
        </button>
      </div>
    </header>
  );
}
