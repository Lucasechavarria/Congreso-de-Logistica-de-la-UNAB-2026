export type LogoItem = { src: string; alt: string; heightClass?: string };

// The main list of all company logos, sorted alphabetically.
// This is the single source of truth for all logos.
export const ALL_LOGOS: LogoItem[] = [
  { src: "/images/logos/AERONOVA.jpg", alt: "Aeronova", heightClass: "h-12" },
  { src: "/images/logos/ARLOG.png", alt: "ARLOG", heightClass: "h-12" },
  { src: "/images/logos/LOGO-CARGO.png", alt: "Cargo", heightClass: "h-12" },
  { src: "/images/logos/CHAGA.png", alt: "CHAGA", heightClass: "h-14" },
  { src: "/images/logos/CITYONE.png", alt: "CityOne", heightClass: "h-12" },
  { src: "/images/logos/CONWORK.jpg", alt: "Conwork", heightClass: "h-12" },
  { src: "/images/logos/EAL-GREEN.png", alt: "EAL Green", heightClass: "h-12" },
  { src: "/images/logos/ETRUCK.png", alt: "eTruck", heightClass: "h-12" },
  {
    src: "/images/logos/ELECTRITRUCK.jpeg",
    alt: "ElectriTruck",
    heightClass: "h-12",
  },
  {
    src: "/images/logos/ESCUELA-CHOFERES.png",
    alt: "Escuela de Choferes",
    heightClass: "h-10",
  },
  {
    src: "/images/logos/Folkode_Group.webp",
    alt: "Folkode Group",
    heightClass: "h-12",
  },
  {
    src: "/images/logos/GENBA-KAIZEN.jpeg",
    alt: "Genba Kaizen",
    heightClass: "h-16",
  },
  { src: "/images/logos/GLI.jpg", alt: "GLI", heightClass: "h-14" },
  {
    src: "/images/logos/GRUAS-GOLISANO.png",
    alt: "Gruas Golisano",
    heightClass: "h-12",
  },
  { src: "/images/logos/ICI.png", alt: "ICI", heightClass: "h-12" },
  { src: "/images/logos/KMD.png", alt: "KMD Logística", heightClass: "h-12" },
  {
    src: "/images/logos/KPI-CONSULTING.png",
    alt: "KPI Consulting",
    heightClass: "h-16",
  },
  { src: "/images/logos/LA-POSTAL.png", alt: "La Postal", heightClass: "h-12" },
  {
    src: "/images/logos/ELECE-LOGISTICA.png",
    alt: "Logística E-LECE",
    heightClass: "h-12",
  },
  {
    src: "/images/logos/LOGISTICA-GARPIC.png",
    alt: "Logística Garpic",
    heightClass: "h-16",
  },
  { src: "/images/logos/M-RRHH.jpeg", alt: "M-RRHH", heightClass: "h-12" },
  { src: "/images/logos/MINISCENICS.jpeg", alt: "Miniscenics", heightClass: "h-12" },
  { src: "/images/logos/MUVON.png", alt: "Muvon", heightClass: "h-12" },
  {
    src: "/images/logos/NYG-TRANSPORTES.PNG",
    alt: "N&G Transportes",
    heightClass: "h-16",
  },
  {
    src: "/images/logos/NUCLEO-LOGISTICO.jpeg",
    alt: "Núcleo Logístico",
    heightClass: "h-16",
  },
  {
    src: "/images/logos/PERFORMANCE-LUBE.png",
    alt: "Performance Lube",
    heightClass: "h-12",
  },
  { src: "/images/logos/PYB.jpg", alt: "PYB", heightClass: "h-16" },
  { src: "/images/logos/RASTA.png", alt: "Rasta", heightClass: "h-12" },
  {
    src: "/images/logos/RED-LOGISTICA.webp",
    alt: "Red Logística",
    heightClass: "h-12",
  },
  {
    src: "/images/logos/RED-PARQUES.png",
    alt: "Red Parques Digital",
    heightClass: "h-12",
  },
  { src: "/images/logos/SHIAFFER.png", alt: "Shiaffer", heightClass: "h-12" },
  { src: "/images/logos/STARGPS.png", alt: "StarGPS", heightClass: "h-10" },
  { src: "/images/logos/SURFRIGO.jpeg", alt: "Surfrigo", heightClass: "h-12" },
  { src: "/images/logos/TRADEN.png", alt: "Traden", heightClass: "h-14" },
  {
    src: "/images/logos/TRANSPORTE-DOMINGUEZ.png",
    alt: "Transporte Dominguez",
    heightClass: "h-12",
  },
  { src: "/images/logos/UCASAL.png", alt: "UCASAL", heightClass: "h-12" },
  { src: "/images/logos/UNLAM.png", alt: "UNLaM", heightClass: "h-14" },
  { src: "/images/logos/UNLP.png", alt: "UNLP", heightClass: "h-12" },
  { src: "/images/logos/UNLZ.png", alt: "UNLZ", heightClass: "h-12" },
  { src: "/images/logos/UNS.jpg", alt: "UNS", heightClass: "h-12" },
  { src: "/images/logos/UPE.png", alt: "UPE", heightClass: "h-12" },
  { src: "/images/logos/UTN.png", alt: "UTN", heightClass: "h-12" },
  {
    src: "/images/logos/VDM-LOGISTICS.jpg",
    alt: "VDM Logistics",
    heightClass: "h-10",
  },
  { src: "/images/logos/VELOX.jpeg", alt: "Velox", heightClass: "h-12" },
  { src: "/images/logos/VIMA.png", alt: "VIMA", heightClass: "h-12" },
  { src: "/images/logos/VOS.jpeg", alt: "VOS", heightClass: "h-12" },
  { src: "/images/logos/XPERTS.jpeg", alt: "Xperts", heightClass: "h-12" },
  { src: "/images/logos/Zento.jpg", alt: "Zento", heightClass: "h-12" },
];

// Split the main list into chunks for the carousels.
const carouselChunkSize = Math.ceil(ALL_LOGOS.length / 3);
export const FIRST_CAROUSEL_LOGOS: LogoItem[] = ALL_LOGOS.slice(
  0,
  carouselChunkSize
);
export const SECOND_CAROUSEL_LOGOS: LogoItem[] = ALL_LOGOS.slice(
  carouselChunkSize,
  2 * carouselChunkSize
);
export const THIRD_CAROUSEL_LOGOS: LogoItem[] = ALL_LOGOS.slice(
  2 * carouselChunkSize
);

// For compatibility, a default export is provided.
export const DEFAULT_LOGOS: LogoItem[] = ALL_LOGOS;

export function chunk<T>(arr: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}
