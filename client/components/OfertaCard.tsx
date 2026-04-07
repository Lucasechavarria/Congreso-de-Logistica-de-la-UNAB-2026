import { Building2, MapPin, ExternalLink } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card";

interface OfertaCardProps {
  oferta: {
    id: number;
    titulo_puesto: string;
    descripcion: string;
    requisitos: string;
    modalidad: string;
    ubicacion: string;
    canal_postulacion: string;
    empresa_detalle?: {
      nombre_empresa: string;
      logo?: string;
    };
  };
}

const modalityColors: Record<string, string> = {
  REMOTO: "bg-green-500/20 text-green-400 border-green-500/30",
  PRESENCIAL: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  HIBRIDO: "bg-purple-500/20 text-purple-400 border-purple-500/30",
};

export default function OfertaCard({ oferta }: OfertaCardProps) {
  const {
    titulo_puesto,
    descripcion,
    modalidad,
    ubicacion,
    canal_postulacion,
    empresa_detalle,
  } = oferta;

  const handlePostular = () => {
    // Si es un email o URL, redirigir
    if (canal_postulacion.includes("@")) {
      window.location.href = `mailto:${canal_postulacion}?subject=Postulación - ${titulo_puesto}`;
    } else if (canal_postulacion.startsWith("http")) {
      window.open(canal_postulacion, "_blank");
    } else {
      // Por defecto intentar abrir como enlace si parece uno
      window.open(`https://${canal_postulacion}`, "_blank");
    }
  };

  return (
    <Card className="bg-[#1a0a2e]/60 backdrop-blur-md border border-[#9b6dd7]/30 hover:border-[#9b6dd7]/60 transition-all duration-300 group overflow-hidden shadow-lg h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1">
            <CardTitle className="text-xl font-bold text-white group-hover:text-congress-cyan transition-colors">
              {titulo_puesto}
            </CardTitle>
            <div className="flex items-center text-slate-400 mt-1 text-sm">
              <Building2 className="h-3 w-3 mr-1" />
              <span>{empresa_detalle?.nombre_empresa || "Empresa"}</span>
            </div>
          </div>
          {empresa_detalle?.logo ? (
            <div className="h-12 w-12 rounded-lg bg-white/10 p-2 flex items-center justify-center shrink-0 border border-white/5">
              <img
                src={empresa_detalle.logo}
                alt={empresa_detalle.nombre_empresa}
                className="max-h-full max-w-full object-contain"
              />
            </div>
          ) : (
             <div className="h-12 w-12 rounded-lg bg-white/5 flex items-center justify-center shrink-0 border border-white/5">
               <Building2 className="h-6 w-6 text-slate-500" />
             </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="flex-grow pt-2">
        <p className="text-slate-300 text-sm line-clamp-3 mb-4">
          {descripcion}
        </p>
        
        <div className="flex flex-wrap gap-2 mt-auto">
          <Badge variant="outline" className={`${modalityColors[modalidad] || ""} font-medium`}>
            {modalidad}
          </Badge>
          <div className="flex items-center text-slate-400 text-xs ml-auto">
            <MapPin className="h-3 w-3 mr-1" />
            {ubicacion}
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-4 border-t border-white/5">
        <Button 
          onClick={handlePostular}
          className="w-full bg-[#9b6dd7] hover:bg-[#8b5cf6] text-white font-semibold transition-all flex items-center justify-center gap-2"
        >
          Postular ahora
          <ExternalLink className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
