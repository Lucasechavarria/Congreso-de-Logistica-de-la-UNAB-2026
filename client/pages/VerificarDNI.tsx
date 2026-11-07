import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  CheckCircle,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Shield,
  Building2,
  Mic2,
  Camera,
  Users,
  UserCheck,
  User,
  Edit2,
  ArrowLeft,
  Check,
  RefreshCw,
  Clock,
  Calendar,
  Zap,
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

interface AlreadyAccreditedData {
  message: string;
  hora_acreditacion: string;
  fecha_acreditacion: string;
  asistente: AsistenteData;
  pantalla: PantallaData;
}

interface AsistenteDetails {
  id: number;
  first_name: string;
  last_name: string;
  nombre_completo?: string;
  email: string;
  phone: string;
  dni: string;
  profile_type: string;
  institution: string;
  career: string;
  is_provisional_phone?: boolean;
  is_provisional_email?: boolean;
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
    gradient: "from-purple-600 via-purple-700 to-[#2d1854]",
    iconBg: "bg-purple-500/20",
    badge: "Asistente General",
    badgeBg: "bg-purple-900/30 text-purple-200 border border-purple-500/30",
  },
  REPRESENTANTE_EMPRESA: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Building2 className="w-16 h-16 text-white" />,
    gradient: "from-blue-600 via-indigo-700 to-[#2d1854]",
    iconBg: "bg-blue-500/20",
    badge: "Representante de Empresa",
    badgeBg: "bg-blue-900/30 text-blue-200 border border-blue-500/30",
  },
  DISERTANTE: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Mic2 className="w-16 h-16 text-white" />,
    gradient: "from-amber-500 via-orange-600 to-[#2d1854]",
    iconBg: "bg-amber-500/20",
    badge: "Disertante",
    badgeBg: "bg-amber-950/40 text-amber-200 border border-amber-400/40",
  },
  PRENSA: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Camera className="w-16 h-16 text-white" />,
    gradient: "from-pink-600 via-rose-700 to-[#2d1854]",
    iconBg: "bg-pink-500/20",
    badge: "Prensa Acreditada",
    badgeBg: "bg-pink-900/30 text-pink-200 border border-pink-500/30",
  },
  REPRESENTANTE_GRUPO: {
    titulo: "¡Asistencia Confirmada!",
    icono: <UserCheck className="w-16 h-16 text-white" />,
    gradient: "from-cyan-600 via-sky-700 to-[#2d1854]",
    iconBg: "bg-cyan-500/20",
    badge: "Representante de Grupo",
    badgeBg: "bg-cyan-900/30 text-cyan-200 border border-cyan-500/30",
  },
  MIEMBRO_GRUPO: {
    titulo: "¡Asistencia Confirmada!",
    icono: <Users className="w-16 h-16 text-white" />,
    gradient: "from-teal-600 via-cyan-700 to-[#2d1854]",
    iconBg: "bg-teal-500/20",
    badge: "Miembro de Grupo",
    badgeBg: "bg-teal-900/30 text-teal-200 border border-teal-500/30",
  },
};

// Helper con timeout seguro para entornos móviles y redes inestables
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs: number = 8000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (error: any) {
    if (error.name === "AbortError") {
      throw new Error("La solicitud demoró más de 8 segundos. Verificá tu señal de internet y volvé a intentar.");
    }
    throw error;
  } finally {
    clearTimeout(id);
  }
}

