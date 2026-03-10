import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { API_HOST } from "@/lib/api";
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Chip from '@mui/material/Chip';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import {
  Category,
  School,
  Person,
  LocalShipping,
  DirectionsCar,
  Inventory,
  Computer,
  Nature,
  Lightbulb,
  Business,
  Group,
  Close,
  AccessTime,
  LocationOn
} from '@mui/icons-material';
import { motion, AnimatePresence } from "framer-motion";
import FloatingParticles from "@/components/FloatingParticles";

// Información completa del disertante
type DisertanteInfo = {
  nombre: string;
  bio: string;
  foto_url: string;
  tema_presentacion: string;
  linkedin?: string;
};

// Nueva estructura de datos para actividades con hora de inicio y fin
type ActividadCalendar = {
  aula: string;
  titulo: string;
  disertantes: DisertanteInfo[];
  descripcion?: string;
  inicio: string; // 'HH:MM'
  fin: string; // 'HH:MM'
  color: string; // color de fondo
  categoria: string; // Categoría del track
};

// Aulas de ejemplo (sin Aula 8 y Aula 9)
const AULAS = [
  "Aula Magna",
  "Aula 1",
  "Aula 2",
  "Aula 3",
  "Aula 4",
  "Aula 5",
  "Aula 6",
  "Aula 7",
];

// Generar horarios fijos cada 15 minutos de 10:00 a 19:00
function getHorariosFijos() {
  const horarios: string[] = [];
  let h = 10, m = 0;
  while (h < 19 || (h === 19 && m === 0)) {
    const hora = `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}`;
    horarios.push(hora);
    m += 15;
    if (m === 60) {
      m = 0;
      h++;
    }
  }
  return horarios;
}

// Categorías de tracks del congreso de logística y transporte
const TRACK_CATEGORIES = {
  "TECNOLOGIA": { bg: "#7c3aed", text: "#ffffff", icon: Computer }, // violeta
  "LOGISTICA": { bg: "#1e40af", text: "#ffffff", icon: LocalShipping }, // azul institucional
  "PUERTOS/COMERCIO EXTERIOR": { bg: "#dc2626", text: "#ffffff", icon: Inventory }, // rojo
  "E-COMMERS": { bg: "#be185d", text: "#ffffff", icon: Business }, // rosa
  "SUPPLY CHAIN": { bg: "#0891b2", text: "#ffffff", icon: Inventory }, // cyan
  "CAPITAL HUMANO": { bg: "#059669", text: "#ffffff", icon: Group }, // verde
  "RADIO": { bg: "#374151", text: "#ffffff", icon: Nature }, // gris
  "SUSTENTABILIDAD": { bg: "#ea580c", text: "#ffffff", icon: Nature }, // naranja
  "TRANSPORTE": { bg: "#0ea5e9", text: "#ffffff", icon: DirectionsCar }, // azul claro
} as const;

// Paleta para aulas (más suave para el fondo de las tarjetas)
const AULA_COLORS: Record<
  string,
  { border: string; bg: string; text: string }
> = {
  "Aula Magna": { border: "#2563eb", bg: "#eff6ff", text: "#1e40af" }, // azul UNAB
  "Aula 1": { border: "#0ea5e9", bg: "#f0f9ff", text: "#0369a1" }, // cyan
  "Aula 2": { border: "#f59e42", bg: "#fffbeb", text: "#d97706" }, // naranja
  "Aula 3": { border: "#a21caf", bg: "#fdf4ff", text: "#a21caf" }, // violeta
  "Aula 4": { border: "#22c55e", bg: "#f0fdf4", text: "#16a34a" }, // verde
  "Aula 5": { border: "#dc2626", bg: "#fef2f2", text: "#dc2626" }, // rojo
  "Aula 6": { border: "#7c3aed", bg: "#f5f3ff", text: "#7c3aed" }, // violeta
  "Aula 7": { border: "#059669", bg: "#ecfdf5", text: "#059669" }, // esmeralda
  "Aula 8": { border: "#be185d", bg: "#fdf2f8", text: "#be185d" }, // rosa
};

// Función para generar colores únicos basados en el nombre del disertante
function getDisertanteColor(disertante: string): string {
  // Array de colores para los disertantes
  const colorsPool = [
    "#1e40af", // azul
    "#059669", // verde
    "#dc2626", // rojo
    "#7c3aed", // violeta
    "#ea580c", // naranja
    "#0891b2", // cyan
    "#be185d", // rosa
    "#374151", // gris
    "#16a34a", // verde claro
    "#d97706", // amarillo
    "#a21caf", // magenta
    "#0369a1", // azul claro
    "#b45309", // marrón
    "#15803d", // verde oscuro
    "#7c2d12", // marrón oscuro
  ];

  // Crear hash simple del nombre del disertante
  let hash = 0;
  for (let i = 0; i < disertante.length; i++) {
    const char = disertante.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convertir a 32bit integer
  }

  // Usar el hash para seleccionar un color
  const colorIndex = Math.abs(hash) % colorsPool.length;
  return colorsPool[colorIndex];
}

