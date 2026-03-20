import React, { useState, useEffect, useRef } from "react";
import { LogoItem, chunk, ALL_LOGOS } from "./data/logos";
import { motion, AnimatePresence } from "framer-motion";
import { useEmpresas } from "@/hooks/use-empresas";
interface LargeLogoCarouselProps {
  edicionId?: number | null;
}

const LargeLogoCarousel: React.FC<LargeLogoCarouselProps> = ({ edicionId }) => {
  const { logosForCarousel, loading, error } = useEmpresas(edicionId);
  const [currentPage, setCurrentPage] = useState(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  // Detectar mobile
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 640);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Elegir chunking según mobile/desktop
  const logosPerPage = isMobile ? 6 : 12; // 2x3 en mobile, 4x3 en desktop
  // Fall back to 2025 ALL_LOGOS if the API returned an error or an empty list
  const isFallback = logosForCarousel.length === 0 || !!error;
  const logosToDisplay = isFallback ? ALL_LOGOS : logosForCarousel;
  const chunkedLogos = chunk(logosToDisplay, logosPerPage);

  useEffect(() => {
    timeoutRef.current = setTimeout(() => {
      setCurrentPage((prev) => (prev + 1) % chunkedLogos.length);
    }, 5000);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [currentPage, chunkedLogos.length]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
    exit: { opacity: 0, transition: { duration: 0.5 } },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.9 },
    visible: { y: 0, opacity: 1, scale: 1 },
    exit: { y: -20, opacity: 0, scale: 0.9 },
  };

  if (loading) {
    return (
      <section className="py-16 bg-lavender-subtle">
        <div className="w-full px-4 flex justify-center items-center h-[400px]">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-violet-600"></div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-2 bg-gray-100 overflow-hidden relative">
      <div className="w-full px-4">
        {isFallback && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center mb-8"
          >
            <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-violet-100 to-fuchsia-100 border border-violet-200 text-violet-800 text-sm md:text-base font-semibold shadow-sm backdrop-blur-sm">
              <svg className="w-5 h-5 text-fuchsia-600 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              Conoce a quienes nos acompañaron en la exitosa Edición 2025
            </span>
          </motion.div>
        )}
        <div className="relative w-full h-[400px]">
          <AnimatePresence mode="wait">
            {chunkedLogos.map(
              (page, pageIndex) =>
                pageIndex === currentPage && (
                  <motion.div
                    key={pageIndex}
                    className={
                      isMobile
                        ? "absolute top-0 left-0 w-full h-full grid grid-cols-2 grid-rows-3 gap-6 justify-items-center items-center"
                        : "absolute top-0 left-0 w-full h-full grid grid-cols-4 grid-rows-3 gap-8 justify-items-center items-center"
                    }
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                  >
                    {page.map((logo, index) => (
                      <motion.div
                        key={index}
                        className="flex justify-center items-center p-4 bg-white rounded-lg shadow-md"
                        variants={itemVariants}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                      >
                        <img
                          src={logo.src}
                          alt={logo.alt}
                          className="max-h-24 w-auto object-contain"
                        />
                      </motion.div>
                    ))}
                  </motion.div>
                ),
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default LargeLogoCarousel;