// ─── Pantalla de éxito ────────────────────────────────────────────────────────
function PantallaExito({
  result,
  onReset,
}: {
  result: VerificacionResult;
  onReset: () => void;
}) {
  const navigate = useNavigate();
  const tipo = result.pantalla.tipo;
  const cfg = PANTALLA_CONFIG[tipo] ?? PANTALLA_CONFIG["GENERAL"];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#2d1854] to-slate-950 p-4">
      {/* Orbes decorativos */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 -left-32 w-80 h-80 rounded-full bg-violet-600/10 blur-3xl orb-float" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full bg-purple-500/10 blur-3xl orb-float-delay" />
      </div>

      <div className="relative w-full max-w-md mx-auto animate-fade-in-up">
        {/* Card principal Glassmorphism */}
        <div className="bg-[#2d1854]/45 backdrop-blur-xl rounded-3xl shadow-3xl overflow-hidden border border-white/10 text-white">
          {/* Header con gradiente */}
          <div className={`bg-gradient-to-br ${cfg.gradient} px-8 pt-10 pb-12 text-center relative`}>
            {/* Ícono animado */}
            <div className={`inline-flex items-center justify-center w-28 h-28 rounded-full ${cfg.iconBg} backdrop-blur-sm border-4 border-white/20 mb-4 animate-gentle-pulse shadow-[0_0_20px_rgba(167,139,250,0.3)]`}>
              {cfg.icono}
            </div>

            {/* Título */}
            <h1 className="text-3xl font-extrabold text-white tracking-tight text-glow">
              {cfg.titulo}
            </h1>

            {/* Badge de tipo */}
            <span className={`inline-block mt-3 px-4 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase ${cfg.badgeBg}`}>
              {cfg.badge}
            </span>

            {/* Ola decorativa */}
            <div className="absolute bottom-0 left-0 right-0">
              <svg viewBox="0 0 400 24" fill="none" className="w-full">
                <path
                  d="M0 24 Q100 0 200 12 Q300 24 400 8 L400 24 Z"
                  fill="#2d1854"
                  fillOpacity="0.45"
                />
              </svg>
            </div>
          </div>

          {/* Contenido */}
          <div className="px-8 pb-8 pt-6">
            {/* Nombre del asistente */}
            <div className="text-center mb-6">
              <p className="text-3xl font-extrabold text-white tracking-tight">
                {result.asistente.nombre_completo}
              </p>
              {result.pantalla.subtitulo && (
                <p className="mt-2 text-base font-semibold text-purple-200">
                  {result.pantalla.subtitulo}
                </p>
              )}
            </div>

            {/* Separador */}
            <div className="border-t border-white/10 my-6" />

            {/* Footer instrucción para colaborador */}
            <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl p-4 text-center border border-white/5 space-y-1 mb-6">
              <Shield className="w-6 h-6 text-purple-400 mx-auto mb-1" />
              <p className="text-sm font-semibold text-purple-100">
                ¡Acreditación exitosa!
              </p>
              <p className="text-xs text-purple-300/90 leading-relaxed">
                Ya podés ingresar a las salas del congreso.
              </p>
              <p className="text-xs text-emerald-300 font-medium bg-emerald-500/10 border border-emerald-500/20 rounded-xl py-1 px-2 mt-2">
                ✉️ Tu certificado oficial de asistencia será emitido y enviado a tu correo al finalizar la jornada.
              </p>
            </div>
            
            {/* Botones de navegación requeridos */}
            <div className="flex flex-col gap-3">
              <button
                onClick={() => navigate("/programa")}
                className="w-full py-4 rounded-2xl text-white font-extrabold text-sm bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2 border border-white/10 btn-shimmer"
              >
                <Calendar className="w-4 h-4" />
                Ver Programa del Congreso
              </button>

              <button
                onClick={() => navigate("/")}
                className="w-full py-3.5 rounded-2xl font-bold bg-white/10 hover:bg-white/20 active:scale-[0.98] transition-all duration-200 text-sm border border-white/10 flex items-center justify-center gap-2 text-purple-100"
              >
                🏁 Finalizar
              </button>

              <button
                onClick={onReset}
                className="w-full py-2.5 rounded-2xl text-xs font-semibold text-purple-300/80 hover:text-white transition-all duration-200 flex items-center justify-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Acreditar otro asistente
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Pantalla Ya Acreditado (Caso 2 - HTTP 409) ────────────────────────────────
function PantallaYaAcreditado({
  data,
  onReset,
}: {
  data: AlreadyAccreditedData;
  onReset: () => void;
}) {
  const navigate = useNavigate();
  const tipo = data.pantalla?.tipo ?? "GENERAL";
  const cfg = PANTALLA_CONFIG[tipo] ?? PANTALLA_CONFIG["GENERAL"];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#2d1854] to-slate-950 p-4">
      {/* Orbes decorativos */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 -left-32 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl orb-float" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full bg-purple-500/10 blur-3xl orb-float-delay" />
      </div>

      <div className="relative w-full max-w-md mx-auto animate-fade-in-up">
        {/* Card principal Glassmorphism */}
        <div className="bg-[#2d1854]/45 backdrop-blur-xl rounded-3xl shadow-3xl overflow-hidden border border-amber-500/20 text-white">
          {/* Header con gradiente ámbar/púrpura */}
          <div className="bg-gradient-to-br from-amber-600 via-purple-700 to-[#2d1854] px-8 pt-10 pb-12 text-center relative">
            {/* Ícono animado */}
            <div className="inline-flex items-center justify-center w-28 h-28 rounded-full bg-amber-500/20 backdrop-blur-sm border-4 border-amber-400/30 mb-4 animate-gentle-pulse shadow-[0_0_25px_rgba(245,158,11,0.3)]">
              <Clock className="w-16 h-16 text-amber-300" />
            </div>

            {/* Título */}
            <h1 className="text-3xl font-extrabold text-white tracking-tight text-glow">
              🕒 ¡Ya te encontrás acreditado!
            </h1>

            {/* Badge de tipo */}
            <span className={`inline-block mt-3 px-4 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase ${cfg.badgeBg}`}>
              {cfg.badge}
            </span>

            {/* Ola decorativa */}
            <div className="absolute bottom-0 left-0 right-0">
              <svg viewBox="0 0 400 24" fill="none" className="w-full">
                <path
                  d="M0 24 Q100 0 200 12 Q300 24 400 8 L400 24 Z"
                  fill="#2d1854"
                  fillOpacity="0.45"
                />
              </svg>
            </div>
          </div>

          {/* Contenido */}
          <div className="px-8 pb-8 pt-6">
            {/* Nombre del asistente */}
            <div className="text-center mb-6">
              <p className="text-2xl font-extrabold text-white tracking-tight">
                {data.asistente.nombre_completo}
              </p>
              {data.pantalla.subtitulo && (
                <p className="mt-1 text-sm font-semibold text-purple-200">
                  {data.pantalla.subtitulo}
                </p>
              )}
              <p className="text-xs text-purple-300/70 mt-1">
                DNI: {data.asistente.dni}
              </p>
            </div>

            {/* Badge destacado de confirmación con hora */}
            <div className="bg-gradient-to-r from-amber-500/15 to-purple-500/15 border border-amber-500/30 rounded-2xl p-4 text-center mb-6 shadow-[0_0_20px_rgba(245,158,11,0.1)]">
              <div className="flex items-center justify-center gap-2 text-amber-300 font-extrabold text-base mb-1">
                <CheckCircle2 className="w-5 h-5 text-amber-400" />
                <span>Asistencia confirmada</span>
              </div>
              <p className="text-sm text-purple-100 font-medium">
                {data.hora_acreditacion
                  ? `Confirmaste tu asistencia hoy a las ${data.hora_acreditacion}`
                  : data.message}
              </p>
              {data.fecha_acreditacion && (
                <span className="inline-block mt-2 text-[11px] font-semibold text-amber-200/80 bg-black/20 px-3 py-1 rounded-full border border-amber-500/20">
                  Fecha: {data.fecha_acreditacion}
                </span>
              )}
            </div>

            {/* Aviso de credencial y certificado */}
            <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl p-4 text-center border border-white/5 space-y-1 mb-6">
              <p className="text-xs text-purple-200/90 leading-relaxed">
                Tu credencial digital ya está habilitada para todas las salas del congreso.
              </p>
              <p className="text-xs text-emerald-300 font-medium bg-emerald-500/10 border border-emerald-500/20 rounded-xl py-1 px-2 mt-2">
                ✉️ Tu certificado oficial será enviado por correo al cierre de la jornada.
              </p>
            </div>

            {/* Botones requeridos por el usuario */}
            <div className="flex flex-col gap-3">
              <button
                onClick={() => navigate("/programa")}
                className="w-full py-4 rounded-2xl text-white font-extrabold text-sm bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2 border border-white/10 btn-shimmer"
              >
                <Calendar className="w-4 h-4" />
                Ver Programa del Congreso
              </button>

              <button
                onClick={() => navigate("/")}
                className="w-full py-3.5 rounded-2xl font-bold bg-white/10 hover:bg-white/20 active:scale-[0.98] transition-all duration-200 text-sm border border-white/10 flex items-center justify-center gap-2 text-purple-100"
              >
                🏁 Finalizar
              </button>

              <button
                onClick={onReset}
                className="w-full py-2.5 rounded-2xl text-xs font-semibold text-purple-300/80 hover:text-white transition-all duration-200 flex items-center justify-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Verificar otro DNI
              </button>
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
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState<"input_dni" | "verify_details" | "edit_details" | "success" | "already_accredited">("input_dni");
  const [dni, setDni] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showRejectedModal, setShowRejectedModal] = useState<boolean>(false);
  const [rejectedMsg, setRejectedMsg] = useState<string>("");

  // Precargar DNI si viene en los query params (ej: /verificar-dni?dni=12345678)
  useEffect(() => {
    const paramDni = searchParams.get("dni");
    if (paramDni) {
      const cleanParam = paramDni.replace(/\D/g, "").slice(0, 8);
      if (cleanParam) {
        setDni(cleanParam);
      }
    }
  }, [searchParams]);
  
  // Datos del asistente para verificar/editar
  const [asistenteDetails, setAsistenteDetails] = useState<AsistenteDetails | null>(null);
  const [editFields, setEditFields] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    institution: "",
    career: "",
  });

  const [result, setResult] = useState<VerificacionResult | null>(null);
  const [alreadyAccreditedData, setAlreadyAccreditedData] = useState<AlreadyAccreditedData | null>(null);

  // Validar si el teléfono es provisional/genérico
  const isPhoneGeneric = asistenteDetails 
    ? Boolean(asistenteDetails.is_provisional_phone ?? (asistenteDetails.phone === "1111111111" || !asistenteDetails.phone.trim()))
    : false;

  // Validar si el correo es provisional/genérico
  const isEmailProvisional = asistenteDetails
    ? Boolean(
        asistenteDetails.is_provisional_email ??
        (!asistenteDetails.email ||
          !asistenteDetails.email.includes("@") ||
          asistenteDetails.email.includes(".temp") ||
          asistenteDetails.email.includes("@empresa.temp") ||
          asistenteDetails.email.includes("@unab.temp"))
      )
    : false;

  const hasProvisionalData = isPhoneGeneric || isEmailProvisional;

  const handleReset = () => {
    setStep("input_dni");
    setDni("");
    setErrorMsg("");
    setAsistenteDetails(null);
    setResult(null);
    setAlreadyAccreditedData(null);
    setShowModal(false);
    setShowRejectedModal(false);
    setRejectedMsg("");
  };

  const handleAlreadyAccreditedResponse = (data: any) => {
    setAlreadyAccreditedData({
      message: data.message || "La asistencia ya fue confirmada.",
      hora_acreditacion: data.hora_acreditacion || "",
      fecha_acreditacion: data.fecha_acreditacion || "",
      asistente: data.asistente || {
        nombre_completo: "Asistente",
        dni: dni.trim(),
        email: "",
        profile_type: "VISITOR",
      },
      pantalla: data.pantalla || {
        tipo: "GENERAL",
        subtitulo: "",
        nombre_vinculado: "",
      },
    });
    setStep("already_accredited");
  };

  // Paso 1: Buscar DNI en modo check_only
  const handleCheckDni = async (e: React.FormEvent) => {
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
      const response = await fetchWithTimeout(`${API_HOST}/api/verificar-dni/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dni: dni.trim(), check_only: true }),
      });

      const data = await response.json();

      if (response.status === 404) {
        setShowModal(true);
        return;
      }
      if (response.status === 409 || data.code === "ALREADY_ACCREDITED") {
        handleAlreadyAccreditedResponse(data);
        return;
      }
      if (response.status === 403 && data.code === "REGISTRATION_REJECTED") {
        setRejectedMsg(data.message || "Tu registro figura con estado rechazado. Por favor, consultá en la mesa de recepción.");
        setShowRejectedModal(true);
        return;
      }
      if (!response.ok) {
        throw new Error(data.message || "Error desconocido al verificar DNI.");
      }

      if (data.status === "pending_confirmation") {
        setAsistenteDetails(data.asistente);
        setEditFields({
          first_name: data.asistente.first_name,
          last_name: data.asistente.last_name,
          email: data.asistente.email,
          phone: data.asistente.phone,
          institution: data.asistente.institution,
          career: data.asistente.career,
        });
        setStep("verify_details");
      }
    } catch (err) {
      setErrorMsg(
        err instanceof Error ? err.message : "No se pudo verificar el DNI."
      );
    } finally {
      setLoading(false);
    }
  };

  // Paso 2: Confirmar datos directamente sin cambios
  const handleConfirmDirect = async () => {
    if (hasProvisionalData) {
      setErrorMsg("Por favor, modificá tus datos e ingresá información de contacto real.");
      return;
    }

    setErrorMsg("");
    setLoading(true);
    try {
      const response = await fetchWithTimeout(`${API_HOST}/api/verificar-dni/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dni: dni.trim(), confirmar: true }),
      });

      const data = await response.json();

      if (response.status === 409 || data.code === "ALREADY_ACCREDITED") {
        handleAlreadyAccreditedResponse(data);
        return;
      }
      if (response.status === 403 && data.code === "REGISTRATION_REJECTED") {
        setRejectedMsg(data.message || "Tu registro figura con estado rechazado. Por favor, consultá en la mesa de recepción.");
        setShowRejectedModal(true);
        return;
      }
      if (!response.ok) {
        throw new Error(data.message || "Error desconocido al confirmar asistencia.");
      }

      setResult(data as VerificacionResult);
      setStep("success");
    } catch (err) {
      setErrorMsg(
        err instanceof Error ? err.message : "No se pudo confirmar la asistencia."
      );
    } finally {
      setLoading(false);
    }
  };

  // Paso 3: Confirmar datos con actualización
  const handleConfirmWithEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (!editFields.first_name.trim()) {
      setErrorMsg("El nombre no puede estar vacío");
      return;
    }
    if (!editFields.last_name.trim()) {
      setErrorMsg("El apellido no puede estar vacío");
      return;
    }
    if (!editFields.email.trim() || editFields.email.toLowerCase().includes(".temp") || !/^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/.test(editFields.email.trim())) {
      setErrorMsg("Por favor, ingresá un correo electrónico válido y no provisorio para recibir tu certificado.");
      return;
    }
    if (!editFields.phone.trim() || editFields.phone.trim() === "1111111111") {
      setErrorMsg("Por favor, ingresá un número de teléfono real. El teléfono provisorio no es válido.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetchWithTimeout(`${API_HOST}/api/verificar-dni/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dni: dni.trim(),
          confirmar: true,
          first_name: editFields.first_name.trim(),
          last_name: editFields.last_name.trim(),
          email: editFields.email.trim(),
          phone: editFields.phone.trim(),
          institution: editFields.institution.trim(),
          career: editFields.career.trim(),
        }),
      });

      const data = await response.json();

      if (response.status === 409 || data.code === "ALREADY_ACCREDITED") {
        handleAlreadyAccreditedResponse(data);
        return;
      }
      if (response.status === 403 && data.code === "REGISTRATION_REJECTED") {
        setRejectedMsg(data.message || "Tu registro figura con estado rechazado. Por favor, consultá en la mesa de recepción.");
        setShowRejectedModal(true);
        return;
      }
      if (!response.ok) {
        throw new Error(data.message || "Error al actualizar y confirmar.");
      }

      setResult(data as VerificacionResult);
      setStep("success");
    } catch (err) {
      setErrorMsg(
        err instanceof Error ? err.message : "No se pudo actualizar y confirmar."
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Pantalla de éxito ──
  if (step === "success" && result) {
    return <PantallaExito result={result} onReset={handleReset} />;
  }

  // ── Pantalla Ya Acreditado (Caso 2 - 409) ──
  if (step === "already_accredited" && alreadyAccreditedData) {
    return <PantallaYaAcreditado data={alreadyAccreditedData} onReset={handleReset} />;
  }

  // ── Formulario de ingreso de DNI ──
  if (step === "input_dni") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#2d1854] to-slate-950 p-4">
        {/* Orbes decorativos */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/3 -left-40 w-96 h-96 rounded-full bg-violet-600/10 blur-3xl orb-float" />
          <div className="absolute bottom-1/3 -right-40 w-80 h-80 rounded-full bg-purple-500/10 blur-3xl orb-float-delay" />
        </div>

        <div className="relative w-full max-w-md animate-fade-in-up">
          <div className="bg-[#2d1854]/45 backdrop-blur-xl rounded-3xl shadow-3xl overflow-hidden border border-white/10 text-white">
            {/* Header */}
            <div className="bg-gradient-to-br from-violet-600 via-purple-700 to-[#2d1854] px-8 pt-10 pb-12 text-center relative">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white/10 backdrop-blur-sm border-4 border-white/20 mb-4 shadow-[0_0_15px_rgba(167,139,250,0.2)]">
                <User className="w-12 h-12 text-white" />
              </div>
              <h1 className="text-3xl font-extrabold text-white text-glow">
                Confirmar Asistencia
              </h1>
              <p className="text-purple-200 text-sm mt-2 font-medium">
                Congreso de Logística UNaB 2026
              </p>
              <div className="absolute bottom-0 left-0 right-0">
                <svg viewBox="0 0 400 24" fill="none" className="w-full">
                  <path
                    d="M0 24 Q100 0 200 12 Q300 24 400 8 L400 24 Z"
                    fill="#2d1854"
                    fillOpacity="0.45"
                  />
                </svg>
              </div>
            </div>

            {/* Formulario */}
            <div className="p-8">
              <form onSubmit={handleCheckDni} className="space-y-6">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-purple-300 mb-2">
                    Número de Documento (DNI)
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      maxLength={8}
                      value={dni}
                      onChange={(e) => setDni(e.target.value.replace(/\D/g, ""))}
                      placeholder="Ej: 12345678"
                      disabled={loading}
                      className="w-full px-5 py-4 text-xl tracking-wider text-center font-mono rounded-2xl border border-white/10 bg-slate-950/40 text-white placeholder-purple-300/30 outline-none focus:border-purple-400 focus:ring-4 focus:ring-purple-500/20 transition-all duration-200 shadow-inner"
                      autoFocus
                    />
                  </div>
                </div>

                {errorMsg && (
                  <div className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-sm text-red-200 leading-relaxed animate-shake">
                    <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p>{errorMsg}</p>
                      {errorMsg.includes("8 segundos") && (
                        <button
                          type="button"
                          onClick={handleCheckDni}
                          className="mt-2 text-xs font-bold text-red-300 hover:text-white underline flex items-center gap-1"
                        >
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          Reintentar ahora
                        </button>
                      )}
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 rounded-2xl text-white font-extrabold text-base bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-purple-500/20 flex items-center justify-center gap-2 btn-shimmer"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Verificando...
                    </>
                  ) : (
                    "Ingresar a Acreditación"
                  )}
                </button>
              </form>

              {/* Aviso */}
              <div className="mt-6 flex items-start gap-2 text-xs text-purple-300/60 leading-relaxed border-t border-white/5 pt-4">
                <Shield className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <p>
                  Tu seguridad nos importa. El sistema solo registrará tu ingreso si poseés una pre-inscripción válida en la edición 2026.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal DNI no registrado (Caso 4: Redirección a Inscripción Rápida con DNI) */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-[#2d1854]/95 border border-white/10 backdrop-blur-xl rounded-3xl shadow-2xl max-w-sm w-full p-8 text-center text-white animate-fade-in-up">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-amber-500/15 border border-amber-500/30 mb-4 shadow-[0_0_15px_rgba(245,158,11,0.2)] animate-gentle-pulse">
                <AlertCircle className="w-10 h-10 text-amber-400" />
              </div>
              <h2 className="text-2xl font-extrabold mb-2 text-glow">
                DNI no registrado
              </h2>
              <p className="text-purple-200/80 text-sm mb-6 leading-relaxed">
                No encontramos el DNI <span className="font-bold text-white">{dni}</span> en nuestro listado de pre-inscriptos de 2026. Podés completar tu acreditación exprés ahora mismo.
              </p>

              {/* Botón primario: Inscripción Rápida */}
              <button
                onClick={() => {
                  setShowModal(false);
                  navigate(`/registro-rapido?dni=${encodeURIComponent(dni.trim())}`);
                }}
                className="w-full py-4 rounded-2xl text-white font-extrabold bg-gradient-to-r from-amber-500 via-orange-600 to-purple-700 hover:from-amber-400 hover:to-purple-600 transition-all duration-200 shadow-lg shadow-orange-500/25 flex items-center justify-center gap-2 btn-shimmer"
              >
                <Zap className="w-5 h-5 text-yellow-300" />
                ⚡ Inscripción Rápida
              </button>

              <button
                onClick={() => {
                  setShowModal(false);
                  navigate("/seleccion-registro");
                }}
                className="w-full mt-3 py-2.5 rounded-2xl font-bold text-xs text-purple-200 bg-white/5 hover:bg-white/10 transition-all duration-200 border border-white/5"
              >
                Otras opciones de registro
              </button>

              <button
                onClick={() => setShowModal(false)}
                className="w-full mt-2 py-2 rounded-2xl font-bold text-purple-300 hover:text-white transition-all duration-200 text-xs"
              >
                Volver a intentar
              </button>
            </div>
          </div>
        )}

        {/* Modal Rechazado */}
        {showRejectedModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-[#2d1854]/95 border border-red-500/30 backdrop-blur-xl rounded-3xl shadow-2xl max-w-sm w-full p-8 text-center text-white animate-fade-in-up">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/20 border border-red-500/40 mb-4 shadow-[0_0_20px_rgba(239,68,68,0.3)] animate-gentle-pulse">
                <AlertCircle className="w-10 h-10 text-red-400" />
              </div>
              <h2 className="text-2xl font-extrabold mb-2 text-glow text-red-300">
                Registro no habilitado
              </h2>
              <p className="text-purple-200/90 text-sm mb-6 leading-relaxed">
                {rejectedMsg || "Tu registro figura con estado rechazado. Por favor, acercate a la coordinación en la mesa de recepción para verificar tu situación."}
              </p>

              <button
                onClick={() => {
                  setShowRejectedModal(false);
                  setStep("input_dni");
                  setDni("");
                }}
                className="w-full py-3.5 rounded-2xl text-white font-bold bg-white/10 hover:bg-white/20 transition-all duration-200 border border-white/10"
              >
                Entendido
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ── Paso 2: Confirmación Intermedia de Datos (Glassmorphism & Lilac Style) ──
  if (step === "verify_details" && asistenteDetails) {
    // Texto dinámico para datos provisorios
    let provisionalWarningText = "";
    if (isPhoneGeneric && isEmailProvisional) {
      provisionalWarningText = "⚠️ Tu teléfono y correo actual son provisorios. Actualizalos para recibir tu certificado oficial al cierre de la jornada.";
    } else if (isPhoneGeneric) {
      provisionalWarningText = "⚠️ Tu teléfono actual es provisorio. Actualizalo para recibir tu certificado oficial al cierre de la jornada.";
    } else if (isEmailProvisional) {
      provisionalWarningText = "⚠️ Tu correo actual es provisorio. Actualizalo para recibir tu certificado oficial al cierre de la jornada.";
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#2d1854] to-slate-950 p-4">
        {/* Orbes decorativos */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/4 -left-32 w-80 h-80 rounded-full bg-violet-600/10 blur-3xl orb-float" />
          <div className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full bg-purple-500/10 blur-3xl orb-float-delay" />
        </div>

        <div className="relative w-full max-w-lg mx-auto animate-fade-in-up">
          {/* Card Glassmorphic con base lila */}
          <div className="bg-[#2d1854]/45 backdrop-blur-xl rounded-3xl shadow-3xl overflow-hidden border border-white/10 text-white p-8">
            <h2 className="text-2xl font-extrabold text-white text-glow mb-2 flex items-center gap-2">
              <UserCheck className="w-7 h-7 text-purple-400" />
              Verificá tus Datos
            </h2>
            <p className="text-purple-200/80 text-sm mb-6 leading-relaxed">
              Confirmá que tus datos personales sean correctos antes de realizar la acreditación.
            </p>

            {/* Banner de Advertencia de Certificados */}
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 text-amber-200 text-sm flex items-start gap-3 shadow-[0_0_15px_rgba(245,158,11,0.05)] mb-6 leading-relaxed">
              <AlertCircle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-bold text-amber-300">⚠️ Importante para tu Certificado</p>
                <p className="mt-1 text-xs text-amber-200/90">
                  Revisá que tu Nombre, Apellido y Email estén correctamente escritos. Cualquier error tipográfico provocará que tu certificado digital de asistencia se emita con errores o falle su entrega.
                </p>
              </div>
            </div>

            {/* Caso 3: Control de Datos Provisorios Detectados */}
            {hasProvisionalData && (
              <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-4 text-rose-200 text-sm flex items-start gap-3 shadow-[0_0_15px_rgba(244,63,94,0.05)] mb-6 leading-relaxed animate-gentle-pulse">
                <AlertCircle className="w-5 h-5 text-rose-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-bold text-rose-300">🚨 Datos Provisorios Detectados</p>
                  <p className="mt-1 text-xs text-rose-200/90 font-medium">
                    {provisionalWarningText}
                  </p>
                </div>
              </div>
            )}

            {/* Listado de Datos */}
            <div className="bg-slate-950/40 rounded-2xl p-6 border border-white/5 space-y-4 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Nombre</span>
                  <span className="text-base font-bold text-white">{asistenteDetails.first_name}</span>
                </div>
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Apellido</span>
                  <span className="text-base font-bold text-white">{asistenteDetails.last_name}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">DNI</span>
                  <span className="text-base font-bold text-white">{asistenteDetails.dni}</span>
                </div>
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Celular</span>
                  {isPhoneGeneric ? (
                    <span className="text-xs font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-lg inline-block">
                      {asistenteDetails.phone || "No especificado"} (Provisorio)
                    </span>
                  ) : (
                    <span className="text-base font-bold text-white">{asistenteDetails.phone || "No especificado"}</span>
                  )}
                </div>
              </div>

              <div>
                <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Correo electrónico</span>
                {isEmailProvisional ? (
                  <span className="text-xs font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-lg inline-block mt-0.5">
                    {asistenteDetails.email || "No especificado"} (Provisorio)
                  </span>
                ) : (
                  <span className="text-base font-bold text-white block truncate">{asistenteDetails.email}</span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-3">
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Institución</span>
                  <span className="text-sm font-bold text-white">{asistenteDetails.institution || "No especificado"}</span>
                </div>
                <div>
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-purple-300/60">Carrera</span>
                  <span className="text-sm font-bold text-white">{asistenteDetails.career || "No especificado"}</span>
                </div>
              </div>
            </div>

            {errorMsg && (
              <div className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/30 rounded-2xl p-4 mb-6 leading-relaxed">
                <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-200">{errorMsg}</p>
              </div>
            )}

            {/* Botones de acción */}
            <div className="flex flex-col gap-3">
              {hasProvisionalData ? (
                <div className="text-center text-xs text-rose-400/90 font-bold bg-rose-500/5 py-3 rounded-2xl border border-rose-500/20 mb-1">
                  🔒 La confirmación directa está bloqueada hasta actualizar tus datos provisorios.
                </div>
              ) : (
                <button
                  onClick={handleConfirmDirect}
                  disabled={loading}
                  className="w-full py-4 rounded-2xl text-white font-extrabold text-base bg-gradient-to-r from-violet-600 to-purple-700 hover:from-violet-500 hover:to-purple-600 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2 btn-shimmer border border-white/10"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Check className="w-5 h-5" />
                  )}
                  Sí, mis datos son correctos (Confirmar)
                </button>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("input_dni")}
                  className="flex-1 py-3.5 rounded-2xl font-bold bg-white/5 hover:bg-white/10 active:scale-[0.98] transition-all duration-200 text-sm border border-white/5 flex items-center justify-center gap-2 text-purple-200"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Volver
                </button>

                <button
                  onClick={() => setStep("edit_details")}
                  className={`flex-1 py-3.5 rounded-2xl font-bold active:scale-[0.98] transition-all duration-200 text-sm flex items-center justify-center gap-2 ${
                    hasProvisionalData
                      ? "bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-lg shadow-purple-500/25 border border-white/20 btn-shimmer"
                      : "bg-purple-500/20 hover:bg-purple-500/35 text-purple-100 border border-purple-500/30"
                  }`}
                >
                  <Edit2 className="w-4 h-4" />
                  Modificar Datos
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Paso 3: Formulario de Modificación Fluida ──
  if (step === "edit_details" && asistenteDetails) {
    const isPhoneInputProvisional = !editFields.phone.trim() || editFields.phone.trim() === "1111111111";
    const isEmailInputProvisional = !editFields.email.trim() || editFields.email.toLowerCase().includes(".temp") || !/^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/.test(editFields.email.trim());

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-[#2d1854] to-slate-950 p-4">
        {/* Orbes decorativos */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/4 -left-32 w-80 h-80 rounded-full bg-violet-600/10 blur-3xl orb-float" />
          <div className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full bg-purple-500/10 blur-3xl orb-float-delay" />
        </div>

        <div className="relative w-full max-w-lg mx-auto animate-fade-in-up">
          {/* Card Glassmorphic */}
          <div className="bg-[#2d1854]/45 backdrop-blur-xl rounded-3xl shadow-3xl overflow-hidden border border-white/10 text-white p-8">
            <h2 className="text-2xl font-extrabold text-white text-glow mb-2 flex items-center gap-2">
              <Edit2 className="w-6 h-6 text-purple-400" />
              Editar Información
            </h2>
            <p className="text-purple-200/80 text-sm mb-6 leading-relaxed">
              Modificá los campos necesarios para tu acreditación y certificado digital.
            </p>

            <form onSubmit={handleConfirmWithEdit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">Nombre</label>
                  <input
                    type="text"
                    value={editFields.first_name}
                    onChange={(e) => setEditFields({ ...editFields, first_name: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm rounded-xl border border-white/10 bg-slate-950/40 text-white outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                    placeholder="Tu nombre"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">Apellido</label>
                  <input
                    type="text"
                    value={editFields.last_name}
                    onChange={(e) => setEditFields({ ...editFields, last_name: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm rounded-xl border border-white/10 bg-slate-950/40 text-white outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                    placeholder="Tu apellido"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">
                  Correo Electrónico {isEmailInputProvisional && "(Corregir)"}
                </label>
                <input
                  type="email"
                  value={editFields.email.includes(".temp") ? "" : editFields.email}
                  onChange={(e) => setEditFields({ ...editFields, email: e.target.value })}
                  placeholder="ejemplo@correo.com"
                  className={`w-full px-4 py-2.5 text-sm rounded-xl border outline-none transition-all duration-200 ${
                    isEmailInputProvisional
                      ? "border-rose-500/80 focus:ring-4 focus:ring-rose-500/20 bg-rose-950/20 shadow-[0_0_12px_rgba(244,63,94,0.35)] font-bold placeholder:text-rose-300/40 text-white"
                      : "border-white/10 bg-slate-950/40 text-white focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                  }`}
                />
                {isEmailInputProvisional && (
                  <span className="block text-[10px] font-semibold text-rose-300 mt-1.5">
                    ⚠️ Se requiere un correo real para recibir tu certificado digital.
                  </span>
                )}
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">
                  Número de Celular {editFields.phone === "1111111111" && "(Corregir)"}
                </label>
                <input
                  type="tel"
                  value={editFields.phone === "1111111111" ? "" : editFields.phone}
                  onChange={(e) => setEditFields({ ...editFields, phone: e.target.value.replace(/\D/g, "") })}
                  placeholder="Ej: 1123456789 (Sin guiones)"
                  className={`w-full px-4 py-2.5 text-sm rounded-xl border outline-none transition-all duration-200 ${
                    isPhoneInputProvisional
                      ? "border-rose-500/80 focus:ring-4 focus:ring-rose-500/20 bg-rose-950/20 shadow-[0_0_12px_rgba(244,63,94,0.35)] font-bold placeholder:text-rose-300/40 text-white"
                      : "border-white/10 bg-slate-950/40 text-white focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                  }`}
                />
                {isPhoneInputProvisional && (
                  <span className="block text-[10px] font-semibold text-rose-300 mt-1.5">
                    ⚠️ Se requiere un número celular real para continuar.
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">Institución</label>
                  <input
                    type="text"
                    value={editFields.institution}
                    onChange={(e) => setEditFields({ ...editFields, institution: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm rounded-xl border border-white/10 bg-slate-950/40 text-white outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                    placeholder="ISDFYT 83 / UNaB"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-purple-300 mb-1.5">Carrera</label>
                  <input
                    type="text"
                    value={editFields.career}
                    onChange={(e) => setEditFields({ ...editFields, career: e.target.value })}
                    className="w-full px-4 py-2.5 text-sm rounded-xl border border-white/10 bg-slate-950/40 text-white outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20"
                    placeholder="LOGISTICA"
                  />
                </div>
              </div>

              {errorMsg && (
                <div className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/30 rounded-2xl p-4 mt-4 leading-relaxed">
                  <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-red-200">{errorMsg}</p>
                </div>
              )}

              {/* Botones de acción */}
              <div className="flex gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setStep("verify_details")}
                  className="flex-1 py-3.5 rounded-2xl font-bold bg-white/5 hover:bg-white/10 active:scale-[0.98] transition-all duration-200 text-sm border border-white/5 flex items-center justify-center gap-2 text-purple-200"
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  disabled={loading || isPhoneInputProvisional || isEmailInputProvisional}
                  className="flex-1 py-3.5 rounded-2xl text-white font-extrabold text-sm bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-400 hover:to-indigo-500 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2 btn-shimmer border border-white/10"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                  Guardar y Acreditar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
