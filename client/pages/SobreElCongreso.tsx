import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import FloatingParticles from "@/components/FloatingParticles";
import { FiCamera, FiVideo, FiFileText, FiX, FiChevronLeft, FiChevronRight, FiExternalLink } from "react-icons/fi";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import LogoCarouselsSection from "@/components/LogoCarouselsSection";

const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const GALLERY_IMAGES = [
  { url: "/images/edicion-2025/2025-gallery-1.webp", alt: "Campus UNAB — Vehículos expositores" },
  { url: "/images/edicion-2025/2025-gallery-2.webp", alt: "Stand DronesVIP — Tecnología aérea" },
  { url: "/images/edicion-2025/2025-gallery-3.webp", alt: "Exposición OCA — Flota de transporte" },
  { url: "/images/edicion-2025/2025-gallery-4.webp", alt: "Paneles de expertos en logística" },
  { url: "/images/edicion-2025/2025-gallery-5.webp", alt: "Asistentes y comunidad universitaria" },
  { url: "/images/edicion-2025/2025-gallery-6.webp", alt: "Exposición de stands empresariales" },
  { url: "/images/edicion-2025/2025-gallery-7.webp", alt: "Debates y rondas de negocios" },
  { url: "/images/edicion-2025/2025-gallery-8.webp", alt: "Innovación tecnológica en el campus" },
  { url: "/images/edicion-2025/2025-gallery-9.jpeg", alt: "Cierre de la jornada 2025" },
  { url: "/images/edicion-2025/2025-gallery-10.webp", alt: "Intercambio de experiencias" },
  { url: "/images/edicion-2025/2025-gallery-11.webp", alt: "Participación institucional" }
];

const NEWS_ARTICLES = [
  {
    title: "Webpicking: Resumen del Congreso 2025",
    date: "22 de Diciembre, 2025",
    resume: "En el programa 'Hablemos de Logística', Hernán Disanto (ARLOG/UNaB) analiza los excelentes resultados de la primera edición y cómo se gestó este hito para la región.",
    link: "https://webpicking.com/hablemos-de-logistica-901-resumen-del-congreso-de-logistica-y-transporte-2025-organizado-por-la-universidad-nacional-guillermo-brown-unab/"
  },
  {
    title: "Diario La Tercera: Más de 1500 participantes",
    date: "18 de Noviembre, 2025",
    resume: "Una cobertura exhaustiva del congreso que reunió a más de 40 disertantes y 50 empresas, destacando la masiva concurrencia y las demostraciones en vivo en el campus.",
    link: "https://diariolatercera.com.ar/contenido/6370/mas-de-1500-personas-participaron-del-primer-congreso-de-logistica-y-transporte-"
  },
  {
    title: "Diario de Malvinas: Consolidación Regional",
    date: "15 de Noviembre, 2025",
    resume: "Reseña del éxito institucional del congreso, destacando la sinergia entre la universidad, el sector público y las empresas líderes del transporte y la logística.",
    link: "https://eldiariodemalvinas.com.ar/municipios-bonaerenses/primer-congreso-de-logistica-y-transporte-de-la-unab/"
  },
  {
    title: "ARLOG: Capacitación y Compromiso",
    date: "20 de Noviembre, 2025",
    resume: "La Asociación Argentina de Logística Empresarial destaca su participación activa en el evento, impulsando la formación y profesionalización del sector.",
    link: "https://arlog.org/arlog-participo-del-1-congreso-de-logistica-y-transporte-de-la-universidad-nacional-guillermo-brown/"
  }
];

