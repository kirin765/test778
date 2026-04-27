type Project = {
  index: string;
  client: string;
  title: string;
  tags: string[];
  year: string;
  gradient: string;
};

const projects: Project[] = [
  {
    index: "01",
    client: "Halcyon Press",
    title: "Editorial system",
    tags: ["Identity", "Editorial", "Typography"],
    year: "MMXXIV",
    gradient: "linear-gradient(135deg,#d6a85c 0%,#6b3f10 100%)",
  },
  {
    index: "02",
    client: "Verdure",
    title: "Direct-to-soil commerce",
    tags: ["Brand", "E-commerce", "Photography"],
    year: "MMXXIV",
    gradient: "linear-gradient(135deg,#4a5d3a 0%,#1c2916 100%)",
  },
  {
    index: "03",
    client: "Norden Acoustics",
    title: "Industrial identity",
    tags: ["Industrial", "Identity", "Web"],
    year: "MMXXIII",
    gradient: "linear-gradient(135deg,#4a5b73 0%,#1a2333 100%)",
  },
  {
    index: "04",
    client: "Maison Lacuna",
    title: "Hospitality program",
    tags: ["Wayfinding", "Print", "Identity"],
    year: "MMXXIII",
    gradient: "linear-gradient(135deg,#d8a39a 0%,#6e2c34 100%)",
  },
  {
    index: "05",
    client: "Astra Mobility",
    title: "Vehicle interface",
    tags: ["Product", "Motion", "Identity"],
    year: "MMXXIII",
    gradient: "linear-gradient(135deg,#2e3548 0%,#6f7ad0 100%)",
  },
  {
    index: "06",
    client: "Quietly Yours",
    title: "Type specimen",
    tags: ["Type design", "Editorial"],
    year: "MMXXII",
    gradient: "linear-gradient(135deg,#d6c7a3 0%,#7a5e2f 100%)",
  },
];

function Row({ p }: { p: Project }) {
  return (
    <a
      href="#"
      data-cursor="View"
      className="group relative block border-t border-ink/15 transition-colors duration-500 hover:border-ink/0"
    >
      <div className="relative z-20 grid grid-cols-12 items-baseline gap-4 px-6 py-7 transition-colors duration-500 group-hover:text-cream md:px-10 md:py-9">
        <span className="col-span-2 md:col-span-1 font-mono text-[11px] tabular-nums tracking-widest text-ink/50 transition-colors duration-500 group-hover:text-cream/60">
          ({p.index})
        </span>
        <h3 className="col-span-10 md:col-span-6 font-display tracking-tight text-3xl md:text-[3.4rem] leading-[1]">
          <span className="font-extralight italic">{p.client}</span>
          <span className="mx-3 opacity-30">/</span>
          <span>{p.title}</span>
        </h3>
        <span className="col-span-7 md:col-span-3 mt-3 md:mt-0 font-mono text-[10.5px] uppercase tracking-[0.2em] text-ink/55 transition-colors duration-500 group-hover:text-cream/70">
          {p.tags.join(" — ")}
        </span>
        <span className="col-span-5 md:col-span-2 mt-3 md:mt-0 text-right font-mono text-[10.5px] tracking-widest text-ink/55 transition-colors duration-500 group-hover:text-cream/70">
          {p.year} ↗
        </span>
      </div>

      {/* Hover ink fill */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-0 origin-bottom scale-y-0 bg-ink transition-transform duration-700 ease-[cubic-bezier(.2,.7,.1,1)] group-hover:scale-y-100"
      />

      {/* Hover media tile */}
      <div
        aria-hidden
        style={{ backgroundImage: p.gradient }}
        className="pointer-events-none absolute right-[6%] top-1/2 z-10 hidden aspect-[3/4] w-[230px] -translate-y-1/2 overflow-hidden opacity-0 shadow-[0_30px_80px_-20px_rgba(0,0,0,0.5)] transition-all duration-700 ease-[cubic-bezier(.2,.7,.1,1)] group-hover:-translate-y-[58%] group-hover:rotate-[2deg] group-hover:opacity-100 md:block"
      >
        <div className="absolute inset-0 grain opacity-40 mix-blend-overlay" style={{ position: "absolute" }} />
        <div className="absolute left-3 top-3 flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.2em] text-cream/85">
          <span className="size-1.5 rounded-full bg-cream/85" />
          <span>{p.client}</span>
        </div>
        <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between font-mono text-[9px] uppercase tracking-[0.2em] text-cream/70">
          <span>Folio · {p.index}</span>
          <span>{p.year}</span>
        </div>
      </div>
    </a>
  );
}

export default function SelectedWork() {
  return (
    <section id="work" className="relative">
      <div className="grid grid-cols-12 items-end gap-6 px-6 pt-24 pb-10 md:px-10 md:pt-36 md:pb-14">
        <div className="col-span-6 md:col-span-3 font-mono text-[11px] uppercase tracking-[0.22em] text-ink/60">
          (Index — 01)
        </div>
        <h2 className="col-span-12 md:col-span-9 font-display text-3xl tracking-tight md:text-5xl">
          <span className="font-extralight italic">Selected</span> work,
          arranged not by date but by patience required.
        </h2>
      </div>

      <div className="border-b border-ink/15">
        {projects.map((p) => (
          <Row key={p.index} p={p} />
        ))}
      </div>

      <div className="flex items-center justify-between px-6 py-6 font-mono text-[10px] uppercase tracking-[0.22em] text-ink/50 md:px-10">
        <span>End of folio · 06 / 06</span>
        <a href="#" data-cursor="Archive" className="underline-offset-4 hover:underline">
          → Full archive (2019—2026)
        </a>
      </div>
    </section>
  );
}
