import * as React from "react";
import LogoMarquee from "@/components/LogoMarquee";
import { useEmpresas } from "@/hooks/use-empresas";
import { chunk } from "@/components/data/logos";
import SkeletonLoader from "./SkeletonLoader";
import { motion, Variants, AnimatePresence } from "framer-motion";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5 } }
};

export default function EmpresasCarousel2026() {
  const { logosForCarousel, loading } = useEmpresas(null); // Fetch current (no edition id forces current)

  if (loading) {
    return (
      <section className="bg-lavender-subtle py-16 relative overflow-hidden">
        <div className="w-full px-4 relative z-10">
          <h2 className="text-3xl md:text-5xl font-extrabold text-[#3b1066] mb-6 text-center tracking-tight">
            Empresas e Instituciones Confirmadas
          </h2>
          <div className="flex justify-center flex-wrap gap-4 py-8 max-w-5xl mx-auto overflow-hidden">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i}>
                <SkeletonLoader type="logo" className="h-20 w-36 mx-2" />
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Si aún no hay ninguna empresa confirmada
  if (!loading && logosForCarousel.length === 0) {
    return (
      <section className="bg-lavender-subtle py-16 relative overflow-hidden border-y border-slate-100 shadow-[inset_0_4px_20px_rgba(0,0,0,0.02)]">
        <div className="w-full px-4 relative z-10 text-center">
          <h2 className="text-3xl md:text-5xl font-extrabold text-[#3b1066] mb-4 tracking-tight">
            Empresas e Instituciones Participantes
          </h2>
          <div className="w-16 h-1 bg-[#8b5cf6] mx-auto mb-8 rounded-full"></div>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            className="max-w-2xl mx-auto bg-white/50 backdrop-blur-sm border border-violet-100 rounded-2xl p-8 shadow-sm"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-violet-100 rounded-full flex items-center justify-center text-violet-600">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-violet-900 mb-2">Próximamente</h3>
            <p className="text-slate-600">
              Estamos sumando a las empresas líderes del sector que formarán parte de esta nueva edición. ¡Mantenete atento a las novedades!
            </p>
          </motion.div>
        </div>
      </section>
    );
  }

  const isFewCompanies = logosForCarousel.length <= 6;

  // Lógica para cuando hay muchas empresas (dividimos en 2 o 3 líneas)
  let firstCarouselLogos = [];
  let secondCarouselLogos = [];
  let thirdCarouselLogos = [];

  if (!isFewCompanies) {
    if (logosForCarousel.length <= 12) {
      // Dos líneas
      const chunkSize = Math.ceil(logosForCarousel.length / 2);
      const logoGroups = chunk(logosForCarousel, chunkSize);
      firstCarouselLogos = logoGroups[0] || [];
      secondCarouselLogos = logoGroups[1] || [];
    } else {
      // Tres líneas
      const chunkSize = Math.ceil(logosForCarousel.length / 3);
      const logoGroups = chunk(logosForCarousel, chunkSize);
      firstCarouselLogos = logoGroups[0] || [];
      secondCarouselLogos = logoGroups[1] || [];
      thirdCarouselLogos = logoGroups[2] || [];
    }
  }

  return (
    <section className="bg-lavender-subtle py-16 border-y border-slate-100 relative shadow-[inset_0_4px_20px_rgba(0,0,0,0.02)] overflow-hidden">
      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 z-0 opacity-[0.15] pointer-events-none">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="logosPattern2026" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
              <path d="M0 30h60 M30 0v60" stroke="#4c1d95" strokeWidth="1.5" strokeDasharray="4 4" fill="none" />
              <circle cx="30" cy="30" r="3" fill="#4c1d95" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#logosPattern2026)" />
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
          Empresas e Instituciones Confirmadas
        </h2>
        <div className="w-16 h-1 bg-[#8b5cf6] mx-auto mb-10 rounded-full"></div>

        <AnimatePresence mode="wait">
          {isFewCompanies ? (
            // Modo Grid/Flex para pocas empresas
            <motion.div
              key="few-companies"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-wrap justify-center items-center gap-8 md:gap-12 max-w-5xl mx-auto py-8"
            >
              {logosForCarousel.map((logo, idx) => (
                <motion.div
                  key={idx}
                  variants={scaleIn}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-white rounded-xl shadow-md border border-slate-100 p-6 flex items-center justify-center hover:shadow-xl hover:-translate-y-1 transition-all duration-300 min-w-[160px] h-[120px]"
                >
                  <img
                    src={logo.src}
                    alt={logo.alt}
                    className="max-w-[120px] max-h-[80px] object-contain filter grayscale hover:grayscale-0 transition-all duration-300"
                  />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            // Modo Marquee para muchas empresas
            <motion.div
              key="many-companies"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {firstCarouselLogos.length > 0 && (
                <LogoMarquee
                  direction="rtl"
                  logos={firstCarouselLogos}
                  startDelaySec={0}
                  durationSec={35.5}
                />
              )}
              {secondCarouselLogos.length > 0 && (
                <LogoMarquee
                  direction="ltr"
                  logos={secondCarouselLogos}
                  startDelaySec={1.5}
                  durationSec={27.2}
                />
              )}
              {thirdCarouselLogos.length > 0 && (
                <LogoMarquee
                  direction="rtl"
                  logos={thirdCarouselLogos}
                  startDelaySec={2.8}
                  durationSec={21.8}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}
