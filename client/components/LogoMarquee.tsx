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

  // Multiplicamos los elementos si el set es muy corto para asegurar que
  // llene pantallas anchas y no queden espacios vacíos durante la transición.
  let baseItems = [...items];
  while (baseItems.length < 8) {
    baseItems = [...baseItems, ...items];
  }

  return (
    <div className="relative flex overflow-hidden w-full select-none">
      <div className="flex flex-row w-max gap-12">
        <motion.div
          className="flex flex-row shrink-0 gap-12 items-center py-2"
          animate={{
            x: direction === "rtl" ? [0, "-100%"] : ["-100%", 0],
          }}
          transition={{
            duration: durationSec,
            ease: "linear",
            repeat: Infinity,
          }}
        >
          {baseItems.map((item, idx) => (
            <div key={`set1-${idx}`} className="flex-shrink-0">
              {renderItem(item, idx)}
            </div>
          ))}
        </motion.div>
        
        <motion.div
          className="flex flex-row shrink-0 gap-12 items-center py-2"
          animate={{
            x: direction === "rtl" ? [0, "-100%"] : ["-100%", 0],
          }}
          transition={{
            duration: durationSec,
            ease: "linear",
            repeat: Infinity,
          }}
        >
          {baseItems.map((item, idx) => (
            <div key={`set2-${idx}`} className="flex-shrink-0">
              {renderItem(item, idx)}
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}