// Lightbox component
function Lightbox({ images, initialIndex, onClose }: { images: typeof GALLERY_IMAGES; initialIndex: number; onClose: () => void }) {
  const [current, setCurrent] = useState(initialIndex);

  const prev = () => setCurrent((c) => (c - 1 + images.length) % images.length);
  const next = () => setCurrent((c) => (c + 1) % images.length);

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center" onClick={onClose}>
      {/* Botón cerrar */}
      <button
        className="absolute top-5 right-5 w-11 h-11 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white transition-all z-10 border border-white/20"
        onClick={onClose}
      >
        <FiX size={20} />
      </button>

      {/* Contador */}
      <div className="absolute top-5 left-1/2 -translate-x-1/2 text-white/60 text-sm font-medium tracking-widest">
        {current + 1} / {images.length}
      </div>

      {/* Imagen */}
      <div className="relative max-w-5xl max-h-[85vh] w-full mx-12" onClick={(e) => e.stopPropagation()}>
        <AnimatePresence mode="wait">
          <motion.img
            key={current}
            src={images[current].url}
            alt={images[current].alt}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-full max-h-[80vh] object-contain rounded-xl shadow-2xl"
          />
        </AnimatePresence>

        {/* Caption */}
        <p className="text-center text-white/70 text-sm mt-4 font-medium">{images[current].alt}</p>
      </div>

      {/* Navegación */}
      <button
        className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 hover:bg-white/25 rounded-full flex items-center justify-center text-white transition-all border border-white/20"
        onClick={(e) => { e.stopPropagation(); prev(); }}
      >
        <FiChevronLeft size={22} />
      </button>
      <button
        className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 hover:bg-white/25 rounded-full flex items-center justify-center text-white transition-all border border-white/20"
        onClick={(e) => { e.stopPropagation(); next(); }}
      >
        <FiChevronRight size={22} />
      </button>

      {/* Thumbnails */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 overflow-x-auto max-w-xl px-4">
        {images.map((img, i) => (
          <button
            key={i}
            onClick={(e) => { e.stopPropagation(); setCurrent(i); }}
            className={`flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2 transition-all ${i === current ? 'border-congress-cyan scale-110' : 'border-white/20 opacity-50 hover:opacity-80'}`}
          >
            <img src={img.url} alt={img.alt} className="w-full h-full object-cover" />
          </button>
        ))}
      </div>
    </div>
  );
}

