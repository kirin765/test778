"use client";

import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "motion/react";

export default function Cursor() {
  const x = useMotionValue(-200);
  const y = useMotionValue(-200);
  const sx = useSpring(x, { stiffness: 600, damping: 50, mass: 0.4 });
  const sy = useSpring(y, { stiffness: 600, damping: 50, mass: 0.4 });
  const [label, setLabel] = useState<string | null>(null);
  const [hidden, setHidden] = useState(true);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      x.set(e.clientX);
      y.set(e.clientY);
      if (hidden) setHidden(false);
      const target = e.target as HTMLElement | null;
      const cur = target?.closest("[data-cursor]") as HTMLElement | null;
      const next = cur?.dataset.cursor ?? null;
      setLabel((prev) => (prev === next ? prev : next));
    };
    const onLeave = () => setHidden(true);
    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("mouseleave", onLeave);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseleave", onLeave);
    };
  }, [x, y, hidden]);

  return (
    <motion.div
      aria-hidden
      className="pointer-events-none fixed left-0 top-0 z-[60] hidden md:block"
      style={{ x: sx, y: sy }}
    >
      <motion.div
        className="relative -translate-x-1/2 -translate-y-1/2 flex items-center justify-center rounded-full bg-ink text-cream"
        animate={{
          width: label ? 96 : 10,
          height: label ? 96 : 10,
          opacity: hidden ? 0 : 1,
        }}
        transition={{ type: "spring", stiffness: 280, damping: 26 }}
      >
        {label && (
          <motion.span
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="font-mono text-[10px] uppercase tracking-[0.2em]"
          >
            {label}
          </motion.span>
        )}
      </motion.div>
    </motion.div>
  );
}
