import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Mail, Instagram, MapPin, Linkedin, MessageSquare } from "lucide-react";
import SafeContact from "@/components/SafeContact";
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

        {/* Grid de 4 tarjetas principales */}
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
              <CardContent className="flex justify-center">
                <SafeContact
                  type="email"
                  user="congresologisticaytransporte"
                  domain="unab.edu.ar"
                  className="text-lg text-white font-medium hover:underline"
                  label="congresologisticaytransporte@unab.edu.ar"
                />
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

        {/* WhatsApp Rectangular CTA - Con efecto de rellenado (Filling effect) */}
        <motion.div 
          className="mt-12 flex justify-center w-full max-w-4xl mx-auto px-4"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <div className="relative group w-full max-w-2xl overflow-hidden rounded-2xl shadow-xl transition-all duration-500 hover:shadow-green-500/30">
            {/* Fondo base */}
            <div className="absolute inset-0 bg-white transition-all duration-500 group-hover:bg-transparent border border-green-500/30 rounded-2xl" />
            
            {/* Efecto de rellenado (Filling effect) */}
            <div className="absolute inset-x-0 bottom-0 h-0 bg-gradient-to-t from-green-600 to-[#25D366] transition-all duration-500 ease-in-out group-hover:h-full" />
            
            <SafeContact
              type="whatsapp"
              phone="5491178270919"
              className="relative z-10 w-full flex items-center justify-center gap-4 py-8 px-8 text-xl md:text-2xl font-black uppercase tracking-widest transition-all duration-500 text-[#25D366] group-hover:text-white"
              icon={
                <svg 
                  viewBox="0 0 24 24" 
                  className="w-10 h-10 fill-current drop-shadow-lg" 
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.414 0 .018 5.393 0 12.03c0 2.123.542 4.197 1.57 6.05L0 24l6.117-1.605a11.845 11.845 0 005.928 1.583h.005c6.637 0 12.032-5.391 12.036-12.029a11.82 11.82 0 00-3.417-8.508z" />
                </svg>
              }
              label="Chateá con nosotros"
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
