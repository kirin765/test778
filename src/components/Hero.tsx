export default function Hero() {
  return (
    <section
      id="top"
      className="relative px-6 pt-40 pb-28 md:px-10 md:pt-52 md:pb-40"
    >
      <div className="rise font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
        ✶ &nbsp; Independent design practice — Portfolio demo · MMXXVI
      </div>

      <h1 className="mt-12 font-display leading-[0.88] tracking-[-0.045em] text-[16.5vw] md:text-[14.5vw]">
        <span className="rise rise-2 block">Slow design</span>
        <span className="rise rise-3 block">for patient brands</span>
        <span className="rise rise-4 block">
          and quiet&nbsp;
          <em className="font-extralight italic" style={{ fontVariationSettings: "'opsz' 144" }}>
            things
          </em>
          .
        </span>
      </h1>

      <div className="rise rise-5 mt-16 grid grid-cols-12 items-end gap-6">
        <p className="col-span-12 max-w-md font-display text-lg italic leading-snug text-ink/80 md:col-span-6 md:text-xl">
          A small studio working on identity, editorial, and digital — for the
          few who can afford to wait, and the patient who insist on it.
        </p>

        <div className="col-span-6 md:col-span-3 md:col-start-10 font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
          <div className="text-ink/40">Currently</div>
          <div className="mt-1">2 / 4 slots open · Q3</div>
        </div>

        <div className="col-span-6 md:col-span-3 font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
          <div className="text-ink/40">Scroll</div>
          <div className="mt-1">↓ Selected work</div>
        </div>
      </div>

      {/* Sidebar registration ticks */}
      <div
        aria-hidden
        className="absolute right-6 top-44 hidden flex-col gap-1 font-mono text-[9px] uppercase tracking-[0.2em] text-ink/30 md:flex md:right-10"
      >
        <span>N° 0001</span>
        <span>—</span>
        <span>Folio I</span>
        <span>—</span>
        <span>v.4.27</span>
      </div>
    </section>
  );
}
