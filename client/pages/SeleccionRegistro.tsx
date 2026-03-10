import { Card, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { Building2, ArrowRight, GraduationCap, Presentation, Users } from "lucide-react";
import FloatingParticles from "@/components/FloatingParticles";

export default function SeleccionRegistro() {
  return (
    <div className="flex-1 flex items-center justify-center px-4 py-8 min-h-[calc(100vh-200px)] bg-professional-gradient relative overflow-hidden">
      <FloatingParticles count={25} />
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-congress-cyan/20 to-transparent rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-congress-blue/20 to-transparent rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-2xl w-full relative z-10 animate-float-up">
        {/* Header elegante */}
        <div className="text-center mb-10 animate-fade-in-delay">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-congress-cyan to-congress-blue rounded-2xl mb-6 shadow-lg">
            <Users className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
            Únete al Congreso
          </h1>
          <p className="text-lg text-gray-600 max-w-md mx-auto leading-relaxed">
            Selecciona el tipo de registro que mejor se adapte a tu perfil profesional
          </p>
        </div>

        <div className="grid gap-6 md:gap-8 animate-fade-in-delay-2">
          {/* REGISTRO DE PARTICIPANTES / VISITANTE */}
          <Link to="/registro-participantes" className="group block">
            <Card className="selection-card form-glass border-0 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden bg-white/80">
              <CardContent className="p-8 relative z-10">
                <div className="flex items-center space-x-6">
                  <div className="flex-shrink-0">
                    <div className="icon-container-elegant w-16 h-16 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                      <GraduationCap className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-congress-blue transition-all duration-300">
                      Inscribite como Visitante
                    </h3>
                    <p className="text-gray-600 leading-relaxed text-sm md:text-base font-medium">
                      Para estudiantes, profesores y profesionales interesados en asistir a las charlas y networking.
                    </p>
                    <div className="flex items-center mt-3 text-xs text-congress-blue font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                      <span>Acceso a Auditorio</span>
                      <div className="w-1 h-1 bg-congress-blue rounded-full mx-2"></div>
                      <span>Certificado de Asistencia</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-congress-blue/10 transition-all duration-300">
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-congress-blue group-hover:translate-x-1 transition-all duration-300" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>

          {/* POSTULATE COMO DISERTANTE */}
          <Link to="/registro-disertante" className="group block">
            <Card className="selection-card form-glass border-0 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden bg-white/80">
              <CardContent className="p-8 relative z-10">
                <div className="flex items-center space-x-6">
                  <div className="flex-shrink-0">
                    <div className="icon-container-elegant w-16 h-16 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300 bg-gradient-to-br from-congress-blue to-congress-blue-dark">
                      <Presentation className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-congress-blue transition-all duration-300">
                      Postulate como Disertante
                    </h3>
                    <p className="text-gray-600 leading-relaxed text-sm md:text-base font-medium">
                      ¿Quieres compartir tus conocimientos? Presenta tu propuesta para disertar en el congreso.
                    </p>
                    <div className="flex items-center mt-3 text-xs text-congress-blue font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                      <span>Espacio de Charla</span>
                      <div className="w-1 h-1 bg-congress-blue rounded-full mx-2"></div>
                      <span>Reconocimiento Académico</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-congress-blue/10 transition-all duration-300">
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-congress-blue group-hover:translate-x-1 transition-all duration-300" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>

          {/* POSTULATE COMO EXPOSITOR */}
          <Link to="/registro-empresas" className="group block">
            <Card className="selection-card form-glass border-0 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden bg-white/80">
              <CardContent className="p-8 relative z-10">
                <div className="flex items-center space-x-6">
                  <div className="flex-shrink-0">
                    <div className="icon-container-elegant w-16 h-16 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300 bg-gradient-to-br from-congress-cyan to-congress-blue">
                      <Building2 className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-congress-blue transition-all duration-300">
                      Postulate como Expositor
                    </h3>
                    <p className="text-gray-600 leading-relaxed text-sm md:text-base font-medium">
                      Para empresas que deseen contar con un stand y visibilidad en el sector industrial.
                    </p>
                    <div className="flex items-center mt-3 text-xs text-congress-blue font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                      <span>Stand Exclusivo</span>
                      <div className="w-1 h-1 bg-congress-blue rounded-full mx-2"></div>
                      <span>Networking B2B</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-congress-blue/10 transition-all duration-300">
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-congress-blue group-hover:translate-x-1 transition-all duration-300" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Footer informativo elegante */}
        <div className="text-center mt-12 mb-8 animate-fade-in-up">
          <p className="text-congress-blue font-bold text-lg mb-4">
            🚀 Todas las modalidades de participación son sin costo.
          </p>
          <p className="text-slate-500 text-sm">
            Universidad Nacional Guillermo Brown - 2026
          </p>
        </div>
      </div>
    </div>
  );
}
