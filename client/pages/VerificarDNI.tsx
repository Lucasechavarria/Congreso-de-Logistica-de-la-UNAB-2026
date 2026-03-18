import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  CheckCircle,
  AlertCircle,
  Loader2,
  Shield,
  Building2,
  Mic2,
  Camera,
  Users,
  UserCheck,
  User,
} from "lucide-react";
import { API_HOST } from "@/lib/api";

// ─── Tipos ────────────────────────────────────────────────────────────────────
interface PantallaData {
  tipo:
    | "GENERAL"
    | "REPRESENTANTE_EMPRESA"
    | "DISERTANTE"
    | "PRENSA"
    | "REPRESENTANTE_GRUPO"
    | "MIEMBRO_GRUPO";
  subtitulo: string;
  nombre_vinculado: string;
}

interface AsistenteData {
  nombre_completo: string;
  email: string;
  dni: string;
  profile_type: string;
}

interface VerificacionResult {
  asistente: AsistenteData;
  pantalla: PantallaData;
  message: string;
}

// ─── Config de cada pantalla ──────────────────────────────────────────────────
const PANTALLA_CONFIG: Record<
  string,
  {
    titulo: string;
    icono: React.ReactNode;
    gradient: string;
    iconBg: string;
    badge: string;
    badgeBg: string;
  }
> = {
  GENERAL: {
    titulo: "¡Asistencia Confirmada!",
    icono: <CheckCircle className="w-16 h-16 text-white" />,
    gradient: "from-emerald-500 via-emerald-600 to-teal-700",
    iconBg: "bg-emerald-500/20",
    badge: "Asistente General",
    badgeBg: "bg-emerald-100 text-emerald-800",
  },
  REPRESENTANTE_EMPRESA: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Building2 className="w-16 h-16 text-white" />,
    gradient: "from-blue-500 via-blue-600 to-indigo-700",
    iconBg: "bg-blue-500/20",
    badge: "Representante de Empresa",
    badgeBg: "bg-blue-100 text-blue-800",
  },
  DISERTANTE: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Mic2 className="w-16 h-16 text-white" />,
    gradient: "from-violet-500 via-purple-600 to-purple-800",
    iconBg: "bg-violet-500/20",
    badge: "Disertante",
    badgeBg: "bg-violet-100 text-violet-800",
  },
  PRENSA: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Camera className="w-16 h-16 text-white" />,
    gradient: "from-amber-500 via-orange-500 to-rose-600",
    iconBg: "bg-amber-500/20",
    badge: "Prensa Acreditada",
    badgeBg: "bg-amber-100 text-amber-800",
  },
  REPRESENTANTE_GRUPO: {
    titulo: "¡Asistencia Confirmada!",
    icono: <UserCheck className="w-16 h-16 text-white" />,
    gradient: "from-cyan-500 via-sky-600 to-blue-700",
    iconBg: "bg-cyan-500/20",
    badge: "Representante de Grupo",
    badgeBg: "bg-cyan-100 text-cyan-800",
  },
  MIEMBRO_GRUPO: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Users className="w-16 h-16 text-white" />,
    gradient: "from-sky-400 via-cyan-500 to-teal-600",
    iconBg: "bg-sky-500/20",
    badge: "Miembro de Grupo",
    badgeBg: "bg-sky-100 text-sky-800",
  },
};

