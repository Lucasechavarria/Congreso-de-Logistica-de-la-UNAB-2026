import * as React from "react";
import LogoMarquee from "@/components/LogoMarquee";
import { useEmpresas } from "@/hooks/use-empresas";
import { chunk } from "@/components/data/logos";
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

  if (error) {
    return (
      <section className="bg-lavender-subtle py-10">
        <div className="w-full px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-center">
            Empresas e Instituciones Participantes
          </h2>
          <div className="flex flex-col items-center justify-center py-12 px-4 text-slate-500">
            <svg className="w-12 h-12 mb-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <p className="text-lg font-medium">Próximamente más empresas</p>
            <p className="text-sm mt-1">Estamos actualizando nuestra lista de sponsors</p>
          </div>
        </div>
      </section>
    );
  }

  if (logosForCarousel.length === 0) {
    return (
      <section className="bg-lavender-subtle py-10">
        <div className="w-full px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-center">
            Empresas e Instituciones Participantes
          </h2>
          <div className="text-center text-gray-600 py-4">
            No hay empresas disponibles en este momento.
            <br />
            Las empresas se mostrarán una vez que sean cargadas desde el panel de administración.
          </div>
        </div>
      </section>
    );
  }

  // Dividir logos en tres grupos para los carruseles
  const chunkSize = Math.ceil(logosForCarousel.length / 3);
  const logoGroups = chunk(logosForCarousel, chunkSize);
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
        <div className="w-16 h-1 bg-[#8b5cf6] mx-auto mb-10 rounded-full"></div>
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