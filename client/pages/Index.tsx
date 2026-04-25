import { useEffect, useRef } from "react";
import { useLocation, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  FiCalendar,
  FiMapPin,
  FiMail,
  FiUsers,
  FiClock,
  FiAward,
} from "react-icons/fi";
import { FaTrain, FaCar } from "react-icons/fa";
import CountdownTimer from "@/components/CountdownTimer";
import EmpresasCarousel2026 from "@/components/EmpresasCarousel2026";
import SponsorsSection from "@/components/SponsorsSection";
import PreviousCongressSection from "@/components/PreviousCongressSection";
import FloatingParticles from "@/components/FloatingParticles";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { motion, Variants } from "framer-motion";

// Animation Variants
const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
};

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: "easeOut" } },
};

// Data for participation modalities to unify styles
const PARTICIPATION_MODALITIES = [
  {
    id: "expositor",
    icon: FiUsers,
    title: "Expositor con Stand",
    description:
      "Presenta tu empresa, servicios o proyectos en un espacio dedicado. Conecta directamente con profesionales del sector y genera nuevas oportunidades de negocio.",
    gradient: "from-congress-blue/90 to-congress-cyan/80",
    iconGradient: "from-congress-blue to-congress-cyan",
  },
  {
    id: "tecnologia",
    icon: FiAward,
    title: "Presentador de Tecnología",
    description:
      "Muestra vehículos, maquinaria o tecnologías innovadoras. Demuestra las últimas innovaciones que están transformando el sector logístico y de transporte.",
    gradient: "from-congress-cyan/90 to-congress-blue/80",
    iconGradient: "from-congress-cyan to-congress-cyan-light",
  },
  {
    id: "taller",
    icon: FiClock,
    title: "Coordinador de Taller",
    description:
      "Lidera un taller práctico o instancia demostrativa. Comparte tu expertise y conocimientos prácticos con otros profesionales del sector.",
    gradient: "from-congress-blue-dark/90 to-congress-cyan/80",
    iconGradient: "from-congress-blue-dark to-congress-blue",
  },
  {
    id: "otras",
    icon: FiUsers,
    title: "Otras Modalidades",
    description:
      "¿Tienes una propuesta diferente? Nos encantaría conocer otras modalidades que consideres relevantes y de interés para el sector. Contáctanos para conversarlo.",
    gradient: "from-congress-cyan-light/90 to-congress-blue-dark/80",
    iconGradient: "from-congress-cyan-light to-congress-blue",
  },
];

