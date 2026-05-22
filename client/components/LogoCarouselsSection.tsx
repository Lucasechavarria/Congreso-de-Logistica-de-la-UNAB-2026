import * as React from "react";
import LogoMarquee from "@/components/LogoMarquee";
import { chunk, ALL_LOGOS } from "@/data/logos";
import { motion, Variants } from "framer-motion";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

export default function LogoCarouselsSection() {
  const logosToDisplay = ALL_LOGOS;




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
          Empresas e Instituciones Edición 2025
        </h2>

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
        <div className="w-16 h-1 bg-[#8b5cf6] mx-auto mb-8 rounded-full"></div>
        <div className="space-y-6">
          {firstCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="rtl"
              items={firstCarouselLogos}
              durationSec={32}
              renderItem={(logo) => (
                <img
                  src={logo.src}
                  alt={logo.alt}
                  className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                />
              )}
            />
          )}
          {secondCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="ltr"
              items={secondCarouselLogos}
              durationSec={28}
              renderItem={(logo) => (
                <img
                  src={logo.src}
                  alt={logo.alt}
                  className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                />
              )}
            />
          )}
          {thirdCarouselLogos.length > 0 && (
            <LogoMarquee
              direction="rtl"
              items={thirdCarouselLogos}
              durationSec={24}
              renderItem={(logo) => (
                <img
                  src={logo.src}
                  alt={logo.alt}
                  className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                />
              )}
            />
          )}
        </div>
      </motion.div>
    </section>
  );
}