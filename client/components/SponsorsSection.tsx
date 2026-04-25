import * as React from "react";
import { useEmpresas, EmpresaAPI } from "@/hooks/use-empresas";
import { motion, Variants } from "framer-motion";
import { EmpresaModal } from "./EmpresaModal";
import { Star, ShieldCheck, Award } from "lucide-react";

const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5 } }
};

export default function SponsorsSection() {
  const { empresas, loading } = useEmpresas(null);
  const [selectedEmpresa, setSelectedEmpresa] = React.useState<EmpresaAPI | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  const sponsors = empresas.filter(e => e.es_sponsor);

  if (loading || sponsors.length === 0) return null;

  const handleLogoClick = (empresa: EmpresaAPI) => {
    setSelectedEmpresa(empresa);
    setIsModalOpen(true);
  };

  return (
    <section className="bg-white py-20 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-amber-50 rounded-full blur-3xl -mr-32 -mt-32 opacity-60" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl -ml-32 -mb-32 opacity-60" />

      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center gap-2 mb-4">
            <Star className="w-6 h-6 text-amber-500 fill-amber-500" />
            <span className="text-amber-600 font-bold uppercase tracking-widest text-sm">Alianzas Estratégicas</span>
            <Star className="w-6 h-6 text-amber-500 fill-amber-500" />
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-slate-900 mb-6 tracking-tight">
            Nuestros <span className="text-congress-blue">Sponsors</span>
          </h2>
          <p className="text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
            Empresas líderes que impulsan la innovación y el crecimiento del sector logístico en esta edición 2026.
          </p>
          <div className="w-24 h-1.5 bg-amber-400 mx-auto mt-8 rounded-full shadow-[0_0_15px_rgba(251,191,36,0.5)]" />
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          {sponsors.map((sponsor, idx) => (
            <motion.div
              key={sponsor.id}
              variants={scaleIn}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              onClick={() => handleLogoClick(sponsor)}
              className="group relative"
            >
              <div className="bg-white rounded-2xl p-8 h-48 flex items-center justify-center border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-500 cursor-pointer overflow-hidden">
                {/* Glow effect on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/5 group-hover:from-amber-500/5 transition-all duration-500" />
                
                {/* Badge corner */}
                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Award className="w-5 h-5 text-amber-500" />
                </div>

                <img
                  src={sponsor.logo}
                  alt={sponsor.nombre_empresa}
                  className="max-w-full max-h-full object-contain transition-transform duration-500 group-hover:scale-110"
                />
              </div>
              
              {/* Name tooltip/label below */}
              <div className="mt-4 text-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <span className="text-slate-900 font-bold text-sm">{sponsor.nombre_empresa}</span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Dynamic CTA for more sponsors */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mt-20 text-center"
        >
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-slate-50 rounded-full border border-slate-100 text-slate-500 text-sm font-medium">
            <ShieldCheck className="w-4 h-4 text-congress-blue" />
            ¿Quieres que tu marca esté aquí? 
            <a href="/contacto" className="text-congress-blue font-bold hover:underline">Contáctanos ahora</a>
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
