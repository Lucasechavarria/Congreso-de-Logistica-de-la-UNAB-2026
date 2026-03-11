import * as React from "react";
import LogoMarquee from "@/components/LogoMarquee";
import { useEmpresas } from "@/hooks/use-empresas";
import { chunk, ALL_LOGOS } from "@/components/data/logos";
import SkeletonLoader from "./SkeletonLoader";
import { motion, Variants } from "framer-motion";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

export default function LogoCarouselsSection() {
  const { logosForCarousel, loading, error } = useEmpresas();

  if (loading) {
    return (
      <section className="bg-lavender-subtle py-10">
        <div className="w-full px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-center">
            Empresas e Instituciones Participantes
          </h2>
          <div className="flex justify-center flex-wrap gap-4 py-8 max-w-5xl mx-auto overflow-hidden">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonLoader key={i} type="logo" className="h-20 w-36 mx-2" />
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Ignore error if we are falling back to ALL_LOGOS anyway
  const isFallback = logosForCarousel.length === 0 || !!error;
  const logosToDisplay = isFallback ? ALL_LOGOS : logosForCarousel;


  // Dividir logos en tres grupos para los carruseles
  const chunkSize = Math.ceil(logosToDisplay.length / 3);
  const logoGroups = chunk(logosToDisplay, chunkSize);
  const firstCarouselLogos = logoGroups[0] || [];
  const secondCarouselLogos = logoGroups[1] || [];
  const thirdCarouselLogos = logoGroups[2] || [];

  return (
    <section className="bg-lavender-subtle py-16 border-y border-slate-100 relative shadow-[inset_0_4px_20px_rgba(0,0,0,0.02)] overflow-hidden">
      {/* Subtle Background Pattern (Cyan particles on white) */}
      <div className="absolute inset-0 z-0 opacity-[0.15] pointer-events-none">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="logosPattern" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
              <path d="M0 30h60 M30 0v60" stroke="#4c1d95" strokeWidth="1.5" strokeDasharray="4 4" fill="none" />
              <circle cx="30" cy="30" r="3" fill="#4c1d95" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#logosPattern)" />
        </svg>
      </div>

      <motion.div
        className="w-full px-4 relative z-10"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeInUp}
      >
        <h2 className="text-3xl md:text-5xl font-extrabold text-[#3b1066] mb-4 text-center tracking-tight">
          Empresas e Instituciones Participantes
        </h2>
        {isFallback && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="flex justify-center mb-6"
          >
            <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-violet-100 to-fuchsia-100 border border-violet-200 text-violet-800 text-sm md:text-base font-semibold shadow-sm backdrop-blur-sm">
              <svg className="w-5 h-5 text-fuchsia-600 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              Conoce a quienes nos acompañaron en la exitosa Edición 2025
            </span>
          </motion.div>
        )}
        <div className={`w-16 h-1 bg-[#8b5cf6] mx-auto ${isFallback ? 'mb-8' : 'mb-10'} rounded-full`}></div>
        <div className="space-y-6">
          {firstCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="rtl"
              logos={firstCarouselLogos}
              startDelaySec={0}
              durationSec={32.76}
            />
          )}
          {secondCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="ltr"
              logos={secondCarouselLogos}
              startDelaySec={1.2}
              durationSec={28.275}
            />
          )}
          {thirdCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="rtl"
              logos={thirdCarouselLogos}
              startDelaySec={2.4}
              durationSec={23.4}
            />
          )}
        </div>
      </motion.div>
    </section>
  );
}