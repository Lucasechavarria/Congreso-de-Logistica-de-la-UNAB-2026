import { motion } from "framer-motion";
import FloatingParticles from "@/components/FloatingParticles";
import { FiCamera, FiVideo, FiFileText } from "react-icons/fi";

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
  { url: "/images/historia-1.png", alt: "Apertura del Congreso" },
  { url: "/images/historia-2.png", alt: "Networking y Stands" },
  { url: "/images/historia-3.png", alt: "Disertantes en acción" },
  { url: "/images/congreso.jpg", alt: "Público en el auditorio" },
  { url: "/images/congress-audience.jpg", alt: "Asistentes interactuando" }
];

const NEWS_ARTICLES = [
  {
    title: "Éxito rotundo en la Primera Edición",
    date: "10 de Noviembre, 2025",
    resume: "Más de 2000 personas y 80 empresas se reunieron en el Campus UNaB para debatir sobre el futuro del sector logístico en Argentina. Un hito histórico para la región.",
    link: "#"
  },
  {
    title: "Innovación y Sostenibilidad como ejes",
    date: "12 de Noviembre, 2025",
    resume: "Los paneles de expertos destacaron la necesidad de adoptar prácticas sustentables y tecnologías disruptivas en el transporte multimodal.",
    link: "#"
  },
  {
    title: "Nuevas alianzas estratégicas",
    date: "15 de Noviembre, 2025",
    resume: "Durante las rondas de networking, se consolidaron acuerdos clave entre empresas tecnológicas y operadoras logísticas nacionales.",
    link: "#"
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
          <FiCamera className="text-3xl text-congress-cyan" />
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
          
          {/* Espacio para Video (Placeholder) */}
          <motion.div
            variants={fadeInUp}
            className="overflow-hidden rounded-2xl shadow-lg border border-slate-200 group cursor-pointer bg-slate-900 flex items-center justify-center min-h-[250px] relative"
          >
            <img src="/images/congress-audience.jpg" alt="Video cover" className="absolute inset-0 w-full h-full object-cover opacity-40 mix-blend-overlay group-hover:scale-105 transition-transform duration-700" />
            <div className="relative z-10 w-16 h-16 bg-congress-cyan rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(34,211,238,0.5)] group-hover:scale-110 transition-transform duration-300">
              <FiVideo className="text-white text-2xl ml-1" />
            </div>
            <div className="absolute bottom-6 left-6 right-6">
               <p className="text-white font-semibold text-lg">Resumen del Evento (Video)</p>
            </div>
          </motion.div>
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
          <FiFileText className="text-3xl text-congress-cyan" />
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
            <motion.div
              key={index}
              variants={fadeInUp}
              className="bg-white rounded-2xl p-8 shadow-xl border border-slate-100 hover:border-congress-cyan/30 hover:shadow-2xl transition-all duration-300 flex flex-col h-full transform hover:-translate-y-2 card-glow-hover"
            >
              <div className="text-congress-cyan font-semibold text-sm mb-3">{news.date}</div>
              <h4 className="text-xl font-bold text-congress-blue mb-4 leading-snug">{news.title}</h4>
              <p className="text-slate-600 leading-relaxed flex-grow">
                {news.resume}
              </p>
              <a href={news.link} className="inline-flex items-center text-congress-blue font-bold mt-6 hover:text-congress-cyan transition-colors">
                Leer más
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </a>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
