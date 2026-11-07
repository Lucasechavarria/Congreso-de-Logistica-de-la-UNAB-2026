import React from "react";

export default function PageLoader() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0f041e] text-white">
      {/* Barra superior de carga animada */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-white/5 overflow-hidden z-50">
        <div className="h-full w-full bg-gradient-to-r from-[#8b5cf6] via-[#c084fc] to-[#7c3aed] animate-pulse" />
      </div>

      {/* Orbe decorativo de fondo */}
      <div className="absolute w-72 h-72 bg-[#8b5cf6]/10 blur-[100px] rounded-full pointer-events-none transform-gpu" />

      {/* Spinner orbital y estética institucional */}
      <div className="relative flex flex-col items-center gap-4 z-10">
        <div className="relative w-14 h-14 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-2 border-[#8b5cf6]/20" />
          <div className="w-14 h-14 rounded-full border-2 border-transparent border-t-[#c084fc] border-r-[#8b5cf6] animate-spin" />
          <div className="w-2.5 h-2.5 rounded-full bg-gradient-to-tr from-[#8b5cf6] to-[#c084fc] animate-ping" />
        </div>

        <div className="text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-purple-200/90 font-['Plus_Jakarta_Sans',sans-serif]">
            Congreso UNAB 2026
          </p>
          <p className="text-[11px] text-purple-300/50 mt-1">
            Cargando experiencia...
          </p>
        </div>
      </div>
    </div>
  );
}

