const services = [
  "Brand Identity",
  "Editorial",
  "Type Design",
  "Motion",
  "Web Design",
  "Art Direction",
  "Wayfinding",
  "Industrial",
];

function Star() {
  return (
    <svg
      width="36"
      height="36"
      viewBox="0 0 36 36"
      className="shrink-0"
      aria-hidden
    >
      <path
        d="M18 2 L20 16 L34 18 L20 20 L18 34 L16 20 L2 18 L16 16 Z"
        fill="currentColor"
      />
    </svg>
  );
}

export default function Marquee() {
  const items = [...services, ...services];
  return (
    <section
      aria-hidden
      className="overflow-hidden border-y border-ink/15 py-7 md:py-10"
    >
      <div className="marquee-track flex w-max items-center gap-10 whitespace-nowrap font-display text-[12vw] leading-none tracking-[-0.03em] text-ink md:text-[8vw]">
        {items.map((s, i) => (
          <span key={i} className="flex items-center gap-10">
            <span className={i % 2 ? "italic font-extralight" : "font-normal"}>
              {s}
            </span>
            <Star />
          </span>
        ))}
      </div>
    </section>
  );
}
