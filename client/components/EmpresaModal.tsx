import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ExternalLink, Video, Building2, MapPin } from "lucide-react";

interface EmpresaModalProps {
  isOpen: boolean;
  onClose: () => void;
  empresa: {
    nombre_empresa: string;
    logo: string;
    descripcion?: string;
    sitio_web?: string;
    youtube_video_url?: string;
    es_sponsor?: boolean;
    numero_stand?: string | number;
  } | null;
}

const getYouTubeEmbedUrl = (url: string) => {
  if (!url) return null;
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? `https://www.youtube.com/embed/${match[2]}` : null;
};

export const EmpresaModal: React.FC<EmpresaModalProps> = ({ isOpen, onClose, empresa }) => {
  if (!empresa) return null;

  const embedUrl = empresa.youtube_video_url ? getYouTubeEmbedUrl(empresa.youtube_video_url) : null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[9999] flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row"
            >
              {/* Lateral Izquierdo: Video o Logo Grande */}
              <div className="w-full md:w-1/2 bg-slate-100 flex flex-col items-center justify-center relative min-h-[300px]">
                {embedUrl ? (
                  <div className="w-full h-full aspect-video md:aspect-square">
                    <iframe
                      src={embedUrl}
                      className="w-full h-full"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      title={empresa.nombre_empresa}
                    />
                  </div>
                ) : (
                  <div className="p-12 flex flex-col items-center gap-6">
                    <img
                      src={empresa.logo}
                      alt={empresa.nombre_empresa}
                      className="w-full max-w-[250px] h-auto object-contain drop-shadow-xl"
                    />
                    {!embedUrl && (
                      <div className="flex items-center gap-2 text-slate-400 text-sm italic">
                        <Video className="w-4 h-4" />
                        Sin video de presentación
                      </div>
                    )}
                  </div>
                )}
                
                <button
                  onClick={onClose}
                  className="absolute top-4 left-4 p-2 bg-white/80 backdrop-blur hover:bg-white rounded-full shadow-lg transition-all md:hidden"
                >
                  <X className="w-6 h-6 text-slate-600" />
                </button>
              </div>

              {/* Contenido Derecho */}
              <div className="w-full md:w-1/2 p-8 md:p-10 flex flex-col overflow-y-auto">
                <div className="flex justify-between items-start mb-6">
                  <div className="flex flex-wrap gap-2">
                    {empresa.es_sponsor && (
                      <span className="px-3 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded-full uppercase tracking-wider border border-amber-200">
                        Sponsor Oficial
                      </span>
                    )}
                    {empresa.numero_stand && (
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full uppercase tracking-wider border border-blue-200 flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> Stand #{empresa.numero_stand}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-slate-100 rounded-full transition-colors hidden md:block"
                  >
                    <X className="w-6 h-6 text-slate-400" />
                  </button>
                </div>

                <div className="mb-8">
                  <h2 className="text-3xl font-extrabold text-slate-900 leading-tight mb-4">
                    {empresa.nombre_empresa}
                  </h2>
                  <div className="h-1 w-20 bg-congress-blue rounded-full mb-6" />
                  
                  <p className="text-slate-600 leading-relaxed text-lg whitespace-pre-line">
                    {empresa.descripcion || "Esta empresa participa en el Congreso de Logística y Transporte 2026. Visita su stand para más información sobre sus servicios y novedades."}
                  </p>
                </div>

                <div className="mt-auto space-y-4">
                  {empresa.sitio_web && (
                    <a
                      href={empresa.sitio_web}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-congress-blue font-semibold hover:underline group"
                    >
                      <ExternalLink className="w-5 h-5" />
                      Visitar Sitio Web
                    </a>
                  )}
                  
                  <div className="pt-6 border-t border-slate-100 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-slate-500" />
                    </div>
                    <div className="text-sm">
                      <p className="text-slate-400 font-medium uppercase tracking-tighter">Empresa Acreditada</p>
                      <p className="text-slate-900 font-bold">Congreso UNAB 2026</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
