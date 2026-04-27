export default function Contact() {
  return (
    <section id="contact" className="px-6 py-28 md:px-10 md:py-44">
      <div className="flex items-baseline justify-between font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
        <span>(Contact — 04)</span>
        <span className="hidden md:inline">
          Currently accepting two projects for Q3.
        </span>
      </div>

      <a
        href="mailto:studio@atelier-oblique.demo"
        data-cursor="Write"
        className="mt-10 block font-display leading-[0.92] tracking-[-0.045em] text-[13.5vw] md:text-[11vw]"
      >
        studio<span className="opacity-30">@</span>
        <em className="font-extralight italic">atelier</em>
        <span className="opacity-30">.</span>demo
      </a>

      <div className="mt-20 grid grid-cols-12 gap-6 font-mono text-[11px] uppercase tracking-[0.22em] text-ink/70">
        <div className="col-span-6 md:col-span-3 space-y-2">
          <div className="text-ink/40">Lisbon</div>
          <div>
            Rua dos Tipógrafos 14
            <br />
            1100—000 PT
          </div>
        </div>
        <div className="col-span-6 md:col-span-3 space-y-2">
          <div className="text-ink/40">Seoul</div>
          <div>
            123—45 Yeonnam-dong
            <br />
            Mapo-gu, KR
          </div>
        </div>
        <div className="col-span-6 md:col-span-3 space-y-2">
          <div className="text-ink/40">Elsewhere</div>
          <ul className="space-y-1">
            <li>
              <a href="#" data-cursor="↗" className="hover:text-ink">
                Instagram ↗
              </a>
            </li>
            <li>
              <a href="#" data-cursor="↗" className="hover:text-ink">
                Are.na ↗
              </a>
            </li>
            <li>
              <a href="#" data-cursor="↗" className="hover:text-ink">
                Read.cv ↗
              </a>
            </li>
          </ul>
        </div>
        <div className="col-span-6 md:col-span-3 space-y-2">
          <div className="text-ink/40">Field notes</div>
          <p className="leading-relaxed text-ink/70 normal-case tracking-normal font-sans">
            Four times a year. Print only. Worth the postage.
          </p>
          <a
            href="#"
            data-cursor="Subscribe"
            className="inline-block underline underline-offset-[6px] decoration-ink/40 hover:decoration-ink"
          >
            Sign up ↗
          </a>
        </div>
      </div>
    </section>
  );
}
