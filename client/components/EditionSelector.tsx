import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useEdiciones, Edicion } from "@/hooks/use-ediciones";
import { ChevronDown, Calendar } from "lucide-react";

interface EditionSelectorProps {
  selectedEditionId: number | null;
  onEditionChange: (editionId: number) => void;
}

export const EditionSelector: React.FC<EditionSelectorProps> = ({
  selectedEditionId,
  onEditionChange,
}) => {
  const { ediciones, loading } = useEdiciones();
  const [isOpen, setIsOpen] = React.useState(false);

  const selectedEdition = ediciones.find((e) => e.id === selectedEditionId) || 
                          ediciones.find((e) => e.activa) || 
                          ediciones[0];

  if (loading || ediciones.length <= 1) return null;

  return (
    <div className="relative inline-block text-left z-50 mb-8">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl text-white font-bold shadow-[0_8px_32px_rgba(0,0,0,0.1)] hover:bg-white/20 transition-all duration-300"
      >
        <Calendar className="w-5 h-5 text-congress-cyan-light" />
        <span className="tracking-tight">
          Edición {selectedEdition?.anio || "Cargando..."}
        </span>
        <ChevronDown 
          className={`w-4 h-4 transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`} 
        />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute left-0 mt-3 w-48 origin-top-left bg-congress-blue-dark/90 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="py-2">
              {ediciones.map((edicion) => (
                <button
                  key={edicion.id}
                  onClick={() => {
                    onEditionChange(edicion.id);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-5 py-3 text-sm font-medium transition-colors flex items-center justify-between ${
                    selectedEditionId === edicion.id
                      ? "bg-congress-cyan/20 text-congress-cyan-light"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  Año {edicion.anio}
                  {edicion.activa && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-congress-cyan/20 border border-congress-cyan/30 text-congress-cyan-light uppercase font-bold tracking-widest">
                      Activa
                    </span>
                  )}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