export default function Index() {
  const mapRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    if (location.hash === "#mapa" && mapRef.current) {
      mapRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [location]);

  const scrollToMap = () => {
    mapRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  return (
    <Layout>
      <Helmet>
        <title>Congreso Logística y Transporte 2026 | UNAB</title>
        <meta name="description" content="Únete al Congreso de Logística y Transporte 2026 en la UNAB. Descubre tendencias en logística verde y automatización. ¡Inscríbete hoy!" />
        <meta name="keywords" content="Congreso de logística y transporte Argentina 2026, Tendencias en logística verde y sostenibilidad en Argentina, Automatización de carga y descarga, Congreso universitario de logística sustentable UNAB 2026" />
        <link rel="canonical" href="https://www.congresologistica.unab.edu.ar/congreso-logistica-unab-2026" />
        {/* Schema.org for Event (Google Rich Snippets) */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Event",
            "name": "Congreso de Logística y Transporte 2026",
            "startDate": "2026-11-07T09:00",
            "endDate": "2026-11-08T18:00",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
              "@type": "Place",
              "name": "Campus Universidad Nacional Guillermo Brown (UNAB)",
              "address": {
                "@type": "PostalAddress",
                "streetAddress": "Blas Parera 132",
                "addressLocality": "Burzaco",
                "addressRegion": "Buenos Aires",
                "postalCode": "1852",
                "addressCountry": "AR"
              }
            },
            "image": [
              "https://www.congresologistica.unab.edu.ar/images/CONGRESO-LOGISTICA-2.png"
            ],
            "description": "Únete al Congreso de Logística y Transporte 2026 en la UNAB. Descubre tendencias en logística verde y automatización.",
            "offers": {
              "@type": "Offer",
              "url": "https://www.congresologistica.unab.edu.ar/registro-participantes",
              "price": "0",
              "priceCurrency": "ARS",
              "availability": "https://schema.org/InStock",
              "validFrom": "2026-03-01T00:00"
            },
            "organizer": {
              "@type": "Organization",
              "name": "Universidad Nacional Guillermo Brown",
              "url": "https://www.unab.edu.ar/"
            }
          })}
        </script>
      </Helmet>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-congress-blue to-congress-blue-dark text-white py-20 degradado-hero overflow-hidden">
        <FloatingParticles count={30} />
        {/* Decorative SVG Pattern Background */}
        <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="logisticsPattern" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
                <path d="M0 30h60 M30 0v60" stroke="#a78bfa" strokeWidth="1" strokeDasharray="4 4" fill="none" />
                <circle cx="30" cy="30" r="3" fill="#a78bfa" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#logisticsPattern)" />
          </svg>
        </div>

        <div className="relative z-10 container mx-auto px-4">
          <motion.div
            className="max-w-4xl mx-auto text-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
          >
            <motion.div className="mb-8" variants={fadeInUp}>
              <h1 className="text-4xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
                CONGRESO DE LOGÍSTICA
                <span className="block text-congress-cyan mt-2">Y TRANSPORTE</span>
              </h1>
              <motion.div
                className="w-24 h-1 bg-congress-cyan mx-auto mb-12"
                initial={{ width: 0 }}
                whileInView={{ width: 96 }}
                transition={{ duration: 1, delay: 0.5 }}
                viewport={{ once: true }}
              ></motion.div>
              <h2 className="text-xl md:text-2xl font-semibold mb-4 text-congress-white">
                NUEVAS OPORTUNIDADES, GRANDES DESAFÍOS
              </h2>

              <p className="text-congress-cyan-light font-bold text-2xl mb-6">
                7 de Noviembre, 2026
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-center mb-16">
                <motion.img
                  src="/images/LogoUnab.png"
                  alt="Logo de la Universidad Nacional Guillermo Brown"
                  className="h-28 md:h-36 w-auto drop-shadow-[0_0_20px_rgba(167,139,250,0.4)] bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/20"
                  variants={scaleIn}
                />
              </div>

              <div className="mb-8">
                <CountdownTimer />
              </div>

              <div className="flex flex-col md:flex-row items-center justify-center gap-4 mb-10">
                <Link to="/registro-empresas">
                  <Button
                    size="lg"
                    className="bg-congress-cyan hover:bg-congress-cyan-light text-congress-blue-dark font-bold px-8 py-6 text-lg shadow-xl hover:shadow-2xl transition-all duration-300 btn-shimmer border-2 border-congress-cyan-light w-full md:w-auto"
                  >
                    Postulate como Expositor
                  </Button>
                </Link>
                <Link to="/registro-disertante">
                  <Button
                    size="lg"
                    className="bg-white/10 hover:bg-white/20 text-white font-bold px-8 py-6 text-lg backdrop-blur-md border border-white/20 shadow-xl transition-all duration-300 w-full md:w-auto hover:-translate-y-1"
                  >
                    Postulate como Disertante
                  </Button>
                </Link>
                <Link to="/registro-participantes">
                  <Button
                    size="lg"
                    className="bg-white hover:bg-slate-100 text-congress-blue-dark font-bold px-8 py-6 text-lg shadow-xl hover:shadow-2xl transition-all duration-300 w-full md:w-auto hover:-translate-y-1"
                  >
                    Inscribite como Visitante
                  </Button>
                </Link>
              </div>
            </motion.div>

            <motion.div
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-center mt-10"
              variants={staggerContainer}
            >
              {/* Card FECHA */}
              <motion.div
                variants={fadeInUp}
                className="card-info group bg-white/10 backdrop-blur-sm rounded-lg p-8 flex flex-col items-center justify-center min-h-[210px] transition-all duration-300 hover:bg-white/20 hover:shadow-xl card-glow-hover"
              >
                <div className="w-8 h-8 mb-3 text-congress-blue-dark icon-hover-spin">
                  <FiCalendar size="100%" />
                </div>
                <h3 className="font-semibold mb-2">Fecha</h3>
                <p className="text-lg text-center">7 de Noviembre 2026</p>
              </motion.div>
              {/* Card UBICACION */}
              <motion.div
                variants={fadeInUp}
                className="card-info group bg-white/10 backdrop-blur-sm rounded-lg p-8 flex flex-col items-center justify-center min-h-[210px] transition-all duration-300 hover:bg-white/20 hover:shadow-xl cursor-pointer card-glow-hover"
                onClick={scrollToMap}
              >
                <div className="w-8 h-8 mb-3 text-congress-blue-dark icon-hover-spin">
                  <FiMapPin size="100%" />
                </div>
                <h3 className="font-semibold mb-2">Ubicación</h3>
                <p className="text-lg text-center">
                  Campus UNaB
                  <br />
                  Blas Parera 132, Burzaco
                </p>
              </motion.div>
              {/* Card CONTACTO */}
              <motion.div variants={fadeInUp}>
                <a
                  href="mailto:congresologisticaytransporte@unab.edu.ar"
                  className="block"
                >
                  <div className="card-info group bg-white/10 backdrop-blur-sm rounded-lg p-8 flex flex-col items-center justify-center min-h-[210px] transition-all duration-300 hover:bg-white/20 hover:shadow-xl card-glow-hover">
                    <div className="w-8 h-8 mb-3 text-congress-blue-dark icon-hover-spin">
                      <FiMail size="100%" />
                    </div>
                    <h3 className="font-semibold mb-2">Contacto</h3>
                    <p className="text-lg break-words text-center leading-tight">
                      congresologisticaytransporte
                      <br />
                      @unab.edu.ar
                    </p>
                  </div>
                </a>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Convocatoria Abierta Section */}
      <section aria-labelledby="convocatoria-titulo" className="py-20 relative overflow-hidden bg-[#0a0514] border-y border-white/5">
        {/* Cinematic 8-second looping video feel (Intermodal ecosystem & glassmorphism) */}
        <div className="absolute inset-0 z-0">
          <FloatingParticles count={30} color="rgba(176, 126, 238, 0.4)" />
          {/* Neon routing lines */}
          <div className="absolute top-1/3 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#9c62de] to-transparent opacity-50 shadow-[0_0_15px_rgba(156,98,222,0.8)]"></div>
          <div className="absolute top-2/3 right-0 w-full h-[1px] bg-gradient-to-l from-transparent via-[#b07eee] to-transparent opacity-30 shadow-[0_0_15px_rgba(176,126,238,0.8)]"></div>

          {/* Deep violet / vibrant purple glowing orbs */}
          <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#3a1b77] rounded-full mix-blend-screen filter blur-[120px] opacity-60 animate-pulse"></div>
          <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#210d51] rounded-full mix-blend-screen filter blur-[120px] opacity-80 animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        <div className="container relative z-10 mx-auto px-4">
          <motion.div
            className="max-w-5xl mx-auto rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(58,27,119,0.5)] border border-white/10 mt-10"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <div className="bg-gradient-to-br from-[#210d51]/80 to-[#0f0728]/90 backdrop-blur-xl p-8 md:p-12 lg:p-16 flex flex-col md:flex-row items-center gap-10">
              <motion.div variants={fadeInUp} className="flex-1 text-center md:text-left">

                <h2 className="text-3xl md:text-5xl font-black text-white mb-4 tracking-tight">
                  CONVOCATORIA <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#9c62de] to-[#b07eee]">ABIERTA</span>
                </h2>
                <p className="text-lg text-slate-300 mb-8 leading-relaxed max-w-xl mx-auto md:mx-0">
                  Formá parte del hub intermodal más grande del año. Buscamos a los referentes que están moviendo el futuro. ¿Tenés una empresa o una ponencia para compartir?
                </p>
                <div className="flex flex-col sm:flex-row items-center gap-4 justify-center md:justify-start">
                  <Link to="/registro-disertante">
                    <Button
  size="lg"
  className="bg-congress-cyan hover:bg-congress-cyan-light text-white font-bold px-8 py-6 text-lg shadow-lg hover:shadow-2xl transition-all duration-300 w-full sm:w-auto"
