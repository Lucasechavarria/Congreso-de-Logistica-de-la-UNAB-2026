import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  FiUsers,
  FiClock,
  FiHome,
  FiTrendingUp,
  FiStar,
  FiMail,
} from "react-icons/fi";
import { FaHandshake } from "react-icons/fa";
import { Link } from "react-router-dom";
import LargeLogoCarousel from "@/components/LargeLogoCarousel";
import FloatingParticles from "@/components/FloatingParticles";
import { motion } from "framer-motion";
import { EditionSelector } from "@/components/EditionSelector";
import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { useEmpresas } from "@/hooks/use-empresas";
import { ALL_LOGOS } from "@/data/logos";

const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

// Constantes para mejorar mantenibilidad
const CONTACT_EMAIL = "congresologisticaytransporte@unab.edu.ar";
const EVENT_DATE = "7 de Noviembre 2026";
const EVENT_LOCATION = "Campus UNaB Blas Parera 132, Burzaco";
const EXPECTED_ATTENDEES = "más de 500 asistentes";

// Datos estructurados para los beneficios
const BENEFITS = [
  {
    id: "visibility",
    icon: FiTrendingUp,
    title: "Visibilidad de Marca",
    description: `Posiciona tu empresa frente a ${EXPECTED_ATTENDEES} especializados en logística y transporte, incluyendo tomadores de decisión.`,
    gradient: "from-congress-blue/90 to-congress-cyan/80",
    iconGradient: "from-congress-blue to-congress-cyan",
  },
  {
    id: "networking",
    icon: FaHandshake,
    title: "Networking Estratégico",
    description:
      "Conecta con empresas del sector, proveedores, clientes potenciales y líderes de la industria en un ambiente propicio para los negocios.",
    gradient: "from-congress-cyan/90 to-congress-blue/80",
    iconGradient: "from-congress-cyan to-congress-cyan-light",
  },
  {
    id: "leadership",
    icon: FiStar,
    title: "Liderazgo de Pensamiento",
    description:
      "Posiciona a tu empresa como líder de innovación compartiendo conocimientos y experiencias con la comunidad profesional.",
    gradient: "from-congress-blue-dark/90 to-congress-cyan/80",
    iconGradient: "from-congress-blue-dark to-congress-blue",
  },
  {
    id: "business",
    icon: FiHome,
    title: "Desarrollo de Negocio",
    description:
      "Genera nuevas oportunidades comerciales y fortalece relaciones con clientes actuales en un contexto académico y profesional.",
    gradient: "from-congress-cyan-light/90 to-congress-blue-dark/80",
    iconGradient: "from-congress-cyan-light to-congress-blue",
    showContact: true,
  },
];

// Datos para las cards de información
const INFO_CARDS = [
  {
    id: "date",
    icon: FiClock,
    title: "Fecha",
    description: EVENT_DATE,
    gradient: "from-congress-blue to-congress-cyan",
  },
  {
    id: "location",
    icon: FiHome,
    title: "Ubicación",
    description: EVENT_LOCATION,
    gradient: "from-congress-cyan to-congress-blue",
    link: "/#mapa",
  },
  {
    id: "contact",
    icon: FiUsers,
    title: "Contacto",
    description: CONTACT_EMAIL.replace("@", "\n@"),
    gradient: "from-congress-blue-dark to-congress-cyan-light",
    link: `mailto:${CONTACT_EMAIL}`,
  },
];

// Componente para las cards de información
function InfoCard({ card }: { card: (typeof INFO_CARDS)[0] }) {
  const CardComponent = (
    <Card className="group h-full flex flex-col items-center rounded-2xl border-0 bg-white/10 p-8 shadow-lg backdrop-blur-md transition-all duration-300 hover:scale-105 hover:shadow-2xl">
      <div
        className={`w-14 h-14 bg-gradient-to-br ${card.gradient} rounded-full flex items-center justify-center mb-4 shadow-md group-hover:shadow-xl transition-shadow duration-300`}
      >
        <div className="h-8 w-8 text-white">
          <card.icon size="100%" />
        </div>
      </div>
      <CardTitle className="mb-2 text-lg font-bold text-white">
        {card.title}
      </CardTitle>
      <CardDescription className="whitespace-pre-line text-center text-base text-white">
        {card.description}
      </CardDescription>
    </Card>
  );

  if (card.link) {
    return card.link.startsWith("mailto:") ? (
      <a href={card.link} className="group">
        {CardComponent}
      </a>
    ) : (
      <Link to={card.link} className="group">
        {CardComponent}
      </Link>
    );
  }

  return CardComponent;
}