// ─── Pantalla de éxito ────────────────────────────────────────────────────────
function PantallaExito({ result }: { result: VerificacionResult }) {
  const tipo = result.pantalla.tipo;
  const cfg = PANTALLA_CONFIG[tipo] ?? PANTALLA_CONFIG["GENERAL"];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      {/* Orbes decorativos */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          className={`absolute top-1/4 -left-32 w-80 h-80 rounded-full bg-gradient-to-r ${cfg.gradient} opacity-10 blur-3xl orb-float`}
        />
        <div
          className={`absolute bottom-1/4 -right-32 w-96 h-96 rounded-full bg-gradient-to-l ${cfg.gradient} opacity-10 blur-3xl orb-float-delay`}
        />
      </div>

      <div className="relative w-full max-w-sm mx-auto animate-fade-in-up">
        {/* Card principal */}
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/20">
          {/* Header con gradiente */}
          <div
            className={`bg-gradient-to-br ${cfg.gradient} px-8 pt-10 pb-12 text-center relative`}
          >
            {/* Ícono animado */}
            <div
              className={`inline-flex items-center justify-center w-28 h-28 rounded-full ${cfg.iconBg} backdrop-blur-sm border-4 border-white/30 mb-4 animate-gentle-pulse`}
            >
              {cfg.icono}
            </div>

            {/* Título */}
            <h1 className="text-2xl font-bold text-white mb-1">
              {cfg.titulo}
            </h1>

            {/* Badge de tipo */}
            <span
              className={`inline-block mt-2 px-4 py-1 rounded-full text-sm font-semibold ${cfg.badgeBg} backdrop-blur-sm`}
            >
              {cfg.badge}
            </span>

            {/* Ola decorativa */}
            <div className="absolute bottom-0 left-0 right-0">
              <svg viewBox="0 0 400 24" fill="none" className="w-full">
                <path
                  d="M0 24 Q100 0 200 12 Q300 24 400 8 L400 24 Z"
                  fill="white"
                  fillOpacity="0.95"
                />
              </svg>
            </div>
          </div>

          {/* Contenido */}
          <div className="px-8 pb-8 pt-2">
            {/* Nombre del asistente */}
            <div className="text-center mb-6">
              <p className="text-2xl font-bold text-slate-800">
                {result.asistente.nombre_completo}
              </p>
              {result.pantalla.subtitulo && (
                <p className="mt-1 text-base font-medium text-slate-500">
                  {result.pantalla.subtitulo}
                </p>
              )}
            </div>

            {/* Separador */}
            <div className="border-t border-slate-100 my-4" />

            {/* Footer instrucción para colaborador */}
            <div className="bg-slate-50 rounded-2xl p-4 text-center border border-slate-200">
              <Shield className="w-5 h-5 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-600">
                Por favor, muestre esta pantalla
              </p>
              <p className="text-sm text-slate-500">
                al colaborador de ingreso
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Componente principal ─────────────────────────────────────────────────────
export default function VerificarDNI() {
  const navigate = useNavigate();
  const [dni, setDni] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<VerificacionResult | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (!dni.trim()) {
      setErrorMsg("Por favor ingresá tu DNI");
      return;
    }
    if (!/^\d{7,8}$/.test(dni.trim())) {
      setErrorMsg("DNI inválido. Debe tener 7 u 8 dígitos numéricos");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_HOST}/api/verificar-dni/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dni: dni.trim() }),
      });

      const data = await response.json();

      if (response.status === 404) {
        setShowModal(true);
        return;
      }
      if (response.status === 409) {
        setErrorMsg(data.message || "La asistencia ya fue confirmada.");
        return;
      }
      if (!response.ok) {
        throw new Error(data.message || "Error desconocido");
      }

      setResult(data as VerificacionResult);
    } catch (err) {
      setErrorMsg(
        err instanceof Error ? err.message : "No se pudo verificar el DNI."
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Pantalla de éxito ──
  if (result) {
    return <PantallaExito result={result} />;
  }

  // ── Formulario de ingreso de DNI ──
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-[#2d1854] to-slate-900 p-4">
      {/* Orbes */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 -left-40 w-96 h-96 rounded-full bg-violet-600/20 blur-3xl orb-float" />
        <div className="absolute bottom-1/3 -right-40 w-80 h-80 rounded-full bg-purple-500/20 blur-3xl orb-float-delay" />
      </div>

      <div className="relative w-full max-w-sm animate-fade-in-up">
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/20">
          {/* Header */}
          <div className="bg-gradient-to-br from-violet-600 via-purple-700 to-[#2d1854] px-8 pt-10 pb-12 text-center relative">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white/10 backdrop-blur-sm border-4 border-white/30 mb-4">
              <User className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">
              Confirmar Asistencia
            </h1>
            <p className="text-purple-200 text-sm mt-1">
              Congreso de Logística UNaB 2026
            </p>
            <div className="absolute bottom-0 left-0 right-0">
              <svg viewBox="0 0 400 24" fill="none" className="w-full">
                <path
                  d="M0 24 Q100 0 200 12 Q300 24 400 8 L400 24 Z"
                  fill="white"
                  fillOpacity="0.95"
                />
              </svg>
            </div>
          </div>

          {/* Form */}
          <div className="px-8 pb-8 pt-4">
            <p className="text-slate-500 text-sm text-center mb-6">
              Ingresá tu DNI (sin puntos ni espacios) para registrar tu ingreso
              al evento
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="dni"
                  className="block text-sm font-semibold text-slate-700 mb-1.5"
                >
                  Número de DNI
                </label>
                <input
                  id="dni"
                  type="tel"
                  inputMode="numeric"
                  placeholder="Ej: 12345678"
                  value={dni}
                  onChange={(e) =>
                    setDni(e.target.value.replace(/\D/g, "").slice(0, 8))
                  }
                  maxLength={8}
                  autoFocus
                  className="w-full px-4 py-3.5 text-lg text-center font-bold tracking-widest rounded-2xl border-2 border-slate-200 focus:border-violet-500 focus:ring-4 focus:ring-violet-100 outline-none transition-all duration-200 bg-slate-50 placeholder:font-normal placeholder:tracking-normal placeholder:text-slate-400"
                />
              </div>

              {errorMsg && (
                <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-xl p-3">
                  <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-red-700">{errorMsg}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-2xl text-white font-bold text-base bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-violet-500/25 flex items-center justify-center gap-2 btn-shimmer"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Verificando...
                  </>
                ) : (
                  "Confirmar mi Asistencia"
                )}
              </button>
            </form>

            {/* Aviso */}
            <div className="mt-6 flex items-start gap-2 text-xs text-slate-400">
              <Shield className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <p>
                Solo podés confirmar tu asistencia una vez. Asegurate de que
                tu registro ya esté completo.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Modal DNI no encontrado */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-xs w-full p-8 text-center animate-fade-in-up">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-100 mb-4">
              <AlertCircle className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="text-xl font-bold text-slate-800 mb-2">
              DNI no registrado
            </h2>
            <p className="text-slate-500 text-sm mb-6">
              No encontramos tu DNI. Primero completá tu inscripción para poder
              confirmar la asistencia.
            </p>
            <button
              onClick={() => {
                setShowModal(false);
                navigate("/seleccion-registro");
              }}
              className="w-full py-3 rounded-2xl text-white font-bold bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 transition-all duration-200 shadow-lg shadow-violet-500/25"
            >
              Ir a Registro
            </button>
            <button
              onClick={() => setShowModal(false)}
              className="w-full mt-3 py-2.5 rounded-2xl font-semibold text-slate-500 hover:bg-slate-100 transition-all duration-200 text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
