import { motion } from "framer-motion";
import FloatingParticles from "@/components/FloatingParticles";
import { FiCamera, FiVideo, FiFileText } from "react-icons/fi";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { AspectRatio } from "@/components/ui/aspect-ratio";

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
  { url: "/images/edicion-2025/2025-gallery-1.webp", alt: "Apertura de la Primera Edición 2025" },
  { url: "/images/edicion-2025/2025-gallery-2.webp", alt: "Autoridades y referentes del sector" },
  { url: "/images/edicion-2025/2025-gallery-3.webp", alt: "Networking entre empresas" },
  { url: "/images/edicion-2025/2025-gallery-4.webp", alt: "Paneles de expertos en logística" },
  { url: "/images/edicion-2025/2025-gallery-5.webp", alt: "Asistentes y comunidad universitaria" },
  { url: "/images/edicion-2025/2025-gallery-6.webp", alt: "Exposición de stands" },
  { url: "/images/edicion-2025/2025-gallery-7.webp", alt: "Debates y rondas de negocios" },
  { url: "/images/edicion-2025/2025-gallery-8.webp", alt: "Innovación tecnológica en el campus" },
  { url: "/images/edicion-2025/2025-gallery-9.webp", alt: "Cierre de la jornada 2025" },
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
    resume: "Reseña del éxito institucional del congreso, destacando la sinergia entre la universidad, el sector público y las empresas líderes del transporte multimodal.",
    link: "https://eldiariodemalvinas.com.ar/municipios-bonaerenses/primer-congreso-de-logistica-y-transporte-de-la-unab/"
  },
  {
    title: "ARLOG: Capacitación y Compromiso",
    date: "20 de Noviembre, 2025",
    resume: "La Asociación Argentina de Logística Empresarial destaca su participación activa en el evento, impulsando la formación y profesionalización del sector.",
    link: "https://arlog.org/arlog-participo-del-1-congreso-de-logistica-y-transporte-de-la-universidad-nacional-guillermo-brown/"
  }
];

export default function SobreElCongreso() {
  return (
    <section className="py-20 bg-slate-50 relative overflow-hidden min-h-screen">
      <FloatingParticles count={20} color="rgba(37, 99, 235, 0.1)" />

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
            >
              <div className="relative w-full h-64 lg:h-full min-h-[250px] bg-slate-200">
                <img
                  src={img.url}
                  alt={img.alt}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-6">
                  <p className="text-white font-semibold text-lg">{img.alt}</p>
                </div>
              </div>
            </motion.div>
          ))}

          {/* Espacio para Video - Modo Cine con Modal */}
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
                  <p className="text-congress-cyan-light text-sm">Haga clic para reproducir</p>
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
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
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
              className="group block bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden cursor-pointer transition-all duration-400 flex flex-col h-full transform hover:-translate-y-3 hover:border-congress-cyan/50 hover:shadow-[0_20px_40px_rgba(34,211,238,0.15)] card-glow-hover"
              style={{ textDecoration: 'none' }}
            >
              {/* Barra de color superior animada */}
              <div className="h-1 w-full bg-gradient-to-r from-congress-blue to-congress-cyan transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-500" />
              <div className="p-8 flex flex-col flex-grow">
                <div className="flex items-center gap-2 mb-3">
                  <span className="inline-block w-2 h-2 rounded-full bg-congress-cyan group-hover:animate-ping" />
                  <span className="text-congress-cyan font-semibold text-sm">{news.date}</span>
                </div>
                <h4 className="text-xl font-bold text-congress-blue mb-4 leading-snug group-hover:text-congress-cyan transition-colors duration-300">{news.title}</h4>
                <p className="text-slate-600 leading-relaxed flex-grow group-hover:text-slate-700 transition-colors duration-300">
                  {news.resume}
                </p>
                <div className="inline-flex items-center text-congress-blue font-bold mt-6 group-hover:text-congress-cyan transition-colors duration-300">
                  Leer más
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
  );
}
