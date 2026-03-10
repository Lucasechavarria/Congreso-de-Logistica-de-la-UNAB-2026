import * as React from "react";
import type { LogoItem } from "./data/logos";

type Direction = "ltr" | "rtl";

interface LogoMarqueeProps {
  logos: LogoItem[];
  direction?: Direction; // default 'rtl'
  durationSec?: number; // seconds to move one full sequence width
  startDelaySec?: number; // initial delay
  gapPx?: number; // space between logos
}

export default function LogoMarquee({
  logos,
  direction = "rtl",
  durationSec = 18,
  startDelaySec = 0,
  gapPx = 32,
}: LogoMarqueeProps) {
  const seq1Ref = React.useRef<HTMLDivElement | null>(null);
  const seq2Ref = React.useRef<HTMLDivElement | null>(null);
  const widthRef = React.useRef(0);
  const x1Ref = React.useRef(0);
  const x2Ref = React.useRef(0);
  const rafRef = React.useRef<number | null>(null);

  const renderLogos = (keyPrefix: string) =>
    logos.map((l, idx) => (
      <div
        key={`${keyPrefix}-${l.src}-${idx}`}
        className="flex items-center justify-center shrink-0"
      >
        <img
          src={l.src}
          alt={l.alt}
          loading="lazy"
          className={`h-24 w-auto object-contain grayscale opacity-80 hover:grayscale-0 hover:opacity-100 transition-all duration-300`}
        />
      </div>
    ));

  React.useEffect(() => {
    const a = seq1Ref.current;
    const b = seq2Ref.current;
    if (!a || !b) return;

    const prefersReduced =
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const measure = () => {
      // measure one sequence width (both sequences have identical content)
      const width = a.scrollWidth;
      widthRef.current = width;
      if (direction === "rtl") {
        x1Ref.current = 0;
        x2Ref.current = width;
      } else {
        x1Ref.current = -width;
        x2Ref.current = 0;
      }
      a.style.transform = `translate3d(${x1Ref.current}px, 0, 0)`;
      b.style.transform = `translate3d(${x2Ref.current}px, 0, 0)`;
    };

    measure();

    const ro = new ResizeObserver(() => {
      const prevWidth = widthRef.current;
      const prevX1 = x1Ref.current;
      // re-measure
      const width = a.scrollWidth;
      widthRef.current = width;
      if (direction === "rtl") {
        // keep b right after a
        const offsetWithin = ((prevX1 % width) + width) % width;
        x1Ref.current = -offsetWithin;
        x2Ref.current = x1Ref.current + width;
      } else {
        const offsetWithin = ((prevX1 % width) + width) % width;
        x1Ref.current = offsetWithin - width;
        x2Ref.current = x1Ref.current + width;
      }
      a.style.transform = `translate3d(${x1Ref.current}px, 0, 0)`;
      b.style.transform = `translate3d(${x2Ref.current}px, 0, 0)`;
    });
    ro.observe(a);

    let prev = performance.now();
    let started = false;

    const speed = () => {
      const w = Math.max(1, widthRef.current);
      return w / Math.max(0.001, durationSec); // px/s to traverse one sequence per duration
    };

    const tick = (now: number) => {
      if (!seq1Ref.current || !seq2Ref.current) return;

      if (!started) {
        if (now - prev < startDelaySec * 1000) {
          rafRef.current = requestAnimationFrame(tick);
          return;
        }
        started = true;
        prev = now;
      }

      const dt = (now - prev) / 1000;
      prev = now;

      const dir = direction === "rtl" ? -1 : 1;
      const dx = dir * speed() * dt;

      let x1 = x1Ref.current + dx;
      let x2 = x2Ref.current + dx;
      const w = widthRef.current;

      if (dir < 0) {
        // moving left: when a sequence fully leaves left, jump it to the right side (offscreen)
        if (x1 <= -w) x1 += w * 2;
        if (x2 <= -w) x2 += w * 2;
      } else {
        // moving right
        if (x1 >= w) x1 -= w * 2;
        if (x2 >= w) x2 -= w * 2;
      }

      x1Ref.current = x1;
      x2Ref.current = x2;
      a.style.transform = `translate3d(${x1}px, 0, 0)`;
      b.style.transform = `translate3d(${x2}px, 0, 0)`;

      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      ro.disconnect();
    };
  }, [direction, durationSec, startDelaySec, logos]);

  return (
    <div className="marquee-frame">
      <div className="relative w-full overflow-hidden py-12 bg-white rounded-[inherit]">
        <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-white to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-white to-transparent" />

        <div className="relative">
          <div
            ref={seq1Ref}
            className="marquee-track no-anim"
            style={{
              ["--marquee-gap" as any]: `${gapPx}px`,
              willChange: "transform",
            }}
          >
            {renderLogos("a")}
            <div
              className="shrink-0"
              style={{ width: `var(--marquee-gap, ${gapPx}px)` }}
            />
          </div>
          <div
            ref={seq2Ref}
            className="marquee-track no-anim absolute top-0 left-0"
            style={{
              ["--marquee-gap" as any]: `${gapPx}px`,
              willChange: "transform",
            }}
          >
            {renderLogos("b")}
            <div
              className="shrink-0"
              style={{ width: `var(--marquee-gap, ${gapPx}px)` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}