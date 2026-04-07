import { motion } from "framer-motion";
import { ArrowLeft, Megaphone } from "lucide-react";
import { Link } from "react-router-dom";
import FormularioOferta from "@/components/FormularioOferta";

export default function PostularVacante() {
  return (
    <div className="min-h-screen bg-[#0f041e] text-white py-12 px-4 sm:px-6 lg:px-8 relative">
      {/* Background patterns */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#9b6dd7]/10 blur-[150px] rounded-full" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-congress-blue/10 blur-[130px] rounded-full" />
      </div>

      <div className="max-w-5xl mx-auto relative z-10">
        {/* Navigation / Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <Link 
            to="/bolsa-de-trabajo"
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
          >
            <ArrowLeft className="h-5 w-5 transition-transform group-hover:-translate-x-1" />
            <span>Volver a la Bolsa</span>
          </Link>

          <div className="flex items-center gap-4 bg-white/5 border border-white/10 px-6 py-2 rounded-2xl">
            <Megaphone className="text-congress-cyan h-5 w-5" />
            <span className="text-sm font-semibold tracking-wide">Área para Empresas e Instituciones</span>
          </div>
        </div>

        {/* Content Header */}
        <div className="text-center mb-16">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-black mb-6 bg-gradient-to-r from-white via-white to-congress-cyan bg-clip-text text-transparent"
          >
            Publique su Vacante
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 text-lg max-w-2xl mx-auto"
          >
            Forme parte de la red de empleo del Congreso UNAB 2026. Conectamos su empresa con estudiantes, profesionales y especialistas del transporte y la logística.
          </motion.p>
        </div>

        {/* Form Section */}
        <motion.div
           initial={{ opacity: 0, y: 40 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ delay: 0.2 }}
        >
          <FormularioOferta />
        </motion.div>
      </div>
    </div>
  );
}