// Función para construir la URL completa de la imagen del disertante
function getDisertanteImageUrl(fotoUrl: string): string {
  if (!fotoUrl) return "";

  const DOMAIN_PROD = "https://www.congresologistica.unab.edu.ar";
  let url = fotoUrl.trim();

  // Si ya viene como URL absoluta HTTPS válida, retornarla directamente
  if (url.startsWith("https://")) {
    return url;
  }

  // Forzar HTTPS si viene con http://
  if (url.startsWith("http://")) {
    return url.replace("http://", "https://");
  }

  // Limpiar rutas mal formadas que incluyen el path completo del servidor
  if (url.includes("Congreso-UNAB/backend/media/")) {
    url = url.split("media/")[1];
    return `${DOMAIN_PROD}/media/${url}`;
  }

  // Si es ruta absoluta del servidor /media/...
  if (url.startsWith("/media/")) {
    return `${DOMAIN_PROD}${url}`;
  }

  // Si es solo ponencias/imagen.png
  if (url.startsWith("ponencias/")) {
    return `${DOMAIN_PROD}/media/${url}`;
  }

  // Si es una ruta relativa tipo media/...
  if (url.startsWith("media/")) {
    return `${DOMAIN_PROD}/${url}`;
  }

  // Si es solo el nombre del archivo (ej: nombre.png)
  if (!url.includes("/")) {
    return `${DOMAIN_PROD}/media/ponencias/${url}`;
  }

  // Default: asumir que es una ruta relativa en media
  return `${DOMAIN_PROD}/media/${url}`;
}

