import { motion } from "framer-motion";
import * as React from "react";
import { chunk, type LogoItem } from "./data/logos";
import { useEmpresas } from "@/hooks/use-empresas";

type Direction = "ltr" | "rtl";

interface TruckCarouselProps {
  direction?: Direction; // default 'rtl'
  durationSec?: number; // full cross duration
  startDelaySec?: number; // offset start between carousels
}

const Wheel: React.FC<{ className?: string }> = ({ className }) => (
  <motion.div
    className={`w-10 h-10 bg-black rounded-full border-2 border-black/70 shadow-inner relative ${className ?? ""}`}
    animate={{ rotate: 360 }}
    transition={{ duration: 2, ease: "linear", repeat: Infinity }}
  >
    <div className="absolute inset-2 rounded-full border-2 border-gray-400" />
    <div className="absolute left-1/2 top-0 -translate-x-1/2 w-0.5 h-full bg-gray-500" />
  </motion.div>
);

const Truck: React.FC<{ logos: LogoItem[]; color: "blue" | "cyan" }> = ({
  logos,
  color,
}) => {
  const bg =
    color === "blue"
      ? "from-congress-blue to-congress-blue-dark"
      : "from-congress-cyan to-congress-cyan-light";
  return (
    <div className="relative w-[980px] max-w-full">
      {/* Road */}
      <div className="absolute -bottom-6 left-0 right-0 h-3 bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 rounded-full" />
      {/* Tractor + Trailer */}
      <div className="flex items-stretch">
        {/* Tractor (cab) */}
        <div
          className={`relative w-[170px] h-[135px] rounded-l-md shadow-xl overflow-hidden bg-gradient-to-br ${bg}`}
          aria-label="Cabina del camión"
        >
          <div className="absolute top-3 right-4 w-16 h-8 bg-white/80 rounded-sm" />
          <div className="absolute bottom-6 right-6 w-12 h-3 bg-black/20 rounded-sm" />
          <div className="absolute -right-3 bottom-4 w-6 h-6 rotate-45 bg-gray-300" />
        </div>
        {/* Semi (trailer/logos) */}
        <div className="relative flex-1">
          <div className="rounded-r-md border-2 border-congress-blue bg-white shadow-lg">
            <div className="h-2 bg-gradient-to-r from-congress-cyan to-congress-cyan-light rounded-t-md" />
            <div className="absolute -bottom-2 left-4 right-4 h-1 bg-gray-400 rounded" />
            <div className="grid grid-cols-4 gap-4 p-4">
              {logos.map((l, idx) => (
                <div key={idx} className="flex items-center justify-center">
                  <img
                    src={l.src}
                    alt={l.alt}
                    className={`${l.heightClass ?? "h-16"} w-auto object-contain`}
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
            <div className="h-2 bg-gray-100 border-t" />
          </div>
        </div>
      </div>
      {/* Wheels */}
      <div className="absolute -bottom-5 left-10 flex gap-6">
        <Wheel />
        <Wheel />
      </div>
      <div className="absolute -bottom-5 left-[280px] flex gap-6">
        <Wheel />
        <Wheel />
        <Wheel />
        <Wheel />
      </div>
    </div>
  );
};

export const TruckCarousel: React.FC<TruckCarouselProps> = ({
  direction = "rtl",
  durationSec = 18,
  startDelaySec = 0,
}) => {
  const { logosForCarousel, loading, error } = useEmpresas();
  
  if (loading || error || logosForCarousel.length === 0) {
    return null; // No renderizar nada si no hay logos disponibles
  }

  const groups = chunk(logosForCarousel.slice(0, 12), 4); // 3 groups of 4
  const initialX = direction === "rtl" ? "110%" : "-110%";
  const targetX = direction === "rtl" ? "-130%" : "130%";

  return (
    <div className="relative w-full overflow-hidden py-10">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          initial={{ x: initialX }}
          animate={{ x: targetX }}
          transition={{
            duration: durationSec,
            ease: "linear",
            repeat: Infinity,
            repeatType: "loop",
            delay: startDelaySec + i * (durationSec / 3),
          }}
          className="absolute top-0"
          style={{
            left: direction === "rtl" ? undefined : 0,
            right: direction === "rtl" ? 0 : undefined,
          }}
        >
          <Truck
            logos={(groups[i] as LogoItem[]) ?? []}
            color={i % 2 === 0 ? "blue" : "cyan"}
          />
        </motion.div>
      ))}
    </div>
  );
};

export default TruckCarousel;