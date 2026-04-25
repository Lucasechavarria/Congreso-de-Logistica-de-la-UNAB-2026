import * as React from "react";
import { motion } from "framer-motion";

interface LogoMarqueeProps {
  items: any[];
  renderItem: (item: any, index: number) => React.ReactNode;
  direction?: "ltr" | "rtl";
  durationSec?: number;
}

export default function LogoMarquee({
  items,
  renderItem,
  direction = "rtl",
  durationSec = 30,
}: LogoMarqueeProps) {
  if (!items || items.length === 0) return null;

  // Duplicamos los items para asegurar el efecto infinito suave
  // Usamos un factor de 4 para asegurar que cubra pantallas anchas
  const displayItems = [...items, ...items, ...items, ...items];

  return (
    <div className="relative flex overflow-hidden w-full">
      <motion.div
        className="flex whitespace-nowrap gap-12 items-center py-4"
        animate={{
          x: direction === "rtl" ? ["0%", "-25%"] : ["-25%", "0%"],
        }}
        transition={{
          duration: durationSec,
          ease: "linear",
          repeat: Infinity,
        }}
      >
        {displayItems.map((item, idx) => (
          <div key={idx} className="flex-shrink-0">
            {renderItem(item, idx)}
          </div>
        ))}
      </motion.div>
    </div>
  );
}