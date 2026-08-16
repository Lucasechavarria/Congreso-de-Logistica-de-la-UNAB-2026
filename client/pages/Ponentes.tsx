import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Helmet } from "react-helmet-async";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { API_HOST } from "@/lib/api";
import FloatingParticles from "@/components/FloatingParticles";
import { EditionSelector } from "@/components/EditionSelector";

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

    // Mismo método robusto implementado en Programa.tsx
    const foto = disertante.foto || disertante.foto_url;

    if (foto && typeof foto === "string" && foto.length > 5) {
      if (foto.startsWith("http")) {
        url = foto;
      } else {
        // Asegurarnos de que no haya dobles media/media o ponencias/ponencias
        const cleanPath = foto.replace(/^\/?(media\/)?(ponencias\/)?/, "");
        url = `${apiUrl}/media/ponencias/${cleanPath}`;
      }
    }

    // Forzar HTTPS si es posible y no es localhost, pero por compatibilidad local lo dejamos limpio
    if (url.startsWith("http://") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
      url = url.replace("http://", "https://");
    }

    return url;
  }

  const renderSkeletons = () =>
    Array.from({ length: 4 }).map((_, index) => (
      <div key={index} className="space-y-4">
        <Skeleton className="h-[250px] w-full rounded-2xl" />
        <Skeleton className="h-6 w-3/4 mx-auto" />
        <Skeleton className="h-4 w-1/2 mx-auto" />
      </div>
    ));

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden py-16 px-4">
      <Helmet>
        <title>Disertantes y Ponentes | Congreso de Logística 2026</title>
        <meta name="description" content="Conoce a los ponentes y disertantes destacados del Congreso de Logística y Transporte 2026 en la UNAB. Expertos líderes en cadena de suministro y transporte sustentable." />
        <meta name="keywords" content="disertantes congreso logistica, ponentes unab, expertos logistica argentina, congreso logistica 2026" />
        <link rel="canonical" href="https://www.congresologistica.unab.edu.ar/ponentes" />
        {disertantes && disertantes.length > 0 && (
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@graph": disertantes.map((d) => ({
                "@type": "Person",
                "@id": `https://www.congresologistica.unab.edu.ar/ponentes#disertante-${d.id}`,
                "name": d.nombre,
                "description": d.bio,
                "jobTitle": d.tema_presentacion,
                "image": getFotoUrl(d),
                "sameAs": d.linkedin ? [d.linkedin] : [],
                "worksFor": {
                  "@type": "Organization",
                  "name": "Congreso de Logística y Transporte UNAB 2026",
                  "url": "https://www.congresologistica.unab.edu.ar"
                }
              }))
            })}
          </script>
        )}
      </Helmet>
      <FloatingParticles count={30} color="rgba(37, 99, 235, 0.2)" />

      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl md:text-6xl font-extrabold text-congress-blue mb-6 tracking-tight">
            Disertantes
          </h1>
          <div className="w-24 h-1.5 bg-congress-cyan mx-auto mb-8 rounded-full"></div>
          <p className="text-xl text-gray-700 max-w-2xl mx-auto font-medium leading-relaxed">
            Expertos líderes que compartirán las últimas tendencias y desafíos en logística y transporte.
          </p>

        </motion.div>

        {/* TODO: Descomentar para la edición del próximo año
        {!loading && (
          <motion.div
            className="mb-16 max-w-5xl mx-auto rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(58,27,119,0.3)] border border-congress-blue/20 relative"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            <div className="absolute inset-0 z-0">
              <div className="absolute top-0 right-0 w-80 h-80 bg-congress-cyan/30 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-pulse"></div>
              <div className="absolute bottom-0 left-0 w-80 h-80 bg-congress-blue/40 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-pulse" style={{ animationDelay: '2s' }}></div>
              <div className="absolute inset-0 z-0 opacity-20 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:30px_30px] mask-image-[radial-gradient(ellipse_at_center,black_40%,transparent_100%)]"></div>
            </div>

            <div className="bg-gradient-to-br from-congress-blue-dark/95 to-congress-blue/90 backdrop-blur-xl p-10 md:p-14 relative z-10 flex flex-col md:flex-row items-center gap-10">
              <div className="flex-1 text-center md:text-left">
                <div className="inline-block px-4 py-1 rounded-full bg-white/10 border border-white/20 text-congress-cyan-light font-bold text-sm tracking-widest uppercase mb-4 shadow-[0_0_15px_rgba(176,126,238,0.2)]">
                  Convocatoria Abierta
                </div>
                <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-4 tracking-tight leading-tight">
                  Sé Parte del Futuro de la <span className="text-transparent bg-clip-text bg-gradient-to-r from-congress-cyan-light to-white">Logística</span>
                </h2>
                <p className="text-lg text-slate-300 mb-8 leading-relaxed max-w-xl mx-auto md:mx-0">
                  Postula tu ponencia ante líderes del sector y la comunidad universitaria, y comparte los avances y conocimientos que moverán la industria hacia adelante.
                </p>
                <a href="/registro-disertante" className="inline-block">
                  <button className="bg-gradient-to-r from-congress-cyan-dark to-congress-blue hover:from-congress-cyan hover:to-congress-cyan-dark text-white font-bold px-8 py-5 text-lg rounded-xl transition-all duration-300 shadow-[0_0_25px_rgba(58,27,119,0.7)] hover:shadow-[0_0_35px_rgba(156,98,222,0.8)] border border-white/20 hover:scale-105 flex items-center justify-center gap-3">
                    Postular Ponencia
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                  </button>
                </a>
              </div>
              <div className="hidden lg:flex flex-1 justify-center relative">
                <div className="w-56 h-56 relative flex justify-center items-center">
                  <div className="absolute inset-0 rounded-full border-2 border-congress-cyan/30 animate-[spin_12s_linear_infinite]"></div>
                  <div className="absolute inset-4 rounded-full border border-congress-cyan-light/40 animate-[spin_8s_linear_infinite_reverse]"></div>
                  <div className="w-32 h-32 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-[0_0_30px_rgba(156,98,222,0.3)] flex items-center justify-center transform rotate-12 transition-transform duration-500 hover:rotate-0">
                    <Users className="w-16 h-16 text-congress-cyan-light" />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        */}

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
            className="text-center max-w-3xl mx-auto rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(58,27,119,0.3)] border border-congress-blue/20 relative"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Elementos decorativos internos de la tarjeta */}
            <div className="absolute inset-0 z-0 pointer-events-none">
              {/* Glowing orbs */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-congress-cyan/20 rounded-full mix-blend-screen filter blur-[80px] opacity-70 animate-pulse"></div>
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-congress-blue/30 rounded-full mix-blend-screen filter blur-[80px] opacity-70 animate-pulse" style={{ animationDelay: '2s' }}></div>
              {/* Grid overlay */}
              <div className="absolute inset-0 z-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:20px_20px]"></div>
            </div>

            <div className="bg-gradient-to-br from-congress-blue-dark/95 to-congress-blue/90 backdrop-blur-xl p-10 md:p-14 relative z-10 flex flex-col items-center text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#9c62de] to-[#b07eee] flex items-center justify-center mb-6 shadow-[0_0_25px_rgba(156,98,222,0.5)]">
                <Users className="w-10 h-10 text-white animate-pulse" />
              </div>
              <span className="inline-block px-4 py-1 rounded-full bg-white/10 border border-white/20 text-congress-cyan-light font-bold text-xs tracking-widest uppercase mb-4 shadow-[0_0_15px_rgba(176,126,238,0.2)]">
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
        ) : (
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
            initial="hidden"
            animate="visible"
            variants={{
              visible: { transition: { staggerChildren: 0.1 } }
            }}
          >
            {disertantes.map((disertante, idx) => {
              const fotoUrl = getFotoUrl(disertante);
              return (
                <motion.div
                  key={disertante.id}
                  variants={{
                    hidden: { opacity: 0, y: 30 },
                    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
                  }}
                  whileHover={{ y: -10 }}
                  className="group"
                >
                  <Card className="overflow-hidden border-0 shadow-xl rounded-3xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-500">
                    <div className="relative h-72 overflow-hidden">
                      {fotoUrl ? (
                        <img
                          src={fotoUrl}
                          alt={disertante.nombre}
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-congress-blue/10 to-congress-cyan/20 flex items-center justify-center">
                          <Users className="w-20 h-20 text-congress-blue/20" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-gradient-to-t from-congress-blue/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                    <CardContent className="p-6 text-center relative z-10">
                      <h3 className="text-xl font-bold text-congress-blue mb-1 group-hover:text-congress-cyan transition-colors">
                        {disertante.nombre}
                      </h3>
                      {disertante.empresa_institucion && (
                        <p className="text-congress-blue/70 font-semibold text-xs mb-2 tracking-wide">
                          Representante de <span className="text-congress-cyan-dark font-bold">{disertante.empresa_institucion}</span>
                        </p>
                      )}
                      <p className="text-congress-cyan-dark font-bold text-sm mb-3 uppercase tracking-wider">
                        {disertante.tema_presentacion}
                      </p>
                      {disertante.bio && (
                        <p className="text-gray-600 text-sm line-clamp-3 leading-relaxed mb-4">
                          {disertante.bio}
                        </p>
                      )}
                      {disertante.linkedin && (
                        <a
                          href={disertante.linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-congress-blue/10 text-congress-blue hover:bg-congress-blue hover:text-white transition-all duration-300"
                        >
                          <svg width={20} height={20} fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 11.268h-3v-5.604c0-1.337-.026-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.838-1.563 3.036 0 3.6 2.001 3.6 4.601v5.595z" /></svg>
                        </a>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </div>
    </div>
  );
}

import { Users } from "lucide-react";
