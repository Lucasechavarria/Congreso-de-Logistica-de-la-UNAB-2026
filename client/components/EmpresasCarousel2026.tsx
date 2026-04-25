import * as React from "react";
import LogoMarquee from "@/components/LogoMarquee";
import { useEmpresas, EmpresaAPI } from "@/hooks/use-empresas";
import { ALL_LOGOS, chunk } from "@/components/data/logos";
import SkeletonLoader from "./SkeletonLoader";
import { motion, Variants, AnimatePresence } from "framer-motion";
import { EmpresaModal } from "./EmpresaModal";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5 } }
};

export default function EmpresasCarousel2026() {
  const { empresas, loading } = useEmpresas(null);
  const [selectedEmpresa, setSelectedEmpresa] = React.useState<EmpresaAPI | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  // Volvemos a los logos estáticos para este carrusel como estaba antes
  const logosForCarousel = ALL_LOGOS;

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

  const handleLogoClick = (src: string) => {
    // Intentar encontrar los datos dinámicos si el logo coincide
    const empresa = empresas.find(e => {
      const cleanLogo = e.logo.split('/').pop();
      const cleanSrc = src.split('/').pop();
      return cleanLogo === cleanSrc;
    });
    
    if (empresa) {
      setSelectedEmpresa(empresa);
      setIsModalOpen(true);
    }
  };

  const isFewCompanies = logosForCarousel.length <= 6;

  // Lógica para cuando hay muchas empresas (dividimos en 2 o 3 líneas)
  let firstCarouselLogos = [];
  let secondCarouselLogos = [];
  let thirdCarouselLogos = [];

  if (!isFewCompanies) {
    const chunkSize = Math.ceil(logosForCarousel.length / 3);
    const logoGroups = chunk(logosForCarousel, chunkSize);
    firstCarouselLogos = logoGroups[0] || [];
    secondCarouselLogos = logoGroups[1] || [];
    thirdCarouselLogos = logoGroups[2] || [];
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
                  onClick={() => handleLogoClick(logo.src)}
                  className="bg-white rounded-xl shadow-md border border-slate-100 p-6 flex items-center justify-center hover:shadow-xl hover:-translate-y-1 transition-all duration-300 min-w-[160px] h-[120px] cursor-pointer"
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
                  items={firstCarouselLogos}
                  durationSec={35}
                  renderItem={(logo) => (
                    <img
                      src={logo.src}
                      alt={logo.alt}
                      onClick={() => handleLogoClick(logo.src)}
                      className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300 cursor-pointer hover:scale-110 transform"
                    />
                  )}
                />
              )}
              {secondCarouselLogos.length > 0 && (
                <LogoMarquee
                  direction="ltr"
                  items={secondCarouselLogos}
                  durationSec={27}
                  renderItem={(logo) => (
                    <img
                      src={logo.src}
                      alt={logo.alt}
                      onClick={() => handleLogoClick(logo.src)}
                      className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300 cursor-pointer hover:scale-110 transform"
                    />
                  )}
                />
              )}
              {thirdCarouselLogos.length > 0 && (
                <LogoMarquee
                  direction="rtl"
                  items={thirdCarouselLogos}
                  durationSec={22}
                  renderItem={(logo) => (
                    <img
                      src={logo.src}
                      alt={logo.alt}
                      onClick={() => handleLogoClick(logo.src)}
                      className="h-20 w-auto object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300 cursor-pointer hover:scale-110 transform"
                    />
                  )}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <EmpresaModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        empresa={selectedEmpresa}
      />
    </section>
  );
}
