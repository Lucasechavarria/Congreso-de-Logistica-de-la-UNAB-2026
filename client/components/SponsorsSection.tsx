import * as React from "react";
import { useEmpresas, EmpresaAPI, FALLBACK_SPONSORS } from "@/hooks/use-empresas";
import { motion, Variants } from "framer-motion";
import { EmpresaModal } from "./EmpresaModal";
import { Star, ShieldCheck, Award, ChevronRight } from "lucide-react";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.85 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: "easeOut" } }
};

export default function SponsorsSection() {
  const { sponsors, loading } = useEmpresas(null);
  const [selectedEmpresa, setSelectedEmpresa] = React.useState<EmpresaAPI | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  // Solo se renderiza en el frontend si hay al menos una empresa tildada como sponsor desde el admin
  if (loading || sponsors.length === 0) return null;

  const count = sponsors.length;

  const handleLogoClick = (empresa: EmpresaAPI) => {
    setSelectedEmpresa(empresa);
    setIsModalOpen(true);
  };

  return (
    <section className="bg-gradient-to-b from-white via-slate-50/60 to-white py-20 relative overflow-hidden">
      {/* Elementos de fondo decorativos */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-amber-100/30 rounded-full blur-3xl -mr-40 -mt-40 opacity-70 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-100/30 rounded-full blur-3xl -ml-40 -mb-40 opacity-70 pointer-events-none" />

      <div className="container mx-auto px-4 relative z-10">
        {/* Encabezado */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center gap-2 mb-4">
            <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
            <span className="text-amber-600 font-extrabold uppercase tracking-widest text-xs sm:text-sm">Auspiciantes</span>
            <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-slate-900 mb-6 tracking-tight">
            Nuestros <span className="text-congress-blue">Auspiciantes</span>
          </h2>
          <p className="text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
            Empresas líderes que impulsan la innovación y el desarrollo logístico en esta edición 2026.
          </p>
          <div className="w-24 h-1.5 bg-gradient-to-r from-amber-400 to-amber-500 mx-auto mt-8 rounded-full shadow-[0_0_15px_rgba(251,191,36,0.6)]" />
        </motion.div>

        {/* Layout Dinámico de Auspiciantes */}
        {count === 1 && (
          /* 1 SPONSOR: Centrado, tamaño Hero VIP grande */
          <div className="max-w-3xl mx-auto flex justify-center">
            <motion.div
              key={sponsors[0].id}
              variants={scaleIn}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              onClick={() => handleLogoClick(sponsors[0])}
              className="group relative w-full cursor-pointer"
            >
              <div className="relative bg-gradient-to-b from-white via-amber-50/20 to-white rounded-3xl p-10 sm:p-14 md:p-16 h-72 sm:h-80 md:h-96 flex flex-col items-center justify-center border-2 border-amber-300/80 shadow-[0_15px_50px_rgba(251,191,36,0.18)] hover:shadow-[0_20px_60px_rgba(251,191,36,0.3)] hover:-translate-y-2 transition-all duration-500 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-amber-400/0 via-amber-400/10 to-amber-400/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 blur-xl" />
                
                <div className="absolute top-4 sm:top-6 inline-flex items-center gap-2 px-4 py-1.5 bg-amber-500/10 text-amber-800 rounded-full border border-amber-300/60 text-xs sm:text-sm font-extrabold uppercase tracking-widest shadow-sm">
                  <Award className="w-4 h-4 text-amber-500" />
                  Auspiciante
                </div>

                <div className="w-full flex-1 flex items-center justify-center mt-6 mb-2">
                  <img
                    src={sponsors[0].logo}
                    alt={sponsors[0].nombre_empresa}
                    className="max-w-[85%] max-h-36 sm:max-h-44 md:max-h-52 object-contain transition-transform duration-500 group-hover:scale-105 filter drop-shadow-md"
                  />
                </div>

                <div className="mt-2 flex items-center gap-2 text-slate-800 font-bold text-lg sm:text-xl group-hover:text-amber-600 transition-colors">
                  <span>{sponsors[0].nombre_empresa}</span>
                  <ChevronRight className="w-5 h-5 text-amber-500 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {count === 2 && (
          /* 2 SPONSORS: 1 sola línea en sm+, perfectamente centrados */
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 md:gap-12 max-w-4xl mx-auto justify-center items-center">
            {sponsors.map((sponsor, idx) => (
              <motion.div
                key={sponsor.id}
                variants={scaleIn}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15 }}
                onClick={() => handleLogoClick(sponsor)}
                className="group relative cursor-pointer"
              >
                <div className="bg-white rounded-2xl p-8 md:p-10 h-60 sm:h-64 flex flex-col items-center justify-center border border-slate-200/90 shadow-md hover:shadow-2xl hover:border-amber-300 hover:-translate-y-2 transition-all duration-500 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/5 group-hover:from-amber-500/5 transition-all duration-500" />
                  
                  <div className="absolute top-3.5 right-3.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Award className="w-5 h-5 text-amber-500" />
                  </div>

                  <div className="w-full flex-1 flex items-center justify-center">
                    <img
                      src={sponsor.logo}
                      alt={sponsor.nombre_empresa}
                      className="max-w-[85%] max-h-32 sm:max-h-36 object-contain transition-transform duration-500 group-hover:scale-105"
                    />
                  </div>

                  <div className="mt-4 text-center">
                    <span className="text-slate-900 font-extrabold text-base md:text-lg group-hover:text-amber-600 transition-colors">
                      {sponsor.nombre_empresa}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {count === 3 && (
          /* 3 SPONSORS: 1 sola línea de 3 en md+, centrados */
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 max-w-5xl md:max-w-6xl mx-auto justify-center items-center">
            {sponsors.map((sponsor, idx) => (
              <motion.div
                key={sponsor.id}
                variants={scaleIn}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                onClick={() => handleLogoClick(sponsor)}
                className="group relative cursor-pointer"
              >
                <div className="bg-white rounded-2xl p-8 h-52 sm:h-56 flex flex-col items-center justify-center border border-slate-200/80 shadow-sm hover:shadow-xl hover:border-amber-300 hover:-translate-y-2 transition-all duration-500 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/5 group-hover:from-amber-500/5 transition-all duration-500" />
                  
                  <div className="absolute top-3.5 right-3.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Award className="w-5 h-5 text-amber-500" />
                  </div>

                  <div className="w-full flex-1 flex items-center justify-center">
                    <img
                      src={sponsor.logo}
                      alt={sponsor.nombre_empresa}
                      className="max-w-[85%] max-h-28 sm:max-h-32 object-contain transition-transform duration-500 group-hover:scale-110"
                    />
                  </div>

                  <div className="mt-3 text-center">
                    <span className="text-slate-900 font-bold text-sm sm:text-base group-hover:text-amber-600 transition-colors">
                      {sponsor.nombre_empresa}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {count === 4 && (
          /* 4 SPONSORS: 4 en 1 línea en lg+ o 2x2 grid centrados */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto justify-center items-center">
            {sponsors.map((sponsor, idx) => (
              <motion.div
                key={sponsor.id}
                variants={scaleIn}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                onClick={() => handleLogoClick(sponsor)}
                className="group relative cursor-pointer"
              >
                <div className="bg-white rounded-2xl p-6 h-48 sm:h-52 flex flex-col items-center justify-center border border-slate-200/80 shadow-sm hover:shadow-xl hover:border-amber-300 hover:-translate-y-2 transition-all duration-500 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/5 group-hover:from-amber-500/5 transition-all duration-500" />
                  
                  <div className="absolute top-3.5 right-3.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Award className="w-5 h-5 text-amber-500" />
                  </div>

                  <div className="w-full flex-1 flex items-center justify-center">
                    <img
                      src={sponsor.logo}
                      alt={sponsor.nombre_empresa}
                      className="max-w-[80%] max-h-24 sm:max-h-28 object-contain transition-transform duration-500 group-hover:scale-110"
                    />
                  </div>

                  <div className="mt-2 text-center">
                    <span className="text-slate-900 font-bold text-sm group-hover:text-amber-600 transition-colors">
                      {sponsor.nombre_empresa}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {count >= 5 && (
          /* 5 O MÁS SPONSORS: Flex Wrap totalmente centrado */
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-8 max-w-6xl mx-auto">
            {sponsors.map((sponsor, idx) => (
              <motion.div
                key={sponsor.id}
                variants={scaleIn}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ delay: idx * 0.08 }}
                onClick={() => handleLogoClick(sponsor)}
                className="group relative cursor-pointer w-full sm:w-[calc(50%-1.25rem)] md:w-[calc(33.333%-1.25rem)] lg:w-[calc(25%-1.25rem)] max-w-xs"
              >
                <div className="bg-white rounded-2xl p-6 h-48 flex flex-col items-center justify-center border border-slate-200/80 shadow-sm hover:shadow-xl hover:border-amber-300 hover:-translate-y-2 transition-all duration-500 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/5 group-hover:from-amber-500/5 transition-all duration-500" />
                  
                  <div className="absolute top-3.5 right-3.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Award className="w-5 h-5 text-amber-500" />
                  </div>

                  <div className="w-full flex-1 flex items-center justify-center">
                    <img
                      src={sponsor.logo}
                      alt={sponsor.nombre_empresa}
                      className="max-w-[80%] max-h-24 object-contain transition-transform duration-500 group-hover:scale-110"
                    />
                  </div>

                  <div className="mt-2 text-center">
                    <span className="text-slate-900 font-bold text-sm group-hover:text-amber-600 transition-colors">
                      {sponsor.nombre_empresa}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* CTA dinámico para sumar más empresas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-20 text-center"
        >
          <div className="inline-flex flex-col sm:flex-row items-center gap-3 px-6 py-3.5 bg-slate-50/90 rounded-2xl sm:rounded-full border border-slate-200/80 text-slate-600 text-sm font-medium shadow-sm hover:shadow-md transition-shadow">
            <ShieldCheck className="w-5 h-5 text-congress-blue" />
            <span>¿Quieres que tu marca lidere como auspiciante del congreso?</span>
            <a href="/contacto" className="text-congress-blue font-bold hover:underline inline-flex items-center gap-1">
              Contáctanos ahora <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </motion.div>
      </div>

      <EmpresaModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        empresa={selectedEmpresa}
      />
    </section>
  );
}



