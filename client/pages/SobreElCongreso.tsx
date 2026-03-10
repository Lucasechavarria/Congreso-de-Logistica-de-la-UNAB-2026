import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FiUsers, FiClock, FiAward } from "react-icons/fi";
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

export default function SobreElCongreso() {
  return (
    <section className="py-20 bg-slate-50 relative overflow-hidden">
      <FloatingParticles count={20} color="rgba(37, 99, 235, 0.1)" />
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          className="max-w-4xl mx-auto text-center mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <h2 className="text-4xl md:text-5xl font-extrabold text-congress-blue mb-6 tracking-tight">
            Sobre el Congreso
          </h2>
          <div className="w-24 h-1.5 bg-congress-cyan mx-auto mb-8 rounded-full"></div>
          <p className="text-xl text-gray-700 leading-relaxed font-medium">
            El Congreso de Logística y Transporte 2026 de la Universidad
            Nacional Guillermo Brown es un evento académico de alcance
            nacional e internacional que reúne a líderes del sector
            y especialistas de primer nivel. Nuestro objetivo es crear
            un espacio de reflexión y debate sobre los principales desafíos y
            oportunidades en la logística y el transporte.
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.div variants={fadeInUp}>
            <Card className="h-full border-0 shadow-xl rounded-2xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              <CardHeader className="text-center pb-2">
                <div className="w-16 h-16 bg-congress-blue/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-congress-blue group-hover:bg-congress-blue group-hover:text-white transition-colors duration-300">
                  <FiUsers className="w-8 h-8" />
                </div>
                <CardTitle className="text-xl font-bold text-congress-blue">Networking</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-base text-gray-600">
                  Conecta con profesionales, académicos y líderes de la
                  industria logística y de transporte.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={fadeInUp}>
            <Card className="h-full border-0 shadow-xl rounded-2xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              <CardHeader className="text-center pb-2">
                <div className="w-16 h-16 bg-congress-cyan/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-congress-cyan">
                  <FiClock className="w-8 h-8" />
                </div>
                <CardTitle className="text-xl font-bold text-congress-blue">Innovación</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-base text-gray-600">
                  Descubre las últimas tecnologías y metodologías que están
                  transformando el sector.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={fadeInUp}>
            <Card className="h-full border-0 shadow-xl rounded-2xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              <CardHeader className="text-center pb-2">
                <div className="w-16 h-16 bg-congress-blue/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-congress-blue">
                  <FiAward className="w-8 h-8" />
                </div>
                <CardTitle className="text-xl font-bold text-congress-blue">Excelencia</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-base text-gray-600">
                  Participa en conferencias magistrales y talleres dirigidos por
                  expertos reconocidos.
                </CardDescription>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        {/* Moviendo el futuro Section */}
        <motion.div
          className="bg-gradient-to-br from-congress-blue to-congress-blue-dark rounded-3xl shadow-2xl p-8 md:p-16 text-white relative overflow-hidden"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <FloatingParticles count={10} color="rgba(255, 255, 255, 0.1)" />
          <div className="relative z-10">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-5xl font-extrabold mb-6 tracking-tight">
                Moviendo el futuro
              </h2>
              <p className="text-lg md:text-xl opacity-90 max-w-3xl mx-auto leading-relaxed">
                Este congreso reunirá a los principales actores del sector
                logístico y de transporte para reflexionar y debatir sobre los
                desafíos y oportunidades.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl w-24 h-24 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <span className="text-3xl font-extrabold text-congress-cyan">+50</span>
                </div>
                <h3 className="text-xl font-bold mb-1">Empresas</h3>
                <p className="text-sm opacity-80">Líderes participantes</p>
              </div>

              <div className="text-center">
                <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl w-24 h-24 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <span className="text-3xl font-extrabold text-congress-cyan">+25</span>
                </div>
                <h3 className="text-xl font-bold mb-1">Disertantes</h3>
                <p className="text-sm opacity-80">Expertos de nivel</p>
              </div>

              <div className="text-center">
                <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl w-24 h-24 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <span className="text-3xl font-extrabold text-congress-cyan">2</span>
                </div>
                <h3 className="text-xl font-bold mb-1">Alcances</h3>
                <p className="text-sm opacity-80">Nac. e Internacional</p>
              </div>

              <div className="text-center">
                <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl w-24 h-24 flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <span className="text-3xl font-extrabold text-congress-cyan">0</span>
                </div>
                <h3 className="text-xl font-bold mb-1">Costo</h3>
                <p className="text-sm opacity-80">Inscripción libre</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
