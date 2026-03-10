import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Mail, Instagram, MapPin, Linkedin } from "lucide-react";
import FloatingParticles from "@/components/FloatingParticles";
import { motion } from "framer-motion";

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

export default function Contacto() {
  return (
    <div className="relative overflow-hidden min-h-screen bg-slate-50">
      <FloatingParticles count={20} color="rgba(59, 130, 246, 0.2)" />

      <div className="container mx-auto px-4 py-16 relative z-10">
        <motion.div
          className="text-center mb-12"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
        >
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
            Información de Contacto
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Estamos aquí para ayudarte. No dudes en contactarnos para cualquier
            consulta o información adicional.
          </p>
        </motion.div>

        <motion.div
          className="text-center mb-12"
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-6 font-display">
            ¿Tienes alguna pregunta?
          </h2>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            Si necesitas asistencia inmediata o tienes consultas específicas,
            por favor, envíanos un correo directamente.
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          {/* Correo Electrónico */}
          <motion.div variants={fadeInUp}>
            <Card className="group border-0 shadow-xl hover:shadow-2xl rounded-2xl bg-gradient-to-br from-congress-blue/90 to-congress-cyan/80 p-6 transition-all duration-300 transform hover:scale-105 text-center h-full">
              <CardHeader className="flex flex-col items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-congress-blue to-congress-blue-dark rounded-full flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 icon-float">
                  <Mail className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-white group-hover:text-congress-cyan transition-colors">
                  Correo Electrónico
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="mailto:congresologisticaytransporte@unab.edu.ar"
                  className="text-lg text-white font-medium leading-relaxed hover:underline break-words"
                >
                  congresologisticaytransporte@unab.edu.ar
                </a>
              </CardContent>
            </Card>
          </motion.div>

          {/* Instagram */}
          <motion.div variants={fadeInUp}>
            <Card className="group border-0 shadow-xl hover:shadow-2xl rounded-2xl bg-gradient-to-br from-congress-cyan/90 to-congress-blue/80 p-6 transition-all duration-300 transform hover:scale-105 text-center h-full">
              <CardHeader className="flex flex-col items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-congress-cyan to-congress-cyan-light rounded-full flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 icon-float">
                  <Instagram className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-white group-hover:text-congress-blue transition-colors">
                  Instagram
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="https://www.instagram.com/congresologisticounab/"
                  className="text-lg text-white font-medium leading-relaxed hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  @congresologisticounab
                </a>
              </CardContent>
            </Card>
          </motion.div>

          {/* Ubicación */}
          <motion.div variants={fadeInUp}>
            <Card className="group border-0 shadow-xl hover:shadow-2xl rounded-2xl bg-gradient-to-br from-congress-blue/90 to-congress-cyan/80 p-6 transition-all duration-300 transform hover:scale-105 text-center h-full">
              <CardHeader className="flex flex-col items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-congress-blue to-congress-blue-dark rounded-full flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 icon-float">
                  <MapPin className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-white group-hover:text-congress-cyan transition-colors">
                  Ubicación
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="/#mapa"
                  className="text-lg text-white font-medium leading-relaxed hover:underline"
                >
                  Universidad Nacional Guillermo Brown
                  <br />
                  Blas Parera 132, Burzaco
                </a>
              </CardContent>
            </Card>
          </motion.div>

          {/* LinkedIn */}
          <motion.div variants={fadeInUp}>
            <Card className="group border-0 shadow-xl hover:shadow-2xl rounded-2xl bg-gradient-to-br from-congress-cyan/90 to-congress-blue/80 p-6 transition-all duration-300 transform hover:scale-105 text-center h-full">
              <CardHeader className="flex flex-col items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-congress-cyan to-congress-cyan-light rounded-full flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl transition-all duration-300 icon-float">
                  <Linkedin className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-white group-hover:text-congress-blue transition-colors">
                  LinkedIn
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="https://www.linkedin.com/company/congresologisticounab/"
                  className="text-lg text-white font-medium leading-relaxed hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  @congresologisticounab
                </a>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