// Componente para las cards de beneficios
function BenefitCard({ benefit }: { benefit: (typeof BENEFITS)[0] }) {
  return (
    <Card
      className={`group h-full flex flex-col transform border-0 bg-gradient-to-br p-6 text-center shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl ${benefit.gradient} rounded-2xl`}
    >
      <CardHeader className="mb-4 flex flex-col items-center justify-center">
        <div
          className={`mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br shadow-lg transition-all duration-300 group-hover:shadow-xl ${benefit.iconGradient}`}
        >
          <div className="h-10 w-10 text-white">
            <benefit.icon size="100%" />
          </div>
        </div>
        <CardTitle className="text-2xl font-bold text-white transition-colors">
          {benefit.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col justify-center">
        <CardDescription className="text-center text-lg leading-relaxed text-congress-white/90">
          {benefit.description}
          {benefit.showContact && (
            <span className="mt-4 block text-base font-semibold text-white">
              <span className="inline-block mr-2 align-text-bottom h-5 w-5">
                <FiMail size="100%" />
              </span>
              {CONTACT_EMAIL.replace("@", "\n@")}
            </span>
          )}
        </CardDescription>
      </CardContent>
    </Card>
  );
}

export default function Empresas() {
  const [selectedEditionId, setSelectedEditionId] = useState<number | null>(null);
  const { logosForCarousel } = useEmpresas(selectedEditionId);
  const empresasToDisplay = logosForCarousel.length > 0 ? logosForCarousel : ALL_LOGOS;

  return (
    <>
      <Helmet>
        <title>Empresas Participantes | Congreso de Logística 2026</title>
        <meta name="description" content="Conoce a las más de 80 empresas del sector logístico e intermodal que apoyan y participan en el Congreso de Logística y Transporte 2026 en la UNAB." />
        <meta name="keywords" content="empresas logistica, sponsors unab, patrocinadores congreso, empresas transporte" />
        <link rel="canonical" href="https://www.congresologistica.unab.edu.ar/empresas" />
        {empresasToDisplay && empresasToDisplay.length > 0 && (
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@graph": empresasToDisplay.map((logo, idx) => ({
                "@type": "Organization",
                "@id": `https://www.congresologistica.unab.edu.ar/empresas#empresa-${idx}`,
                "name": logo.alt || "Empresa Participante",
                "image": logo.src,
                "url": "https://www.congresologistica.unab.edu.ar/empresas",
                "sponsor": {
                  "@type": "Event",
                  "name": "Congreso de Logística y Transporte UNAB 2026"
                }
              }))
            })}
          </script>
        )}
      </Helmet>
      {/* Call to Action - Immersive Neo-Logistics */}
      <section className="py-24 relative overflow-hidden bg-[#0A0514]">
        {/* Dynamic Background */}
        <div className="absolute inset-0 z-0">
          {/* Glowing orbs */}
          <div className="absolute -top-32 -right-32 w-96 h-96 bg-congress-blue-dark rounded-full mix-blend-screen filter blur-[120px] opacity-80 animate-pulse"></div>
          <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-[#210D51] rounded-full mix-blend-screen filter blur-[100px] opacity-90 animate-pulse" style={{ animationDelay: '3s' }}></div>
          {/* Grid overlay */}
          <div className="absolute inset-0 z-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:30px_30px] mask-image-[radial-gradient(ellipse_at_center,black_40%,transparent_100%)]"></div>
          <FloatingParticles count={25} color="rgba(156, 98, 222, 0.5)" />
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            className="max-w-4xl mx-auto text-center bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-10 md:p-16 shadow-[0_0_50px_rgba(58,27,119,0.3)] relative overflow-hidden"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            {/* Inner glow lines */}
            <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-transparent via-congress-cyan-light to-transparent"></div>
            <div className="absolute right-0 top-0 w-1 h-full bg-gradient-to-b from-transparent via-congress-cyan-light to-transparent"></div>

            <motion.h2 variants={fadeInUp} className="text-3xl md:text-5xl font-black text-white mb-6 tracking-tight">
              ¿Listo para <span className="text-transparent bg-clip-text bg-gradient-to-r from-congress-cyan-light to-congress-cyan text-glow">Exponer tu Empresa</span>?
            </motion.h2>

            <motion.p variants={fadeInUp} className="text-xl mb-10 text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Únete a las empresas más innovadoras del sector y presenta tus productos y servicios al público especializado.
            </motion.p>

            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row justify-center items-center gap-6">
              <Link to="/registro-empresas" className="w-full sm:w-auto">
                <Button
                  size="xl"
                  className="w-full sm:w-auto bg-gradient-to-r from-[#3a1b77] to-congress-blue hover:from-congress-blue hover:to-[#3a1b77] text-white font-bold px-10 py-6 text-xl shadow-[0_0_30px_rgba(58,27,119,0.5)] border border-congress-cyan/30 rounded-xl transition-all duration-300 transform hover:scale-105 group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-3">
                    Inscribir a mi Empresa
                    <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                  </span>
                  <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-in-out"></div>
                </Button>
              </Link>
            </motion.div>

            {/* Contact Footer within Card */}
            <motion.div variants={fadeInUp} className="mt-14 pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-center gap-6 text-slate-400">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                  <div className="h-5 w-5 text-congress-cyan-light">
                    <FiMail size="100%" />
                  </div>
                </div>
                <a href={`mailto:${CONTACT_EMAIL}`} className="hover:text-white transition-colors">
                  {CONTACT_EMAIL}
                </a>
              </div>
              <div className="hidden md:block w-1.5 h-1.5 rounded-full bg-white/20"></div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                  <div className="h-5 w-5 text-congress-cyan-light">
                    <FiHome size="100%" />
                  </div>
                </div>
                <a
                  href="https://www.google.com/maps/search/?api=1&query=Campus+UNaB+Blas+Parera+132+Burzaco"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  {EVENT_LOCATION}
                </a>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>
      {/* Large Logo Carousel Section */}
      <section className="bg-gray-100 py-16 md:py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-8">
            Nuestras Empresas Participantes
          </h2>

          <LargeLogoCarousel edicionId={selectedEditionId} />
        </div>
      </section>
      {/* Benefits Section */}
      <section className="py-20 relative overflow-hidden bg-slate-50">
        <FloatingParticles count={15} color="rgba(37, 99, 235, 0.1)" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="mx-auto max-w-7xl">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
                Beneficios de Participar
              </h2>
              <div className="w-24 h-1.5 bg-congress-cyan mx-auto rounded-full"></div>
            </motion.div>

            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-10"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={staggerContainer}
            >
              {BENEFITS.map((benefit) => (
                <motion.div key={benefit.id} variants={fadeInUp} className="h-full">
                  <BenefitCard benefit={benefit} />
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Participation Modalities */}
      {/* <section className="py-16 bg-gray-50">
                  </ul>
                  </ul>
                  </ul>
      </section> */}

    </>
  );
}
