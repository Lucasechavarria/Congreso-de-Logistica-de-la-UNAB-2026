import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Helmet } from "react-helmet-async";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { API_HOST } from "@/lib/api";
import FloatingParticles from "@/components/FloatingParticles";
import {
  Users,
  Search,
  Building2,
  Mic,
  FileText,
  ArrowRight,
  X,
  Sparkles,
  Award,
} from "lucide-react";

// Definimos el tipo de dato para un disertante, basado en el modelo de Django
type Disertante = {
  id: number;
  nombre: string;
  empresa_institucion?: string;
  bio?: string;
  foto_url: string;
  foto?: string;
  tema_presentacion: string;
  linkedin?: string;
};

export default function Ponentes() {
  const [disertantes, setDisertantes] = useState<Disertante[]>([]);
  const [selectedEditionId, setSelectedEditionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDisertante, setSelectedDisertante] = useState<Disertante | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const apiUrl = API_HOST;

  useEffect(() => {
    const fetchDisertantes = async () => {
      try {
        setLoading(true);
        setError(null);
        const url = selectedEditionId 
          ? `${apiUrl}/api/disertantes/?edicion_id=${selectedEditionId}`
          : `${apiUrl}/api/disertantes/`;
          
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error("Error al cargar los datos de los ponentes.");
        }
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          const dataOrdenada = [...data].sort((a, b) => a.nombre.localeCompare(b.nombre));
          setDisertantes(dataOrdenada);
        } else {
          setDisertantes([]);
        }
      } catch (err) {
        console.error("Error al cargar disertantes:", err);
        setError("Error al conectar con el servidor.");
      } finally {
        setLoading(false);
      }
    };
    fetchDisertantes();
  }, [apiUrl, selectedEditionId]);

  function getFotoUrl(disertante: Disertante): string {
    let url = "";

    const foto = disertante.foto || disertante.foto_url;

    if (foto && typeof foto === "string" && foto.length > 5) {
      if (foto.startsWith("http")) {
        url = foto;
      } else {
        const cleanPath = foto.replace(/^\/?(media\/)?(ponencias\/)?/, "");
        url = `${apiUrl}/media/ponencias/${cleanPath}`;
      }
    }

    if (url.startsWith("http://") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
      url = url.replace("http://", "https://");
    }

    return url;
  }

  // Filtrado en tiempo real
  const disertantesFiltrados = disertantes.filter((d) => {
    const term = searchTerm.toLowerCase();
    const coincideNombre = d.nombre.toLowerCase().includes(term);
    const coincideEmpresa = d.empresa_institucion ? d.empresa_institucion.toLowerCase().includes(term) : false;
    const coincideTema = d.tema_presentacion ? d.tema_presentacion.toLowerCase().includes(term) : false;
    return coincideNombre || coincideEmpresa || coincideTema;
  });

  const renderSkeletons = () =>
    Array.from({ length: 8 }).map((_, index) => (
      <div key={index} className="space-y-4 bg-white/70 p-6 rounded-3xl shadow-sm border border-slate-100">
        <Skeleton className="h-48 w-full rounded-2xl" />
        <Skeleton className="h-6 w-3/4 mx-auto" />
        <Skeleton className="h-4 w-1/2 mx-auto" />
        <Skeleton className="h-10 w-full rounded-xl" />
      </div>
    ));

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-blue-50/20 to-slate-100 relative overflow-hidden py-16 px-4">
      <Helmet>
        <title>Disertantes y Ponentes | Congreso de Logística 2026</title>
        <meta
          name="description"
          content="Conoce a los ponentes y disertantes destacados del Congreso de Logística y Transporte 2026 en la UNAB. Expertos líderes en cadena de suministro y transporte sustentable."
        />
        <meta
          name="keywords"
          content="disertantes congreso logistica, ponentes unab, expertos logistica argentina, congreso logistica 2026"
        />
        <link rel="canonical" href="https://www.congresologistica.unab.edu.ar/ponentes" />
        {disertantes && disertantes.length > 0 && (
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@graph": disertantes.map((d) => ({
                "@type": "Person",
                "@id": `https://www.congresologistica.unab.edu.ar/ponentes#disertante-${d.id}`,
                name: d.nombre,
                description: d.bio,
                jobTitle: d.tema_presentacion,
                image: getFotoUrl(d),
                sameAs: d.linkedin ? [d.linkedin] : [],
                worksFor: {
                  "@type": "Organization",
                  name: d.empresa_institucion || "Congreso de Logística y Transporte UNAB 2026",
                  url: "https://www.congresologistica.unab.edu.ar",
                },
              })),
            })}
          </script>
        )}
      </Helmet>

      <FloatingParticles count={35} color="rgba(37, 99, 235, 0.15)" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header de la Sección */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-congress-blue/10 border border-congress-blue/20 text-congress-blue font-bold text-xs uppercase tracking-widest mb-4 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-congress-cyan-dark" />
            Edición 2026
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold text-congress-blue mb-4 tracking-tight">
            Disertantes
          </h1>
          <div className="w-24 h-1.5 bg-gradient-to-r from-congress-blue via-congress-cyan to-purple-500 mx-auto mb-6 rounded-full"></div>
          <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto font-medium leading-relaxed">
            Líderes de la industria, referentes académicos y especialistas que transforman la logística y la cadena de suministro.
          </p>
        </motion.div>

        {/* Barra de Búsqueda interactiva en vivo */}
        {!loading && !error && disertantes.length > 0 && (
          <motion.div
            className="max-w-md mx-auto mb-12 relative"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="relative flex items-center">
              <Search className="absolute left-4 w-5 h-5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Buscar por disertante, empresa o tema..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-10 py-3.5 rounded-2xl bg-white/90 backdrop-blur-md border border-slate-200/80 shadow-[0_4px_20px_rgba(0,0,0,0.04)] focus:outline-none focus:ring-2 focus:ring-congress-cyan focus:border-transparent text-slate-800 placeholder-slate-400 text-sm transition-all"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm("")}
                  className="absolute right-3 p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            {searchTerm && (
              <p className="text-xs text-slate-500 text-center mt-2 font-medium">
                Mostrando {disertantesFiltrados.length} de {disertantes.length} disertantes
              </p>
            )}
          </motion.div>
        )}

        {/* Grid o Estados de Carga/Error */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {renderSkeletons()}
          </div>
        ) : error ? (
          <div className="text-center text-red-500 bg-red-50 p-6 rounded-2xl border border-red-100 max-w-md mx-auto shadow-sm">
            <p className="font-bold mb-2">Aviso</p>
            <p className="text-sm opacity-80">{error}</p>
          </div>
        ) : disertantes.length === 0 ? (
          <motion.div
            className="text-center max-w-3xl mx-auto rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(58,27,119,0.2)] border border-congress-blue/20 relative"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="bg-gradient-to-br from-congress-blue-dark/95 to-congress-blue/90 backdrop-blur-xl p-10 md:p-14 relative z-10 flex flex-col items-center text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#9c62de] to-[#b07eee] flex items-center justify-center mb-6 shadow-[0_0_25px_rgba(156,98,222,0.5)]">
                <Users className="w-10 h-10 text-white animate-pulse" />
              </div>
              <span className="inline-block px-4 py-1 rounded-full bg-white/10 border border-white/20 text-congress-cyan-light font-bold text-xs tracking-widest uppercase mb-4">
                Edición 2026
              </span>
              <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-4 tracking-tight leading-tight">
                Agenda de Disertantes en <span className="text-transparent bg-clip-text bg-gradient-to-r from-congress-cyan-light to-white">Preparación</span>
              </h2>
              <p className="text-slate-300 text-lg leading-relaxed max-w-2xl font-light">
                La grilla de disertantes destacados y el cronograma de ponencias para esta edición estarán disponibles muy pronto. Estamos diseñando una agenda académica de primer nivel.
              </p>
            </div>
          </motion.div>
        ) : disertantesFiltrados.length === 0 ? (
          <div className="text-center py-16 bg-white/60 rounded-3xl border border-slate-200/60 max-w-lg mx-auto shadow-sm">
            <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-700 mb-1">Sin resultados</h3>
            <p className="text-sm text-slate-500 mb-4">
              No se encontraron disertantes que coincidan con "{searchTerm}".
            </p>
            <button
              onClick={() => setSearchTerm("")}
              className="text-xs font-semibold px-4 py-2 bg-congress-blue text-white rounded-xl hover:bg-congress-blue-dark transition-all"
            >
              Ver todos los disertantes
            </button>
          </div>
        ) : (
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-7"
            initial="hidden"
            animate="visible"
            variants={{
              visible: { transition: { staggerChildren: 0.08 } },
            }}
          >
            {disertantesFiltrados.map((disertante) => {
              const fotoUrl = getFotoUrl(disertante);
              const tieneEmpresa = Boolean(
                disertante.empresa_institucion &&
                  disertante.empresa_institucion.trim() !== ""
              );

              return (
                <motion.div
                  key={disertante.id}
                  variants={{
                    hidden: { opacity: 0, y: 25 },
                    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
                  }}
                  whileHover={{ y: -8, scale: 1.01 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  onClick={() => setSelectedDisertante(disertante)}
                  className="group cursor-pointer h-full"
                >
                  <Card className="h-full flex flex-col overflow-hidden border border-slate-200/70 shadow-[0_4px_25px_rgba(0,0,0,0.05)] rounded-3xl bg-white/90 backdrop-blur-md group-hover:shadow-[0_20px_40px_rgba(37,99,235,0.15)] group-hover:border-congress-cyan/40 transition-all duration-300">
                    {/* Foto de la Tarjeta */}
                    <div className="relative h-64 overflow-hidden bg-slate-100">
                      {fotoUrl ? (
                        <img
                          src={fotoUrl}
                          alt={disertante.nombre}
                          className="w-full h-full object-cover object-center transition-transform duration-700 group-hover:scale-105"
                          loading="lazy"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-slate-100 via-blue-50/50 to-congress-cyan/10 flex items-center justify-center">
                          <Users className="w-20 h-20 text-congress-blue/25 group-hover:scale-110 transition-transform duration-500" />
                        </div>
                      )}
                      
                      {/* Overlay sutil al hover */}
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-slate-900/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center p-4">
                        <span className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-white/20 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/30 shadow-lg group-hover:translate-y-0 translate-y-2 transition-transform duration-300">
                          Ver detalles <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                        </span>
                      </div>
                    </div>

                    {/* Contenido de la Tarjeta */}
                    <CardContent className="p-5 flex-1 flex flex-col justify-between relative z-10">
                      <div>
                        {/* Nombre del Disertante */}
                        <h3 className="text-xl font-extrabold text-slate-900 group-hover:text-congress-blue transition-colors leading-tight mb-2">
                          {disertante.nombre}
                        </h3>

                        {/* Empresa / Institución (Optativa - Se omite limpio si no posee) */}
                        {tieneEmpresa && (
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-50/90 border border-blue-100/80 text-congress-blue font-semibold text-xs mb-3 max-w-full">
                            <Building2 className="w-3.5 h-3.5 text-congress-cyan-dark flex-shrink-0" />
                            <span className="truncate">
                              Representante de <strong className="text-congress-cyan-dark font-bold">{disertante.empresa_institucion}</strong>
                            </span>
                          </div>
                        )}

                        {/* Título de la Charla */}
                        <div className="bg-slate-50 group-hover:bg-blue-50/50 p-3 rounded-2xl border border-slate-100 group-hover:border-blue-100 transition-colors">
                          <p className="text-slate-700 font-bold text-sm leading-snug line-clamp-2">
                            {disertante.tema_presentacion && disertante.tema_presentacion.trim() !== ""
                              ? disertante.tema_presentacion
                              : "Tema de exposición en confirmación"}
                          </p>
                        </div>
                      </div>

                      {/* Icono de LinkedIn en la tarjeta (Se omite si no posee) */}
                      {disertante.linkedin && disertante.linkedin.trim() !== "" && (
                        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-center">
                          <a
                            href={disertante.linkedin}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-[#0A66C2]/10 text-[#0A66C2] hover:bg-[#0A66C2] hover:text-white transition-all duration-300 shadow-sm"
                            title="Perfil de LinkedIn"
                          >
                            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75-1.75zm13.5 11.268h-3v-5.604c0-1.337-.026-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.838-1.563 3.036 0 3.6 2.001 3.6 4.601v5.595z" />
                            </svg>
                          </a>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </div>

      {/* Modal de Detalle del Disertante */}
      <Dialog
        open={Boolean(selectedDisertante)}
        onOpenChange={(open) => {
          if (!open) setSelectedDisertante(null);
        }}
      >
        <DialogContent className="sm:max-w-xl p-0 overflow-hidden rounded-3xl border-0 bg-white shadow-2xl z-50">
          {selectedDisertante && (
            <div>
              {/* Header con Degradado Vanguardista */}
              <div className="bg-gradient-to-r from-congress-blue-dark via-congress-blue to-purple-900 h-28 relative p-6 flex justify-between items-start">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white font-bold text-xs uppercase tracking-widest">
                  <Award className="w-3.5 h-3.5 text-congress-cyan-light" /> Disertante Confirmado 2026
                </div>
              </div>

              {/* Avatar superpuesto */}
              <div className="px-6 relative -mt-12 flex items-end justify-between mb-4">
                <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl border-4 border-white shadow-xl bg-slate-100 overflow-hidden relative">
                  {getFotoUrl(selectedDisertante) ? (
                    <img
                      src={getFotoUrl(selectedDisertante)}
                      alt={selectedDisertante.nombre}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-slate-200 to-blue-100 flex items-center justify-center">
                      <Users className="w-12 h-12 text-congress-blue/40" />
                    </div>
                  )}
                </div>

                {/* LinkedIn Link si posee */}
                {selectedDisertante.linkedin && (
                  <a
                    href={selectedDisertante.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[#0A66C2] hover:bg-[#084e96] text-white rounded-xl font-bold text-xs shadow-md transition-all hover:scale-105"
                  >
                    <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                      <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 11.268h-3v-5.604c0-1.337-.026-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.838-1.563 3.036 0 3.6 2.001 3.6 4.601v5.595z" />
                    </svg>
                    Perfil LinkedIn
                  </a>
                )}
              </div>

              {/* Información Principal del Modal */}
              <div className="px-6 pb-6 space-y-5">
                <div>
                  <DialogTitle className="text-2xl sm:text-3xl font-extrabold text-slate-900 leading-tight">
                    {selectedDisertante.nombre}
                  </DialogTitle>
                  
                  {/* Empresa (Solo si existe) */}
                  {selectedDisertante.empresa_institucion &&
                    selectedDisertante.empresa_institucion.trim() !== "" && (
                      <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-50 border border-blue-100 text-congress-blue font-semibold text-xs">
                        <Building2 className="w-3.5 h-3.5 text-congress-cyan-dark" />
                        <span>
                          Representante de{" "}
                          <strong className="text-congress-cyan-dark font-bold">
                            {selectedDisertante.empresa_institucion}
                          </strong>
                        </span>
                      </div>
                    )}
                </div>

                {/* Título de la Charla */}
                <div className="bg-gradient-to-r from-blue-50/80 via-slate-50 to-indigo-50/40 p-4 sm:p-5 rounded-2xl border border-blue-100 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-extrabold text-congress-blue uppercase tracking-wider mb-1.5">
                    <Mic className="w-4 h-4 text-congress-cyan-dark" />
                    <span>Título de la Charla</span>
                  </div>
                  <h4 className="text-lg font-extrabold text-slate-800 leading-snug">
                    {selectedDisertante.tema_presentacion &&
                    selectedDisertante.tema_presentacion.trim() !== ""
                      ? selectedDisertante.tema_presentacion
                      : "Título de exposición en confirmación por el comité académico"}
                  </h4>
                </div>

                {/* Resumen - Solo se renderiza si está disponible */}
                {selectedDisertante.bio && selectedDisertante.bio.trim() !== "" && (
                  <div>
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                      <FileText className="w-3.5 h-3.5 text-slate-400" />
                      <span>Resumen</span>
                    </div>

                    <div className="text-slate-700 text-sm leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-100 font-normal whitespace-pre-line">
                      {selectedDisertante.bio}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

