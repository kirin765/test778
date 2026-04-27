export default function Approach() {
  return (
    <section
      id="approach"
      className="relative grid grid-cols-12 gap-6 px-6 py-28 md:px-10 md:py-44"
    >
      <div className="col-span-12 md:col-span-3">
        <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
          (Approach — 02)
        </div>
        <div className="diag mt-6 hidden h-12 w-32 md:block" aria-hidden />
      </div>

      <div className="col-span-12 space-y-12 md:col-span-9">
        <p className="font-display text-3xl leading-[1.15] tracking-[-0.015em] md:text-[3.2rem]">
          We work with a small number of clients each year. The work is{" "}
          <em className="font-extralight italic">slow</em>, deliberate, and made
          entirely in-house — from the first sketch to the final pixel.
        </p>

        <div className="grid grid-cols-12 gap-6">
          <p className="col-span-12 max-w-2xl font-display text-xl italic leading-relaxed text-ink/80 md:col-span-7 md:text-2xl">
            No process decks. No moodboards as a service. Just considered,
            well-made things — for the kind of brands that prefer a long
            conversation to a fast pitch.
          </p>

          <ul className="col-span-12 space-y-3 font-mono text-[11px] uppercase tracking-[0.22em] text-ink/70 md:col-span-4 md:col-start-9">
            <li className="flex items-baseline gap-3">
              <span className="text-ink/40">A.</span>
              <span>Two engagements per quarter, never more.</span>
            </li>
            <li className="flex items-baseline gap-3">
              <span className="text-ink/40">B.</span>
              <span>One studio, one brief, one estimate.</span>
            </li>
            <li className="flex items-baseline gap-3">
              <span className="text-ink/40">C.</span>
              <span>No retainer work; no subcontracting.</span>
            </li>
            <li className="flex items-baseline gap-3">
              <span className="text-ink/40">D.</span>
              <span>We charge by the kilo of attention.</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