// Estado para actividades y carga
export default function Programa() {
  const [actividades, setActividades] = useState<ActividadCalendar[] | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Variable para controlar si se muestra el programa completo o el banner "Convocatoria"
  // ACUALMENTE FORZADO EN FALSE PARA MOSTRAR LA CONVOCATORIA (VITE_PROGRAMA_DISPONIBLE=true en .env pero forzado a false aquí por directiva)
  const programaDisponible = false; // import.meta.env.VITE_PROGRAMA_DISPONIBLE === 'true' || false;

  // Fetch de la API de Django
  useEffect(() => {
    const fetchPrograma = async () => {
      try {
        const apiUrl = API_HOST;
        const response = await fetch(`${apiUrl}/api/programa/`);
        if (!response.ok)
          throw new Error("No se pudo cargar la agenda desde el backend.");
        const data = await response.json();
        // Mapear los datos del backend al formato visual
        const mapped: ActividadCalendar[] = data.map((item: any) => {
          const aula = item.aula || item.sala || "Aula Magna";
          // Si no hay disertantes, poner array vacío
          const disertantes: DisertanteInfo[] = Array.isArray(item.disertantes) ? item.disertantes.map((d: any) => ({
            nombre: d.nombre || "",
            bio: d.bio || "",
            foto_url: d.foto_url || "",
            tema_presentacion: d.tema_presentacion || "",
            linkedin: d.linkedin || ""
          })) : [];
          return {
            aula,
            titulo: item.titulo,
            disertantes,
            descripcion: item.descripcion || "",
            inicio: item.hora_inicio.substring(0, 5),
            fin: item.hora_fin.substring(0, 5),
            color: AULA_COLORS[aula] ? aula : "Aula Magna",
            categoria: item.categoria || "LOGÍSTICA",
          };
        });
        setActividades(mapped);
        setError(null);
      } catch (err) {
        console.error("Error cargando programa:", err);
        setError("No se pudo cargar la agenda desde el backend.");
        setActividades([]);
      } finally {
        setLoading(false);
      }
    };
    fetchPrograma();
  }, []);

  // Para calcular el número de filas que ocupa una actividad
  // Cada fila representa 15 minutos
  function getRowSpan(inicio: string, fin: string) {
    const [h1, m1] = inicio.split(":").map(Number);
    const [h2, m2] = fin.split(":").map(Number);
    const inicioMinutos = h1 * 60 + m1;
    const finMinutos = h2 * 60 + m2;
    const duracionMinutos = finMinutos - inicioMinutos;
    return Math.ceil(duracionMinutos / 15); // 15 minutos por fila
  }

  // Usar solo los datos reales de la base de datos
  const actividadesToShow = actividades || [];
  // Usar horarios fijos cada 30 minutos de 10:00 a 19:00
  const HORARIOS = getHorariosFijos();

  // Mapeo de actividades por aula y hora para renderizado
  const grid: { [aula: string]: { [hora: string]: ActividadCalendar | null } } =
    {};
  for (const aula of AULAS) {
    grid[aula] = {};
    for (const hora of HORARIOS) {
      grid[aula][hora] = null;
    }
  }
  for (const act of actividadesToShow) {
    // Solo agregar si el aula está definida en la grilla
    if (AULAS.includes(act.aula)) {
      grid[act.aula][act.inicio] = act;
    }
  }

  // Para saber si una celda debe renderizarse (solo la de inicio de actividad)
  function isStartOfActivity(aula: string, hora: string) {
    return grid[aula][hora] !== null;
  }

  // Para saber si una celda está ocupada por una actividad que empezó antes
  function isCellCovered(aula: string, hora: string) {
    // Convertir la hora actual a minutos para comparación precisa
    const [h, m] = hora.split(":").map(Number);
    const horaMinutos = h * 60 + m;

    // Buscar si hay una actividad que comenzó antes y termina después de la hora actual
    const actividad = actividadesToShow.find((a) => {
      if (a.aula !== aula) return false;

      const [h1, m1] = a.inicio.split(":").map(Number);
      const [h2, m2] = a.fin.split(":").map(Number);
      const inicioMinutos = h1 * 60 + m1;
      const finMinutos = h2 * 60 + m2;

      // La celda está cubierta si la hora actual está dentro del rango de la actividad
      // pero no es el inicio de la actividad
      return inicioMinutos < horaMinutos && horaMinutos < finMinutos;
    });

    return !!actividad;
  }

  // Estado para filtros
  const [filtroCategoria, setFiltroCategoria] = useState<string>("TODOS");
  const [filtroAula, setFiltroAula] = useState<string>("TODAS");

  // Categorías para el filtro (usando TRACK_CATEGORIES)
  const categorias = Object.keys(TRACK_CATEGORIES);

  // Disertantes únicos para el filtro
  const disertantesUnicos = Array.from(new Set(
    actividadesToShow.flatMap(act => act.disertantes.map(d => d.nombre))
  )).filter(d => d && d.length > 0);
  const [filtroDisertante, setFiltroDisertante] = useState<string>("TODOS");

  // Estado para el modal
  const [modalActividad, setModalActividad] = useState<ActividadCalendar | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Función para abrir el modal
  const abrirModal = (actividad: ActividadCalendar) => {
    setModalActividad(actividad);
    setIsModalOpen(true);
  };

  // Función para cerrar el modal
  const cerrarModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setModalActividad(null), 300); // Delay para la animación
  };

  // Filtrar actividades
  const actividadesFiltradas = actividadesToShow.filter(act => {
    if (filtroCategoria === "TODOS" && filtroAula === "TODAS" && filtroDisertante === "TODOS") {
      return true;
    }
    const matchCategoria = filtroCategoria === "TODOS" || act.categoria === filtroCategoria;
    const matchAula = filtroAula === "TODAS" || act.aula === filtroAula;
    const matchDisertante = filtroDisertante === "TODOS" || act.disertantes.some(d => d.nombre === filtroDisertante);
    return matchCategoria && matchAula && matchDisertante;
  });

  // Reconstruir la grilla con las actividades filtradas
  const gridFiltrada: { [aula: string]: { [hora: string]: ActividadCalendar | null } } = {};
  for (const aula of AULAS) {
    gridFiltrada[aula] = {};
    for (const hora of HORARIOS) {
      gridFiltrada[aula][hora] = null;
    }
  }
  for (const act of actividadesFiltradas) {
    // Solo agregar si el aula está definida en la grilla
    if (AULAS.includes(act.aula)) {
      gridFiltrada[act.aula][act.inicio] = act;
    }
  }

  // Función actualizada para verificar si una celda está cubierta (usando actividades filtradas)
  function isCellCoveredFiltrado(aula: string, hora: string) {
    // Convertir la hora actual a minutos para comparación precisa
    const [h, m] = hora.split(":").map(Number);
    const horaMinutos = h * 60 + m;

    // Buscar si hay una actividad que comenzó antes y termina después de la hora actual
    const actividad = actividadesFiltradas.find((a) => {
      if (a.aula !== aula) return false;

      const [h1, m1] = a.inicio.split(":").map(Number);
      const [h2, m2] = a.fin.split(":").map(Number);
      const inicioMinutos = h1 * 60 + m1;
      const finMinutos = h2 * 60 + m2;

      // La celda está cubierta si la hora actual está dentro del rango de la actividad
      // pero no es el inicio de la actividad
      return inicioMinutos < horaMinutos && horaMinutos < finMinutos;
    });

    return !!actividad;
  }

  // Componente del banner "Convocatoria Abierta" (Split Screen)
  const BannerProximamente = () => (
    <div className="min-h-screen bg-[#0f0728] flex items-center justify-center relative overflow-hidden">
      {/* Abstract Motion Background (Option 3 style) */}
      <div className="absolute inset-0 z-0">
        <FloatingParticles count={40} color="rgba(176, 126, 238, 0.4)" />
        {/* Horizontal glowing paths */}
        <div className="absolute top-1/4 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#9c62de] to-transparent opacity-50 shadow-[0_0_15px_rgba(156,98,222,0.8)]"></div>
        <div className="absolute top-2/4 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-[#b07eee] to-transparent opacity-30 shadow-[0_0_20px_rgba(176,126,238,0.8)]"></div>
        <div className="absolute top-3/4 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-congress-cyan to-transparent opacity-40 shadow-[0_0_10px_rgba(156,98,222,0.5)]"></div>

        {/* Blurred light refractions */}
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-96 h-96 bg-[#3a1b77] rounded-full mix-blend-screen filter blur-[100px] opacity-60 animate-pulse"></div>
        <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-96 h-96 bg-[#210d51] rounded-full mix-blend-screen filter blur-[120px] opacity-80 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10 h-full flex flex-col justify-center mt-16 md:mt-0">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-block px-4 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-[#b07eee] font-bold text-sm tracking-widest uppercase mb-4 shadow-[0_0_15px_rgba(176,126,238,0.3)]">
            Edición 2026
          </div>
          <h1 className="text-4xl md:text-6xl font-black text-white mb-4 tracking-tight drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
            CONVOCATORIA <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#9c62de] to-[#b07eee]">ABIERTA</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto font-light">
            Sé parte del mayor evento de logística y transporte. Presentá tu propuesta innovadora o exhibí tu marca ante los líderes del sector.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto w-full">
          {/* Card Disertantes (Option 2 style: Blue/Purple, Holographic glass) */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="group relative rounded-3xl overflow-hidden cursor-pointer selection-card"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-[#210d51]/80 to-[#3a1b77]/90 z-0 group-hover:opacity-90 transition-opacity duration-500"></div>
            {/* Holographic glass edge */}
            <div className="absolute inset-0 border-2 border-white/10 rounded-3xl z-10 pointer-events-none group-hover:border-[#9c62de]/50 transition-colors duration-500 shadow-[inset_0_0_30px_rgba(156,98,222,0.2)]"></div>

            <div className="relative z-20 p-8 md:p-10 flex flex-col h-full min-h-[420px] justify-between backdrop-blur-sm bg-white/5">
              <div>
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#9c62de] to-[#b07eee] flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(156,98,222,0.5)] group-hover:scale-110 transition-transform duration-500">
                  <Person className="text-white text-3xl" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">Ser Disertante</h2>
                <p className="text-slate-300 text-lg mb-6 leading-relaxed">
                  ¿Tenés un proyecto innovador, una investigación o desarrollos tecnológicos? Compartí tu experiencia en nuestro ciclo de conferencias.
                </p>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center text-slate-200">
                    <Lightbulb className="text-[#b07eee] mr-3 text-sm" /> Exposición dinámica
                  </li>
                  <li className="flex items-center text-slate-200">
                    <Group className="text-[#b07eee] mr-3 text-sm" /> Networking con referentes
                  </li>
                </ul>
              </div>

              <Link to="/registro-disertante" className="block w-full">
                <button className="w-full py-4 rounded-xl bg-white/10 hover:bg-[#9c62de] text-white font-bold tracking-wide transition-all duration-300 border border-white/20 hover:border-transparent group-hover:shadow-[0_0_30px_rgba(156,98,222,0.6)] flex items-center justify-center gap-2 mt-auto">
                  Postular Ponencia
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                </button>
              </Link>
            </div>
          </motion.div>

          {/* Card Empresas (Option 1/2 style: Green Logistics & Digital Twins / Cyan) */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="group relative rounded-3xl overflow-hidden cursor-pointer selection-card"
          >
            <div className="absolute inset-0 bg-gradient-to-bl from-[#0f0728]/90 to-congress-blue-dark/80 z-0 group-hover:opacity-90 transition-opacity duration-500"></div>
            {/* Tech grid overlay */}
            <div className="absolute inset-0 z-0 opacity-20 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:20px_20px]"></div>

            <div className="absolute inset-0 border-2 border-white/10 rounded-3xl z-10 pointer-events-none group-hover:border-congress-cyan-light/50 transition-colors duration-500 shadow-[inset_0_0_30px_rgba(176,126,238,0.2)]"></div>

            <div className="relative z-20 p-8 md:p-10 flex flex-col h-full min-h-[420px] justify-between backdrop-blur-sm bg-white/5">
              <div>
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-congress-blue to-congress-cyan flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(58,27,119,0.8)] group-hover:scale-110 transition-transform duration-500">
                  <Business className="text-white text-3xl" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">Exponer Empresa</h2>
                <p className="text-slate-300 text-lg mb-6 leading-relaxed">
                  Mostrá tu marca, productos y servicios ante un público hiper-segmentado. Formá parte del ecosistema intermodal de innovación.
                </p>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center text-slate-200">
                    <Inventory className="text-congress-cyan-light mr-3 text-sm" /> Stand en área de exhibición
                  </li>
                  <li className="flex items-center text-slate-200">
                    <Computer className="text-congress-cyan-light mr-3 text-sm" /> Presencia de marca digital
                  </li>
                </ul>
              </div>

              <Link to="/registro-empresas" className="block w-full">
                <button className="w-full py-4 rounded-xl bg-gradient-to-r from-congress-blue to-congress-cyan hover:from-congress-blue-dark hover:to-congress-blue text-white font-bold tracking-wide transition-all duration-300 shadow-[0_10px_20px_rgba(0,0,0,0.2)] group-hover:shadow-[0_0_30px_rgba(156,98,222,0.6)] flex items-center justify-center gap-2 border border-white/10 mt-auto">
                  Reservar Espacio
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                </button>
              </Link>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 1 }}
          className="mt-16 text-center"
        >
          <div className="inline-block text-[#b07eee] text-sm opacity-80 uppercase tracking-widest transition-opacity">
            Agenda en construcción. El cronograma completo estará disponible al finalizar la etapa de convocatoria.
          </div>
        </motion.div>
      </div>
    </div>
  );

  return (
    <>
      {!programaDisponible ? (
        <BannerProximamente />
      ) : (
        <div className="min-h-screen bg-slate-50 relative overflow-hidden">
          <FloatingParticles count={25} color="rgba(37, 99, 235, 0.15)" />

          {/* Hero Section */}
          <div className="bg-gradient-to-br from-congress-blue via-congress-blue/90 to-congress-cyan min-h-[40vh] flex items-center relative overflow-hidden">
            <div className="absolute inset-0 bg-black/10"></div>
            <FloatingParticles count={15} color="rgba(255, 255, 255, 0.2)" />
            <div className="container mx-auto px-4 relative z-10">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center"
              >
                <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 tracking-tight drop-shadow-lg">
                  Agenda_
                </h1>
                <p className="text-xl md:text-2xl text-white/90 max-w-4xl mx-auto font-light drop-shadow-md">
                  Charlas y actividades por aula • de 10:00 a 18:00 hs
                </p>
                {loading && (
                  <div className="text-white/80 mt-6 text-lg animate-pulse">Cargando agenda...</div>
                )}
                {error && <div className="text-red-200 mt-6 bg-red-500/20 p-4 rounded-xl border border-red-500/30 max-w-2xl mx-auto backdrop-blur-md">{error}</div>}
              </motion.div>
            </div>
          </div>

          {/* Filtros Modernos con MUI */}
          <Box sx={{ position: 'sticky', top: 144, zIndex: 40, background: 'transparent', py: 0, display: 'flex', justifyContent: 'center' }}>
            <Card sx={{ maxWidth: 1200, width: '100%', boxShadow: 6, borderRadius: 4, background: '#fff', px: { xs: 2, md: 6 }, py: { xs: 2, md: 3 } }}>
              <CardContent sx={{ display: 'flex', flexWrap: 'wrap', gap: { xs: 2, md: 3 }, alignItems: 'center', justifyContent: 'center', px: 0, mx: 'auto', width: '100%' }}>
                <Box sx={{
                  display: 'flex',
                  flexDirection: { xs: 'column', md: 'row' },
                  flexWrap: 'wrap',
                  gap: { xs: 2, md: 3 },
                  alignItems: { xs: 'stretch', md: 'center' },
                  justifyContent: 'center',
                  width: '100%'
                }}>
                  {/* Categoría */}
                  <FormControl sx={{ minWidth: { xs: '100%', md: 200 } }} size="small" variant="outlined">
                    <InputLabel id="categoria-label" sx={{ background: '#fff', px: 0.5, ml: -0.5 }}><Category sx={{ mr: 1, fontSize: 18 }} />Categoría</InputLabel>
                    <Select
                      labelId="categoria-label"
                      value={filtroCategoria}
                      label="Categoría"
                      onChange={(e) => setFiltroCategoria(e.target.value)}
                      sx={{ borderRadius: 2, fontWeight: 500 }}
                    >
                      <MenuItem value="TODOS">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Category sx={{ color: '#666', fontSize: 18 }} />
                          Todos los tracks
                        </Box>
                      </MenuItem>
                      {categorias.map(cat => {
                        const IconComponent = TRACK_CATEGORIES[cat as keyof typeof TRACK_CATEGORIES]?.icon;
                        return (
                          <MenuItem key={cat} value={cat}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {IconComponent && <IconComponent sx={{ color: TRACK_CATEGORIES[cat as keyof typeof TRACK_CATEGORIES]?.bg, fontSize: 18 }} />}
                              {cat}
                            </Box>
                          </MenuItem>
                        );
                      })}
                    </Select>
                  </FormControl>
                  {/* Aula */}
                  <FormControl sx={{ minWidth: { xs: '100%', md: 180 } }} size="small" variant="outlined">
                    <InputLabel id="aula-label" sx={{ background: '#fff', px: 0.5, ml: -0.5 }}><School sx={{ mr: 1, fontSize: 18 }} />Aula</InputLabel>
                    <Select
                      labelId="aula-label"
                      value={filtroAula}
                      label="Aula"
                      onChange={(e) => setFiltroAula(e.target.value)}
                      sx={{ borderRadius: 2, fontWeight: 500 }}
                    >
                      <MenuItem value="TODAS">Todas las aulas</MenuItem>
                      {AULAS.slice(0, 9).map(aula => (
                        <MenuItem key={aula} value={aula}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <School sx={{ color: AULA_COLORS[aula]?.border, fontSize: 18 }} />
                            {aula}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {/* Disertante */}
                  <Autocomplete
                    options={["TODOS", ...disertantesUnicos]}
                    value={filtroDisertante}
                    onChange={(_, value) => setFiltroDisertante(value || "TODOS")}
                    size="small"
                    sx={{ minWidth: { xs: '100%', md: 220 } }}
                    renderInput={(params) => (
                      <TextField {...params} label={<><Person sx={{ mr: 1, fontSize: 18 }} />Disertante</>} variant="outlined" sx={{ background: '#fff' }} />
                    )}
                  />
                  {/* Chips de filtros activos */}
                  <Box sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 1,
                    alignItems: 'center',
                    width: { xs: '100%', md: 'auto' },
                    justifyContent: { xs: 'flex-start', md: 'center' }
                  }}>
                    {filtroCategoria !== "TODOS" && (() => {
                      const IconComponent = TRACK_CATEGORIES[filtroCategoria as keyof typeof TRACK_CATEGORIES]?.icon;
                      return (
                        <Chip
                          icon={IconComponent ? <IconComponent sx={{ color: '#fff !important', fontSize: 16 }} /> : undefined}
                          label={filtroCategoria}
                          color="primary"
                          size="small"
                          sx={{ bgcolor: TRACK_CATEGORIES[filtroCategoria as keyof typeof TRACK_CATEGORIES]?.bg, color: '#fff', fontWeight: 500 }}
                          onDelete={() => setFiltroCategoria("TODOS")}
                        />
                      );
                    })()}
                    {filtroAula !== "TODAS" && (
                      <Chip
                        icon={<School sx={{ color: '#fff !important', fontSize: 16 }} />}
                        label={filtroAula}
                        color="secondary"
                        size="small"
                        sx={{ bgcolor: AULA_COLORS[filtroAula]?.border, color: '#fff', fontWeight: 500 }}
                        onDelete={() => setFiltroAula("TODAS")}
                      />
                    )}
                    {filtroDisertante !== "TODOS" && (
                      <Chip
                        icon={<Person sx={{ color: '#fff !important', fontSize: 16 }} />}
                        label={filtroDisertante}
                        color="default"
                        size="small"
                        sx={{ bgcolor: '#374151', color: '#fff', fontWeight: 500 }}
                        onDelete={() => setFiltroDisertante("TODOS")}
                      />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Vista Desktop - Grilla */}
          <div className="hidden md:block bg-gray-50 min-h-screen py-8">
            <div className="w-full px-4">
              <div className="w-full max-w-full mx-auto">

                {/* Grilla Principal - Usando tabla para mejor control de rowspan */}
                <div className="bg-white rounded-2xl shadow-xl overflow-hidden w-full">
                  <div className="w-full">
                    <table className="w-full table-fixed"
                      style={{ minWidth: 'auto' }}>

                      {/* Header de aulas */}
                      <thead>
                        <tr className="bg-gradient-to-r from-congress-blue to-congress-cyan text-white">
                          <th className="w-32 p-4 font-bold text-center border-r border-white/20">
                            Horario
                          </th>
                          {AULAS.filter(aula => aula !== "Aula 8").slice(0, 8).map((aula) => (
                            <th key={aula} className="p-4 font-bold text-center border-r border-white/20 last:border-r-0 text-sm">
                              {aula}
                            </th>
                          ))}
                        </tr>
                      </thead>

                      {/* Filas de horarios */}
                      <tbody>
                        {HORARIOS.map((hora, rowIdx) => (
                          <tr key={hora} className="border-b border-gray-200 min-h-[80px]">
                            {/* Columna de horario */}
                            <td className="w-32 bg-gray-50 p-4 text-center border-r border-gray-200 align-middle">
                              <div className="text-center">
                                <div className="text-xl font-bold text-congress-blue font-mono">
                                  {hora}
                                </div>
                                <div className="text-xs text-gray-500 uppercase tracking-wide">
                                  GMT -3
                                </div>
                              </div>
                            </td>

                            {/* Columnas de aulas */}
                            {AULAS.filter(aula => aula !== "Aula 8").slice(0, 8).map((aula) => {
                              if (isCellCoveredFiltrado(aula, hora)) return null;

                              const actividad = gridFiltrada[aula] && gridFiltrada[aula][hora];
                              if (actividad) {
                                const rowSpan = getRowSpan(actividad.inicio, actividad.fin);
                                const trackColor = TRACK_CATEGORIES[actividad.categoria as keyof typeof TRACK_CATEGORIES];
                                const aulaColor = AULA_COLORS[actividad.color] || AULA_COLORS["Aula Magna"];
                                const disertanteColor = getDisertanteColor(actividad.disertantes[0]?.nombre || "");

                                return (
                                  <td
                                    key={aula + hora}
                                    rowSpan={rowSpan}
                                    className="border-r border-gray-200 p-2 align-top"
                                    style={{
                                      minHeight: `${rowSpan * 80}px`,
                                    }}
                                  >
                                    <motion.div
                                      initial={{ opacity: 0, scale: 0.95 }}
                                      animate={{ opacity: 1, scale: 1 }}
                                      transition={{ duration: 0.3 }}
                                      className="h-full"
                                    >
                                      <div
                                        className="w-full h-full bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-3 border-l-4 hover:scale-[1.02] cursor-pointer group"
                                        onClick={() => abrirModal(actividad)}
                                        style={{
                                          borderLeftColor: disertanteColor,
                                          minHeight: `${Math.max(rowSpan * 76, 100)}px`,
                                          boxShadow: `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), -4px 0 6px -1px ${disertanteColor}20`
                                        }}>

                                        {/* Categoría Tag */}
                                        <div className="flex items-center mb-2">
                                          <span
                                            className="px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wide flex items-center gap-1"
                                            style={{
                                              backgroundColor: trackColor?.bg || aulaColor.border,
                                              color: trackColor?.text || 'white'
                                            }}
                                          >
                                            {(() => {
                                              const IconComponent = TRACK_CATEGORIES[actividad.categoria as keyof typeof TRACK_CATEGORIES]?.icon;
                                              return IconComponent ? <IconComponent style={{ fontSize: 14, color: trackColor?.text || 'white' }} /> : null;
                                            })()}
                                            {actividad.categoria}
                                          </span>
                                        </div>

                                        {/* Título */}
                                        <h3 className="font-bold text-sm text-gray-900 mb-2 group-hover:text-congress-blue transition-colors overflow-hidden leading-tight"
                                          style={{
                                            display: '-webkit-box',
                                            WebkitLineClamp: 2,
                                            WebkitBoxOrient: 'vertical'
                                          }}>
                                          {actividad.titulo.replace(/\s*\(\d+h\)/gi, "")}
                                        </h3>

                                        {/* Speakers */}
                                        <div className="text-xs font-semibold text-gray-700 mb-1 truncate flex flex-wrap gap-1">
                                          {actividad.disertantes.map((d, idx) => (
                                            <span key={d.nombre + idx}>{d.nombre}{idx < actividad.disertantes.length - 1 ? ',' : ''}</span>
                                          ))}
                                        </div>

                                        {/* Descripción */}
                                        {actividad.descripcion && (
                                          <p className="text-xs text-gray-600 overflow-hidden leading-tight"
                                            style={{
                                              display: '-webkit-box',
                                              WebkitLineClamp: rowSpan > 2 ? 3 : 2,
                                              WebkitBoxOrient: 'vertical'
                                            }}>
                                            {actividad.descripcion}
                                          </p>
                                        )}
                                      </div>
                                    </motion.div>
                                  </td>
                                );
                              } else {
                                return (
                                  <td key={aula + hora} className="border-r border-gray-200 p-3 text-center align-middle">
                                    <span className="text-gray-300 text-sm">-</span>
                                  </td>
                                );
                              }
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Vista Móvil - Lista por Horarios (estilo Nerdear.la) */}
          <div className="md:hidden bg-gray-50 min-h-screen py-4">
            <div className="px-4 space-y-6">
              {HORARIOS.map((hora) => {
                // Obtener todas las actividades que empiezan en esta hora
                const actividadesEnHora = actividadesFiltradas.filter(act => act.inicio === hora);

                if (actividadesEnHora.length === 0) return null;

                return (
                  <div key={hora} className="space-y-4">
                    {/* Encabezado de hora */}
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4 }}
                      className="sticky top-20 z-10 bg-gradient-to-r from-congress-blue to-congress-cyan rounded-xl p-4 shadow-lg"
                    >
                      <h3 className="text-2xl font-bold text-white">
                        {hora} <span className="text-sm font-normal opacity-90">(GMT -3)</span>
                      </h3>
                    </motion.div>

                    {/* Actividades en esta hora */}
                    <div className="space-y-3">
                      {actividadesEnHora.map((actividad, idx) => {
                        const trackColor = TRACK_CATEGORIES[actividad.categoria as keyof typeof TRACK_CATEGORIES];
                        const aulaColor = AULA_COLORS[actividad.color] || AULA_COLORS["Aula Magna"];
                        const disertanteColor = getDisertanteColor(actividad.disertantes[0]?.nombre || "");

                        return (
                          <motion.div
                            key={`${actividad.aula}-${actividad.inicio}-${idx}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.4, delay: idx * 0.1 }}
                            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border-l-4 cursor-pointer"
                            onClick={() => abrirModal(actividad)}
                            style={{
                              borderLeftColor: disertanteColor,
                              boxShadow: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06), -2px 0 4px -1px ${disertanteColor}20`
                            }}
                          >
                            <div className="p-4">
                              {/* Header con categoría y aula */}
                              <div className="flex items-center justify-between mb-3">
                                <span
                                  className="px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide flex items-center gap-1.5"
                                  style={{
                                    backgroundColor: trackColor?.bg || aulaColor.border,
                                    color: trackColor?.text || 'white'
                                  }}
                                >
                                  {(() => {
                                    const IconComponent = TRACK_CATEGORIES[actividad.categoria as keyof typeof TRACK_CATEGORIES]?.icon;
                                    return IconComponent ? <IconComponent style={{ fontSize: 14, color: trackColor?.text || 'white' }} /> : null;
                                  })()}
                                  {actividad.categoria}
                                </span>
                                <div className="flex items-center gap-2 text-sm">
                                  <span className="text-gray-600">{actividad.inicio} - {actividad.fin}</span>
                                  <span
                                    className="px-2 py-1 rounded-lg text-xs font-semibold"
                                    style={{
                                      backgroundColor: aulaColor.bg,
                                      color: aulaColor.text,
                                      border: `1px solid ${aulaColor.border}`
                                    }}
                                  >
                                    {actividad.aula}
                                  </span>
                                </div>
                              </div>

                              {/* Título */}
                              <h4 className="font-bold text-lg text-gray-900 mb-2 leading-tight">
                                {actividad.titulo.replace(/\s*\(\d+h\)/gi, "")}
                              </h4>

                              {/* Disertantes */}
                              <div className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2 flex-wrap">
                                <Person style={{ fontSize: 16, color: disertanteColor }} />
                                {actividad.disertantes.map((d, idx) => (
                                  <span key={d.nombre + idx}>{d.nombre}{idx < actividad.disertantes.length - 1 ? ',' : ''}</span>
                                ))}
                              </div>

                              {/* Descripción */}
                              {actividad.descripcion && (
                                <p className="text-sm text-gray-600 leading-relaxed">
                                  {actividad.descripcion}
                                </p>
                              )}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}

              {/* Mensaje si no hay actividades */}
              {actividadesFiltradas.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="text-gray-400 text-6xl mb-4">📅</div>
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    No hay actividades que coincidan con los filtros seleccionados
                  </h3>
                  <p className="text-gray-500">
                    Prueba ajustando los filtros para ver más charlas
                  </p>
                </motion.div>
              )}
            </div>
          </div>

          {/* Modal de Actividad estilo Nerdear.la */}
          <AnimatePresence>
            {isModalOpen && modalActividad && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4"
                onClick={cerrarModal}
              >
                {/* Overlay */}
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

                {/* Modal Content */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: 20 }}
                  className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto flex flex-col"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Header con imagen y categoría */}
                  <div
                    className="relative h-64 bg-gradient-to-br from-congress-blue to-congress-cyan overflow-hidden"
                    style={{
                      background: `linear-gradient(135deg, ${TRACK_CATEGORIES[modalActividad.categoria as keyof typeof TRACK_CATEGORIES]?.bg || '#1e40af'} 0%, ${getDisertanteColor(modalActividad.disertantes[0]?.nombre || "")} 100%)`
                    }}
                  >
                    {/* Botón de cierre */}
                    <button
                      onClick={cerrarModal}
                      className="absolute top-4 right-4 z-10 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-full p-2 transition-all duration-200"
                    >
                      <Close className="text-white text-xl" />
                    </button>

                    {/* Imagen del disertante */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      {/* Imagen del primer disertante si existe, si no, icono */}
                      {modalActividad.disertantes[0]?.foto_url ? (
                        <div className="w-44 h-44 rounded-full overflow-hidden bg-white/10 backdrop-blur-md border-4 border-white/30 shadow-2xl">
                          <img
                            src={getDisertanteImageUrl(modalActividad.disertantes[0].foto_url)}
                            alt={modalActividad.disertantes[0].nombre}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              // Log del error para debugging
                              console.error('Error cargando imagen del disertante:', {
                                nombre: modalActividad.disertantes[0]?.nombre,
                                foto_url_original: modalActividad.disertantes[0]?.foto_url,
                                foto_url_procesada: getDisertanteImageUrl(modalActividad.disertantes[0]?.foto_url)
                              });

                              // Fallback si la imagen no carga
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                parent.innerHTML = `
                              <div class=\"w-full h-full bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center\">
                                <svg class=\"text-white text-8xl w-22 h-22\" fill=\"currentColor\" viewBox=\"0 0 24 24\">
                                  <path d=\"M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z\"/>
                                </svg>
                              </div>
                            `;
                              }
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-44 h-44 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center shadow-2xl">
                          <Person className="text-white text-8xl" />
                        </div>
                      )}
                    </div>

                    {/* Logo/branding */}
                    <div className="absolute top-4 left-4">
                      <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-lg flex items-center justify-center">
                        {(() => {
                          const IconComponent = TRACK_CATEGORIES[modalActividad.categoria as keyof typeof TRACK_CATEGORIES]?.icon;
                          return IconComponent ? <IconComponent className="text-white text-2xl" /> : <Category className="text-white text-2xl" />;
                        })()}
                      </div>
                    </div>

                    {/* Etiqueta VIRTUAL/PRESENCIAL */}
                    <div className="absolute bottom-4 right-4">
                      <span className="bg-white/20 backdrop-blur-md text-white px-3 py-1 rounded-full text-sm font-semibold">
                        PRESENCIAL
                      </span>
                    </div>
                  </div>

                  {/* Contenido */}
                  <div className="p-6 overflow-y-auto flex-1">
                    {/* Título */}
                    <h2 className="text-2xl font-bold text-gray-900 mb-3 leading-tight">
                      {modalActividad.titulo.replace(/\s*\(\d+h\)/gi, "")}
                    </h2>

                    {/* Horario y fecha */}
                    <div className="flex items-center gap-4 mb-4 text-gray-600">
                      <div className="flex items-center gap-2">
                        <AccessTime className="text-lg" />
                        <span className="font-medium">
                          {modalActividad.inicio} - {modalActividad.fin} (GMT -3)
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <LocationOn className="text-lg" />
                        <span className="font-medium">{modalActividad.aula}</span>
                      </div>
                    </div>

                    {/* Disertantes */}
                    <div className="mb-4 max-h-[400px] overflow-y-auto">
                      {modalActividad.disertantes.map((d, idx) => (
                        <div key={d.nombre + idx} className="mb-4 flex flex-row items-start gap-4">
                          {/* Foto del disertante */}
                          {d.foto_url && (
                            <img
                              src={getDisertanteImageUrl(d.foto_url)}
                              alt={d.nombre}
                              className="w-20 h-20 object-cover rounded-full border border-gray-200 shadow-sm flex-shrink-0"
                              onError={(e) => {
                                console.error('Error cargando imagen del disertante en lista:', {
                                  nombre: d.nombre,
                                  foto_url_original: d.foto_url,
                                  foto_url_procesada: getDisertanteImageUrl(d.foto_url)
                                });
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                              }}
                            />
                          )}
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-800">
                              {d.nombre}
                            </h3>
                            {d.bio ? (
                              <p className="text-gray-600 text-sm leading-relaxed mb-2">
                                {d.bio}
                              </p>
                            ) : (
                              <p className="text-gray-600 text-sm">
                                Especialista en {modalActividad.categoria.toLowerCase()}
                              </p>
                            )}
                            {d.tema_presentacion && d.tema_presentacion !== "Título de la Presentación" && (
                              <p className="text-congress-blue text-sm font-medium">
                                📝 {d.tema_presentacion}
                              </p>
                            )}
                            {d.linkedin && (
                              <a
                                href={d.linkedin}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-congress-blue font-semibold text-xs mt-2 hover:underline hover:text-violet-700"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24" className="inline-block align-middle"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 11.268h-3v-5.604c0-1.337-.026-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.838-1.563 3.036 0 3.6 2.001 3.6 4.601v5.595z" /></svg>
                                LinkedIn
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Descripción */}
                    {modalActividad.descripcion && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-gray-800 mb-2">Descripción</h4>
                        <p className="text-gray-700 leading-relaxed">
                          {modalActividad.descripcion}
                        </p>
                      </div>
                    )}

                    {/* Categoría chip */}
                    <div className="flex items-center gap-2">
                      <span
                        className="px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide flex items-center gap-2"
                        style={{
                          backgroundColor: TRACK_CATEGORIES[modalActividad.categoria as keyof typeof TRACK_CATEGORIES]?.bg || '#1e40af',
                          color: TRACK_CATEGORIES[modalActividad.categoria as keyof typeof TRACK_CATEGORIES]?.text || 'white'
                        }}
                      >
                        {(() => {
                          const IconComponent = TRACK_CATEGORIES[modalActividad.categoria as keyof typeof TRACK_CATEGORIES]?.icon;
                          return IconComponent ? <IconComponent className="text-lg" /> : null;
                        })()}
                        {modalActividad.categoria}
                      </span>
                    </div>

                    {/* Botón de acción (opcional) */}
                    <div className="mt-6 pt-4 border-t border-gray-200">
                      <button
                        onClick={cerrarModal}
                        className="w-full bg-congress-blue hover:bg-congress-blue/90 text-white font-semibold py-3 px-6 rounded-xl transition-colors duration-200"
                      >
                        CERRAR
                      </button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </>
  );
}