>
  Postular Ponencia
</Button>
                  </Link>
                  <Link to="/registro-empresas">
                    <Button
                      size="lg"
                      className="bg-gradient-to-r from-[#3a1b77] to-[#9c62de] hover:from-[#210d51] hover:to-[#3a1b77] text-white font-bold px-8 py-6 text-lg transition-all duration-300 w-full sm:w-auto shadow-[0_0_20px_rgba(58,27,119,0.5)] border border-[#9c62de]/50"
                    >
                      Exponer mi Empresa
                    </Button>
                  </Link>
                </div>
              </motion.div>

              {/* Decorative graphic side (Glassmorphism & Logistics) */}
              <motion.div variants={scaleIn} className="hidden lg:flex flex-1 justify-center relative">
                <div className="relative w-72 h-72">
                  {/* Glowing rings */}
                  <div className="absolute inset-0 rounded-full border-2 border-[#9c62de]/30 animate-[spin_10s_linear_infinite]"></div>
                  <div className="absolute inset-4 rounded-full border border-[#b07eee]/50 animate-[spin_15s_linear_infinite_reverse]"></div>

                  {/* Floating Glass panels */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-white/5 backdrop-blur-md rounded-2xl border border-white/20 shadow-[0_0_30px_rgba(176,126,238,0.2)] flex items-center justify-center transform rotate-12 hover:rotate-0 transition-transform duration-500">
                    <svg className="w-20 h-20 text-[#b07eee]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>

                  {/* Floating elements */}
                  <div className="absolute top-0 right-10 w-16 h-16 bg-gradient-to-br from-[#9c62de] to-[#210d51] rounded-xl flex items-center justify-center shadow-lg animate-[float-orb_4s_ease-in-out_infinite]">
                  <div className="text-white text-xl">
                    <FiUsers size="100%" />
                  </div>
                  </div>
                  <div className="absolute bottom-10 left-0 w-20 h-20 bg-gradient-to-br from-congress-cyan-light to-congress-blue rounded-full flex items-center justify-center shadow-lg animate-[float-orb_6s_ease-in-out_infinite_1s]">
                  <div className="text-white text-2xl">
                    <FiAward size="100%" />
                  </div>
                  </div>
                </div>
              </motion.div>

            </div>
          </motion.div>
        </div>
      </section>

      <SponsorsSection />

      <EmpresasCarousel2026 />

      <PreviousCongressSection />

      {/* Participation Modalities Section */}
      <section aria-labelledby="modalidades-titulo" className="py-24 relative overflow-hidden bg-gradient-to-br from-[#1a0a2e] via-congress-blue-dark to-congress-blue">
        <FloatingParticles count={40} color="rgba(139, 92, 246, 0.4)" />
        {/* Subtle Background Pattern (Logistics Particles) */}
        <div className="absolute inset-0 z-0 opacity-[0.12]">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="modalitiesPattern" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
                <path d="M0 30h60 M30 0v60" stroke="#a78bfa" strokeWidth="1" strokeDasharray="4 4" fill="none" />
                <circle cx="30" cy="30" r="3" fill="#a78bfa" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#modalitiesPattern)" />
          </svg>
        </div>

        <div className="container relative z-10 mx-auto px-4">
          <motion.div
            className="max-w-4xl mx-auto"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div className="text-center mb-16" variants={fadeInUp}>
              <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                Modalidades de Participación
              </h2>
              <div className="w-20 h-1 bg-congress-cyan mx-auto mb-8 rounded-full"></div>
              <p className="text-xl text-slate-300 leading-relaxed">
                Te invitamos a participar en la modalidad que prefieras.
              </p>
            </motion.div>

            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-8"
              variants={staggerContainer}
            >
              {PARTICIPATION_MODALITIES.map((modality) => (
                <motion.div key={modality.id} variants={scaleIn}>
                  <Card
                    className={`group flex h-full flex-col transform border border-white/10 bg-white/5 backdrop-blur-md p-6 text-center shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_8px_30px_rgb(139,92,246,0.2)] hover:border-congress-cyan/30 rounded-2xl card-glow-hover`}
                  >
                    <CardHeader className="mb-4 flex flex-col items-center justify-center">
                      <div
                        className={`mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/10 shadow-sm transition-all duration-300 border border-white/5 group-hover:bg-congress-cyan/20`}
                      >
                        <div className="h-8 w-8 text-congress-cyan transition-colors icon-hover-spin">
                          <modality.icon size="100%" />
                        </div>
                      </div>
                      <CardTitle className="text-2xl font-bold text-white transition-colors group-hover:text-congress-cyan-light">
                        {modality.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-grow">
                      <CardDescription className="text-center text-lg leading-relaxed text-slate-300 group-hover:text-slate-200">
                        {modality.description}
                      </CardDescription>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>

            <motion.div className="text-center mt-12" variants={fadeInUp}>
              <div className="relative bg-gradient-to-br from-congress-blue to-congress-blue-dark rounded-2xl p-8 border-2 border-congress-cyan shadow-2xl hover:shadow-3xl transition-all duration-300 overflow-hidden">
                {/* Efecto de brillo decorativo */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-congress-cyan/20 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-congress-cyan-light/20 rounded-full blur-2xl"></div>

                <div className="relative z-10 text-center">
                  <h3 className="text-2xl font-bold text-white mb-4 flex items-center justify-center gap-3">
                    <span className="text-3xl">💡</span>
                    ¿Interesado en Participar como Empresa?
                  </h3>
                  <p className="text-congress-cyan-light mb-6 text-lg leading-relaxed max-w-2xl mx-auto">
                    Sumate a las más de 80 empresas que ya confirmaron su
                    participación. Es una excelente oportunidad para networking,
                    visibilidad y desarrollo de negocio.
                  </p>
                  <Link to="/contacto">
                    <Button
                      size="xl"
                      className="bg-congress-cyan hover:bg-congress-cyan-light text-congress-blue-dark hover:text-congress-blue font-bold px-12 py-6 text-lg shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 border-2 border-congress-cyan-light btn-shimmer"
                    >
                      Contactar para Participar
                    </Button>
                  </Link>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Mapa Section */}
      <section id="mapa" ref={mapRef} className="py-24 bg-lavender-subtle relative overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-[0.18]">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="lightPatternMap" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(-15)">
                <path d="M0 30h60 M30 0v60" stroke="#4c1d95" strokeWidth="1.5" strokeDasharray="4 4" fill="none" />
                <circle cx="30" cy="30" r="3" fill="#4c1d95" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#lightPatternMap)" />
          </svg>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            className="max-w-4xl mx-auto text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
          >
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-extrabold text-[#2d1854] tracking-tight mb-6">
              ¿Cómo llegar?
            </motion.h2>
            <motion.div variants={fadeInUp} className="w-16 h-1 bg-[#8b5cf6] mx-auto mb-8 rounded-full"></motion.div>
            <motion.p variants={fadeInUp} className="text-xl text-slate-900 font-medium mb-8">
              El congreso se realizará en el Campus de la Universidad Nacional
              Guillermo Brown, ubicado en Blas Parera 132. ¡Te esperamos!
            </motion.p>
          </motion.div>

          <div className="max-w-5xl mx-auto">
            {/* Acordeón para opciones de transporte con estilos personalizados */}
            <Accordion
              type="single"
              collapsible
              className="w-full max-w-4xl mx-auto space-y-4"
            >
              <AccordionItem
                value="caba"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  Desde CABA (Obelisco)
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <ul className="space-y-4">
                    <li>
                      <strong>Transporte Público:</strong> Tomar Subte hasta
                      Constitución, luego Tren Roca (ramales A. Korn, Glew)
                      hasta la estación Burzaco. Desde allí, colectivos locales
                      o 15 min a pie.
                    </li>
                    <li>
                      <strong>En Auto:</strong> Tomar Au. 25 de Mayo, luego Au.
                      Riccheri y Camino de Cintura (Ruta 4) hasta Av. Espora. El
                      viaje dura aprox. 45-60 min.
                    </li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="adrogue"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  Desde Adrogué
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <ul className="space-y-4">
                    <li>
                      <strong>506 (Gendarmería - Por Bynnon):</strong> Av Espora
                      - esq. Ricardo Rojas
                    </li>
                    <li>
                      <strong>79 (Constitución - San Vicente):</strong> Av
                      Espora (Colegio Nacional de Adrogué)
                    </li>
                    <li>
                      <strong>74 (A):</strong> Av Espora (Colegio Nacional de
                      Adrogué)
                    </li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="burzaco"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  Desde Burzaco
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <ul className="space-y-4">
                    <li>
                      <strong>506 (Gendarmería - Por Bynnon):</strong> Av Espora
                      - esq. Ricardo Rojas
                    </li>
                    <li>
                      <strong>266 (A):</strong> Estación Burzaco
                    </li>
                    <li>
                      <strong>74 (A):</strong>                      esq. Ricardo Rojas
                    </li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="longchamps"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  Desde Longchamps
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <ul className="space-y-4">
                    <li>
                      <strong>79 (San Vicente):</strong> Constitución (Chiesa y
                      Francia)
                    </li>
                    <li>
                      <strong>506 (San Jose, Por Bynnon):</strong> Alsina y
                      Magdalena Motti de Tieghi
                    </li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="tren"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  En Tren (Línea Roca)
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <p>
                    Las estaciones más cercanas son <strong>Adrogué</strong>,{" "}
                    <strong>Burzaco</strong> y <strong>Longchamps</strong>.
                    <br />
                    Desde ambas, puedes tomar un colectivo o servicio de auto
                    hasta el campus.
                  </p>
                  <p className="mt-2 text-xs text-gray-400">
                    Nota: Se está construyendo la nueva estación "Universidad
                    Guillermo Brown". Verifica su estado para la fecha del
                    evento.
                  </p>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="auto"
                className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 accordion-animated-border"
              >
                <AccordionTrigger className="px-6 py-5 text-[#2d1854] text-lg font-bold hover:bg-slate-50 transition-colors hover:no-underline">
                  En Auto
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6 text-slate-900 font-medium bg-white leading-relaxed text-base border-t border-slate-100 mt-2 pt-4">
                  <p>
                    <strong>Acceso principal:</strong> Por Av. Espora, a 3
                    cuadras de la Ruta Provincial 4 (Camino de Cintura).
                  </p>
                  <p>
                    <strong>GPS:</strong> Blas Parera 132, Burzaco.
                  </p>
                  <p>
                    <strong>Estacionamiento:</strong> Habrá estacionamiento
                    disponible en un predio alejado para los asistentes al
                    congreso.
                  </p>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          <div className="flex justify-center mt-12">
            <div className="w-full max-w-4xl rounded-2xl border-4 border-[#8b5cf6]/30 overflow-hidden shadow-2xl bg-white p-2 relative">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3274.70762014795!2d-58.38742082408727!3d-34.838443069932694!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x95bcd5aebf3ce8ad%3A0x61e0dc504088584!2sUniversidad%20Nacional%20Guillermo%20Brown%20(UNAB)!5e0!3m2!1ses-419!2sar!4v1756827211940!5m2!1ses-419!2sar"
                width="100%"
                height="450"
                style={{
                  border: 0,
                  borderRadius: '12px',
                  filter: 'grayscale(100%) contrast(110%) brightness(90%) hue-rotate(260deg)'
                }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Ubicación del Congreso - Universidad Nacional Guillermo Brown"
              ></iframe>
            </div>
          </div>

          <motion.div
            className="max-w-4xl mx-auto mt-8 text-center"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className="bg-white rounded-2xl p-6 shadow-md border border-slate-200 card-glow-hover">
              <h3 className="text-xl font-semibold text-[#3b1066] mb-4">
                Dirección
              </h3>
              <p className="text-lg text-slate-800 mb-2">
                <strong>Universidad Nacional Guillermo Brown</strong>
              </p>
              <p className="text-lg text-slate-600 mb-4">
                Blas Parera 132, Burzaco, Buenos Aires
              </p>
              <Button
                size="xl"
                className="bg-[#3b1066] hover:bg-[#4c1d95] text-white font-bold px-12 py-6 text-lg shadow-[0_0_20px_rgba(59,16,102,0.2)] hover:shadow-[0_0_40px_rgba(59,16,102,0.4)] transform hover:scale-105 transition-all duration-300 btn-shimmer"
                asChild
              >
                <a
                  href="https://maps.google.com/?q=Universidad+Nacional+Guillermo+Brown+Blas+Parera+132+Adrogué+Buenos+Aires"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Abrir en Google Maps
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section (El Gran Final) */}
      <section className="bg-gradient-to-br from-[#1a0a2e] via-congress-blue-dark to-congress-blue text-white relative overflow-hidden py-24">
        {/* Decorative SVG Pattern Background (Particles) */}
        <div className="absolute inset-0 z-0 opacity-[0.1] pointer-events-none">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="finalCtaPattern" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(15)">
                <path d="M0 30h60 M30 0v60" stroke="#a78bfa" strokeWidth="1" strokeDasharray="4 4" fill="none" />
                <circle cx="30" cy="30" r="3" fill="#a78bfa" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#finalCtaPattern)" />
          </svg>
        </div>

        {/* Animated Glow Particles */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-[#8b5cf6]/20 blur-[120px] rounded-full pointer-events-none animate-pulse z-0"></div>

        <motion.div
          className="container mx-auto px-4 text-center relative z-10"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-extrabold mb-6 tracking-tight">
            ¿Listo para ser parte del futuro?
          </motion.h2>
          <motion.div variants={fadeInUp} className="w-24 h-1 bg-white/20 mx-auto mb-8 rounded-full"></motion.div>
          <motion.p variants={fadeInUp} className="text-xl md:text-2xl mb-4 max-w-3xl mx-auto text-slate-300 leading-relaxed">
            Comparte con nosotros este importante evento que marcará el rumbo de
            la logística y el transporte en Argentina y Latinoamérica.
          </motion.p>
          <motion.p variants={fadeInUp} className="text-congress-cyan font-bold text-xl mb-10">
            Sábado 7 de Noviembre de 2026 - Campus UNaB
          </motion.p>

          <motion.div variants={scaleIn} className="flex flex-col md:flex-row items-center justify-center gap-6 mt-12">
            <Link to="/registro-empresas">
              <Button
                size="xxl"
                className="bg-congress-cyan hover:bg-congress-cyan-light text-congress-blue-dark font-black px-12 py-8 text-xl shadow-[0_0_30px_rgba(167,139,250,0.3)] hover:shadow-[0_0_50px_rgba(167,139,250,0.5)] transform hover:scale-105 transition-all duration-300 border-2 border-congress-cyan-light btn-shimmer w-full md:w-auto"
              >
                Ser Expositor
              </Button>
            </Link>
            <Link to="/registro-disertante">
              <Button
                size="xxl"
                className="bg-white/10 hover:bg-white/20 text-white font-black px-12 py-8 text-xl backdrop-blur-md border border-white/20 shadow-xl transition-all duration-300 w-full md:w-auto hover:-translate-y-1"
              >
                Ser Disertante
              </Button>
            </Link>
            <Link to="/registro-participantes">
              <Button
                size="xxl"
                className="bg-white hover:bg-slate-100 text-congress-blue-dark font-black px-12 py-8 text-xl shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 w-full md:w-auto"
              >
                Asistir Gratis
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </section>
    </Layout>
  );
}