export default function SobreElCongreso() {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  return (
    <>
      <LogoCarouselsSection />
      <section className="py-20 bg-slate-50 relative overflow-hidden min-h-screen">
        <FloatingParticles count={20} color="rgba(37, 99, 235, 0.1)" />

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <Lightbox images={GALLERY_IMAGES} initialIndex={lightboxIndex} onClose={() => setLightboxIndex(null)} />
      )}

      {/* Encabezado */}
      <div className="container mx-auto px-4 relative z-10 mb-20">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <div className="inline-block px-4 py-1 rounded-full bg-congress-cyan/20 border border-congress-cyan text-congress-blue font-bold text-sm tracking-widest uppercase mb-4 shadow-sm">
            Edición Anterior
          </div>
          <h2 className="text-4xl md:text-6xl font-extrabold text-congress-blue mb-6 tracking-tight leading-tight">
            Primera Edición <span className="text-congress-cyan">2025</span>
          </h2>
          <div className="w-24 h-1.5 bg-congress-cyan mx-auto mb-8 rounded-full"></div>
          <p className="text-xl text-gray-700 leading-relaxed font-medium">
            Reviví los mejores momentos del Primer Congreso de Logística y Transporte. Un evento sin precedentes que reunió a los principales referentes del sector, generando un espacio único de encuentro, aprendizaje y networking.
          </p>
        </motion.div>
      </div>

      {/* Galería Multimedia */}
      <div className="container mx-auto px-4 relative z-10 mb-24">
        <motion.div
          className="mb-10 flex items-center gap-3"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <div className="text-3xl text-congress-cyan">
            <FiCamera />
          </div>
          <h3 className="text-3xl font-bold text-congress-blue">Galería Multimedia</h3>
          <span className="ml-2 text-sm text-slate-400 font-medium">— clic para ampliar</span>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          {GALLERY_IMAGES.map((img, index) => (
            <motion.div
              key={index}
              variants={fadeInUp}
              className={`overflow-hidden rounded-2xl shadow-lg border border-slate-200 group cursor-pointer ${index === 0 ? 'lg:col-span-2 lg:row-span-2' : ''}`}
              onClick={() => setLightboxIndex(index)}
            >
              <div className="relative w-full h-64 lg:h-full min-h-[250px] bg-slate-200">
                <img
                  src={img.url}
                  alt={img.alt}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                {/* Overlay con zoom icon */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-6">
                  <div className="self-end">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/30">
                      <svg width="18" height="18" fill="none" stroke="white" strokeWidth="2" viewBox="0 0 24 24">
                        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35M11 8v6M8 11h6"/>
                      </svg>
                    </div>
                  </div>
                  <p className="text-white font-semibold text-lg">{img.alt}</p>
                </div>
                {/* Borde cian en hover */}
                <div className="absolute inset-0 border-2 border-transparent group-hover:border-congress-cyan/50 rounded-2xl transition-colors duration-300 pointer-events-none" />
              </div>
            </motion.div>
          ))}

          {/* Video Modal */}
          <Dialog>
            <DialogTrigger asChild>
              <motion.div
                variants={fadeInUp}
                className="overflow-hidden rounded-2xl shadow-lg border border-slate-200 group cursor-pointer bg-slate-900 flex items-center justify-center min-h-[250px] relative"
              >
                <img
                  src="/images/edicion-2025/2025-gallery-4.webp"
                  alt="Resumen del Congreso 2025"
                  className="absolute inset-0 w-full h-full object-cover opacity-60 mix-blend-overlay group-hover:scale-105 transition-transform duration-700"
                />
                <div className="relative z-10 w-20 h-20 bg-congress-cyan rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(34,211,238,0.5)] group-hover:scale-110 transition-transform duration-300">
                  <div className="text-white text-3xl ml-1">
                    <FiVideo />
                  </div>
                </div>
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                  <p className="text-white font-bold text-xl">Ver Resumen Edición 2025</p>
                  <p className="text-congress-cyan text-sm">Haga clic para reproducir</p>
                </div>
              </motion.div>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[900px] p-2 bg-black border-slate-800">
              <DialogHeader className="opacity-0 h-0 overflow-hidden">
                <DialogTitle>Resumen del Congreso de Logística 2025</DialogTitle>
              </DialogHeader>
              <div className="w-full">
                <AspectRatio ratio={16 / 9}>
                  <iframe
                    src="https://www.youtube.com/embed/3syPHKEDKBc?autoplay=1"
                    title="Resumen Congreso de Logística 2025"
                    className="h-full w-full rounded-md border-none"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </AspectRatio>
              </div>
            </DialogContent>
          </Dialog>
        </motion.div>
      </div>

      {/* Notas y Noticias */}
      <div className="container mx-auto px-4 relative z-10 pb-20">
        <motion.div
          className="mb-10 flex items-center gap-3"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <div className="text-3xl text-congress-cyan">
            <FiFileText />
          </div>
          <h3 className="text-3xl font-bold text-congress-blue">Notas y Noticias</h3>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          {NEWS_ARTICLES.map((news, index) => (
            <motion.a
              key={index}
              href={news.link}
              target="_blank"
              rel="noopener noreferrer"
              variants={fadeInUp}
              className="group block bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden cursor-pointer transition-all duration-300 flex flex-col h-full transform hover:-translate-y-2 hover:border-congress-cyan/40 hover:shadow-[0_20px_40px_rgba(34,211,238,0.12)]"
              style={{ textDecoration: 'none' }}
            >
              {/* Barra superior animada */}
              <div className="h-1 w-full bg-gradient-to-r from-congress-blue to-congress-cyan transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-500" />
              <div className="p-7 flex flex-col flex-grow">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-congress-cyan group-hover:animate-ping" />
                    <span className="text-congress-cyan font-semibold text-sm">{news.date}</span>
                  </div>
                  <span className="text-slate-300 group-hover:text-congress-cyan transition-colors duration-300"><FiExternalLink size={15} /></span>
                </div>
                <h4 className="text-lg font-bold text-congress-blue mb-3 leading-snug group-hover:text-congress-cyan transition-colors duration-300">{news.title}</h4>
                <p className="text-slate-600 leading-relaxed flex-grow text-sm group-hover:text-slate-700 transition-colors duration-300">
                  {news.resume}
                </p>
                <div className="inline-flex items-center text-congress-blue font-bold mt-5 text-sm group-hover:text-congress-cyan transition-colors duration-300">
                  Leer nota completa
                  <svg className="w-4 h-4 ml-2 transform group-hover:translate-x-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                  </svg>
                </div>
              </div>
            </motion.a>
          ))}
        </motion.div>
      </div>
    </section>
    </>
  );
}
