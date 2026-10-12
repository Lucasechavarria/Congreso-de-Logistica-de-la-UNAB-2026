import React from "react";
import { Building2, Presentation, CheckCircle2 } from "lucide-react";

interface ConvocatoriaStatusBannerProps {
  tipo: "disertante" | "empresa";
  className?: string;
}

export const ConvocatoriaStatusBanner: React.FC<ConvocatoriaStatusBannerProps> = ({
  tipo,
  className = "",
}) => {
  const isEmpresa = tipo === "empresa";

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-br from-amber-500/10 via-slate-900/5 to-purple-500/10 backdrop-blur-md p-5 sm:p-6 shadow-lg transition-all duration-300 hover:border-amber-500/40 hover:shadow-xl ${className}`}
    >
      {/* Decorative background glow */}
      <div className="pointer-events-none absolute -right-16 -top-16 h-36 w-36 rounded-full bg-amber-400/15 blur-2xl" />
      <div className="pointer-events-none absolute -left-16 -bottom-16 h-36 w-36 rounded-full bg-purple-500/15 blur-2xl" />

      <div className="relative z-10 flex flex-col gap-4 text-center">
        {/* Header with pill badge centered */}
        <div className="flex items-center justify-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-800 tracking-wide uppercase">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-500 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-600" />
            </span>
            Convocatoria 2026 Cerrada
          </div>
        </div>

        {/* Title & Introduction centered */}
        <div className="text-center">
          <h3 className="text-lg sm:text-xl font-bold text-slate-900 flex items-center justify-center gap-2">
            {isEmpresa ? (
              <Building2 className="h-5 w-5 text-amber-600 flex-shrink-0" />
            ) : (
              <Presentation className="h-5 w-5 text-amber-600 flex-shrink-0" />
            )}
            <span>
              {isEmpresa
                ? "Postulaciones para el Congreso 2026 Cerradas"
                : "Convocatoria de Disertantes 2026 Cerrada"}
            </span>
          </h3>
          <p className="mt-1.5 text-sm text-slate-700 leading-relaxed max-w-xl mx-auto">
            {isEmpresa
              ? "Las postulaciones regulares de stands y participación empresarial para el actual congreso están cerradas. Sin embargo, mantenemos el formulario habilitado para registrarse de cara al próximo año."
              : "Las postulaciones oficiales de ponencias para el actual congreso están cerradas. Sin embargo, mantenemos el formulario habilitado para registrarse de cara al próximo año."}
          </p>
        </div>

        {/* Single improved, crystal-clear card centered */}
        <div className="rounded-xl border border-congress-blue/20 bg-white/85 p-5 shadow-sm transition-all hover:bg-white/95 text-center">
          <div className="flex flex-col items-center">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-congress-blue/10 text-congress-blue mb-2.5 shadow-sm">
              <CheckCircle2 className="h-5 w-5" />
            </div>
            <h4 className="text-sm sm:text-base font-bold text-slate-900">
              {isEmpresa
                ? "Inscripción para la Próxima Edición (2027)"
                : "Postulación para la Próxima Edición (2027)"}
            </h4>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-600 leading-relaxed max-w-lg mx-auto">
              {isEmpresa
                ? "Tu empresa quedará registrada para participar en el Congreso 2027. El comité organizador evaluará las propuestas recibidas de cara a la organización del próximo año."
                : "Tu propuesta quedará registrada para participar en el Congreso 2027. La comisión académica evaluará las postulaciones recibidas de cara a la organización del próximo año."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConvocatoriaStatusBanner;
