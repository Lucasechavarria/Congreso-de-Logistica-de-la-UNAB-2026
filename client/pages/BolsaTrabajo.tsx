import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Briefcase, Filter, X, Building2, Ghost, Megaphone } from "lucide-react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import OfertaCard from "@/components/OfertaCard";
import { getOfertasLaborales, getEmpresas } from "@/lib/api";

const MODALIDADES = [
  { id: "TODAS", label: "Todas" },
  { id: "PRESENCIAL", label: "Presencial" },
  { id: "REMOTO", label: "Remoto" },
  { id: "HIBRIDO", label: "Híbrido" },
];

export default function BolsaTrabajo() {
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [modalidad, setModalidad] = useState("TODAS");
  const [empresaId, setEmpresaId] = useState("TODAS");

  // Debounce para búsqueda
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch de ofertas
  const { data: ofertas = [], isLoading: isLoadingOfertas } = useQuery({
    queryKey: ["ofertas", debouncedSearch, modalidad, empresaId],
    queryFn: () => {
      const params: Record<string, string> = {};
      if (debouncedSearch) params.q = debouncedSearch;
      if (modalidad !== "TODAS") params.modalidad = modalidad;
      if (empresaId !== "TODAS") params.empresa = empresaId;
      return getOfertasLaborales(params);
    },
  });

  // Fetch de empresas para el filtro
  const { data: empresas = [] } = useQuery({
    queryKey: ["empresas-filtro"],
    queryFn: getEmpresas,
  });

  const clearFilters = () => {
    setSearchTerm("");
    setModalidad("TODAS");
    setEmpresaId("TODAS");
  };

  const hasActiveFilters = searchTerm !== "" || modalidad !== "TODAS" || empresaId !== "TODAS";

  return (
    <div className="min-h-screen bg-[#0f041e] text-white py-12 px-4 sm:px-6 lg:px-8">
      {/* Background Decorative Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#9b6dd7]/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-congress-blue/10 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header Section */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-congress-cyan mb-4"
          >
            <Briefcase size={16} />
            <span className="text-sm font-semibold tracking-wider uppercase">Oportunidades</span>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-black mb-4 bg-gradient-to-r from-white via-white to-congress-cyan bg-clip-text text-transparent"
          >
            Bolsa de Trabajo
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-slate-400 text-lg max-w-2xl mx-auto mb-8"
          >
            Conectamos el talento del Congreso UNAB 2026 con las empresas líderes del sector logístico y de transporte.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.25 }}
            className="flex justify-center"
          >
            <Link to="/empresas/postular-vacante">
              <Button className="bg-[#9b6dd7] hover:bg-[#805ad5] text-white font-bold py-6 px-10 rounded-2xl shadow-[0_0_20px_rgba(155,109,215,0.3)] transition-all hover:scale-[1.05] active:scale-[0.95] flex items-center gap-3 border border-white/20">
                <Megaphone size={20} className="animate-bounce" />
                ¿Sos una empresa? Publicá tu vacante
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Filters Box */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 mb-12 shadow-2xl"
        >
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Search Input */}
            <div className="md:col-span-5 relative">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2 block ml-1">
                ¿Qué estás buscando?
              </label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 h-5 w-5" />
                <Input
                  placeholder="Título, palabras clave o descripción..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-12 py-6 bg-white/[0.03] border-white/10 rounded-2xl focus:ring-[#9b6dd7]/40 focus:border-[#9b6dd7]/40 text-white placeholder:text-slate-600 transition-all"
                />
              </div>
            </div>

            {/* Company Dropdown */}
            <div className="md:col-span-3">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2 block ml-1">
                Empresa
              </label>
              <Select value={empresaId} onValueChange={setEmpresaId}>
                <SelectTrigger className="w-full py-6 bg-white/[0.03] border-white/10 rounded-2xl focus:ring-[#9b6dd7]/40 text-left">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-slate-500" />
                    <SelectValue placeholder="Todas las empresas" />
                  </div>
                </SelectTrigger>
                <SelectContent className="bg-[#1a0a2e] border-white/10 text-white">
                  <SelectItem value="TODAS">Todas las empresas</SelectItem>
                  {empresas.map((emp: any) => (
                    <SelectItem key={emp.id} value={emp.id.toString()}>
                      {emp.nombre_empresa}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Modality Pills */}
            <div className="md:col-span-4">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2 block ml-1">
                Modalidad
              </label>
              <div className="flex flex-wrap gap-2">
                {MODALIDADES.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setModalidad(m.id)}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${
                      modalidad === m.id
                        ? "bg-[#9b6dd7] border-[#b794f4] text-white shadow-[0_0_15px_rgba(155,109,215,0.4)]"
                        : "bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <AnimatePresence>
            {hasActiveFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center justify-end mt-4 pt-4 border-t border-white/5"
              >
                <Button
                  variant="ghost"
                  onClick={clearFilters}
                  className="text-slate-400 hover:text-white transition-colors gap-2"
                >
                  <X size={16} />
                  Limpiar filtros
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Results Info */}
        <div className="flex items-center justify-between mb-8 px-2">
          <p className="text-slate-400">
            Mostrando <span className="text-white font-bold">{ofertas.length}</span> ofertas encontradas
          </p>
        </div>

        {/* Grid Section */}
        {isLoadingOfertas ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-[280px] rounded-3xl bg-white/5 animate-pulse border border-white/10" />
            ))}
          </div>
        ) : ofertas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <AnimatePresence mode="popLayout">
              {ofertas.map((oferta: any, idx: number) => (
                <motion.div
                  key={oferta.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.4, delay: idx * 0.05 }}
                  layout
                >
                  <OfertaCard oferta={oferta} />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        ) : (
          /* Empty State */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 bg-white/[0.02] border border-dashed border-white/10 rounded-[40px]"
          >
            <div className="p-6 bg-[#9b6dd7]/10 rounded-full mb-6">
              <Ghost className="h-12 w-12 text-[#9b6dd7]" />
            </div>
            <h3 className="text-2xl font-bold mb-2">No encontramos ofertas</h3>
            <p className="text-slate-400 text-center max-w-sm mb-8">
              Prueba ajustando los filtros o buscando con otros términos para encontrar lo que necesitas.
            </p>
            <Button onClick={clearFilters} className="bg-white/10 hover:bg-white/20 text-white border-white/10">
              Ver todas las vacantes
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
