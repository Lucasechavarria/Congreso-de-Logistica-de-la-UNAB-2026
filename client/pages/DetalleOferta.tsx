import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { 
  getOfertaLaboral, 
  getOfertasLaborales 
} from "@/lib/api";
import { 
  Building2, 
  MapPin, 
  Briefcase, 
  Calendar, 
  ArrowLeft, 
  Send,
  ChevronRight,
  Clock,
  Globe,
  Share2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import { Helmet } from "react-helmet-async";
import { format } from "date-fns";
import { es } from "date-fns/locale";

export default function DetalleOferta() {
  const { id } = useParams<{ id: string }>();

  const { data: oferta, isLoading, error } = useQuery({
    queryKey: ['oferta', id],
    queryFn: () => getOfertaLaboral(id!),
    enabled: !!id,
  });

  const { data: otrasOfertas } = useQuery({
    queryKey: ['otras-ofertas'],
    queryFn: () => getOfertasLaborales({ limit: '3' }),
    enabled: !!oferta,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0f041e] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-congress-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !oferta) {
    return (
      <div className="min-h-screen bg-[#0f041e] text-white flex flex-col items-center justify-center p-4">
        <h1 className="text-2xl font-bold mb-4">Oferta no encontrada</h1>
        <Link to="/bolsa-de-trabajo">
          <Button variant="outline">Volver a la Bolsa</Button>
        </Link>
      </div>
    );
  }

  // Schema.org JobPosting JSON-LD
  const jsonLd = {
    "@context": "https://schema.org/",
    "@type": "JobPosting",
    "title": oferta.titulo_puesto,
    "description": oferta.descripcion,
    "datePosted": oferta.fecha_creacion,
    "validThrough": oferta.fecha_expiracion,
    "employmentType": oferta.modalidad === 'REMOTO' ? 'FULL_TIME' : 'OTHER',
    "hiringOrganization": {
      "@type": "Organization",
      "name": oferta.empresa_nombre,
      "logo": oferta.empresa_logo || "https://www.congresologistica.unab.edu.ar/logo.png"
    },
    "jobLocation": {
      "@type": "Place",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": oferta.ubicacion,
        "addressCountry": "AR"
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#0f041e] text-white pb-20 pt-8 px-4 sm:px-6 relative">
      <Helmet>
        <title>{oferta.titulo_puesto} | Bolsa de Trabajo Congreso UNAB</title>
        <meta name="description" content={oferta.descripcion.substring(0, 160)} />
        <meta property="og:title" content={`${oferta.titulo_puesto} - ${oferta.empresa_nombre}`} />
        <meta property="og:description" content={oferta.descripcion.substring(0, 160)} />
        <meta property="og:type" content="website" />
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      </Helmet>

      {/* Hero Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-congress-cyan/5 blur-[150px] rounded-full" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#9b6dd7]/5 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Navigation / Breadcrumbs */}
        <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8 overflow-x-auto whitespace-nowrap pb-2">
          <Link to="/" className="hover:text-white transition-colors">Inicio</Link>
          <ChevronRight size={14} />
          <Link to="/bolsa-de-trabajo" className="hover:text-white transition-colors">Bolsa de Trabajo</Link>
          <ChevronRight size={14} />
          <span className="text-congress-cyan font-medium truncate">{oferta.titulo_puesto}</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[32px] p-8 md:p-10 shadow-2xl"
            >
              <div className="flex flex-col md:flex-row justify-between items-start gap-6 mb-10">
                <div className="space-y-4">
                  <Badge className="bg-congress-cyan/20 text-congress-cyan border-congress-cyan/20 px-3 py-1">
                    {oferta.modalidad}
                  </Badge>
                  <h1 className="text-3xl md:text-5xl font-black">{oferta.titulo_puesto}</h1>
                  <div className="flex flex-wrap items-center gap-6 text-slate-400">
                    <div className="flex items-center gap-2">
                      <Building2 size={18} className="text-congress-cyan" />
                      <span className="font-bold text-white/90">{oferta.empresa_nombre}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin size={18} />
                      <span>{oferta.ubicacion}</span>
                    </div>
                  </div>
                </div>
                {oferta.empresa_logo && (
                  <div className="w-24 h-24 bg-white/5 rounded-2xl flex items-center justify-center p-2 border border-white/10 shrink-0">
                    <img src={oferta.empresa_logo} alt={oferta.empresa_nombre} className="max-w-full max-h-full object-contain" />
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 p-6 bg-white/[0.02] rounded-2xl border border-white/5">
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Publicado</span>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock size={14} className="text-congress-cyan" />
                    {format(new Date(oferta.fecha_creacion), 'dd MMM', { locale: es })}
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Expiración</span>
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar size={14} className="text-congress-cyan" />
                    {oferta.fecha_expiracion ? format(new Date(oferta.fecha_expiracion), 'dd MMM', { locale: es }) : 'Abierta'}
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Modalidad</span>
                  <div className="flex items-center gap-2 text-sm text-congress-cyan capitalize font-medium">
                    <Globe size={14} />
                    {oferta.modalidad.toLowerCase()}
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">ID Vacante</span>
                  <div className="flex items-center gap-2 text-sm text-slate-300">
                    #{oferta.id}
                  </div>
                </div>
              </div>

              <div className="prose prose-invert max-w-none space-y-10">
                <section>
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <div className="w-1.5 h-6 bg-congress-cyan rounded-full" />
                    Descripción del Puesto
                  </h2>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {oferta.descripcion}
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <div className="w-1.5 h-6 bg-[#9b6dd7] rounded-full" />
                    Requisitos
                  </h2>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {oferta.requisitos}
                  </p>
                </section>
              </div>

              <div className="mt-12 pt-8 border-t border-white/10 flex flex-col sm:flex-row gap-6 items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-bold text-slate-400">¿Te interesa esta posición?</p>
                  <p className="text-xs text-slate-500 italic">Sigue las instrucciones del canal de postulación.</p>
                </div>
                <a 
                  href={oferta.canal_postulacion.startsWith('http') ? oferta.canal_postulacion : `mailto:${oferta.canal_postulacion}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto"
                >
                  <Button className="w-full sm:w-auto bg-congress-cyan hover:bg-congress-cyan/80 text-congress-blue font-black px-12 py-7 rounded-2xl shadow-[0_0_30px_rgba(34,211,238,0.2)] transition-all transform hover:scale-[1.03]">
                    <Send size={20} className="mr-2" />
                    POSTULARME AHORA
                  </Button>
                </a>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Share Card */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[32px] p-6">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <Share2 size={18} className="text-congress-cyan" />
                Compartir vacante
              </h3>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1 border-white/10 hover:bg-white/5 rounded-xl text-xs h-10" onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  alert("Link copiado al portapapeles");
                }}>
                  Copiar Link
                </Button>
              </div>
            </div>

            {/* Other Offers Card */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[32px] p-6">
              <h3 className="font-bold mb-6 flex items-center gap-2">
                <Briefcase size={18} className="text-congress-cyan" />
                Otras Vacantes
              </h3>
              <div className="space-y-6">
                {otrasOfertas?.filter((o: any) => o.id !== oferta.id).slice(0, 3).map((otra: any) => (
                  <Link key={otra.id} to={`/bolsa-de-trabajo/${otra.id}`} className="group block">
                    <div className="space-y-2">
                      <h4 className="text-sm font-bold group-hover:text-congress-cyan transition-colors line-clamp-1">{otra.titulo_puesto}</h4>
                      <p className="text-xs text-slate-500 flex items-center gap-1">
                        <Building2 size={12} />
                        {otra.empresa_nombre}
                      </p>
                      <Badge variant="secondary" className="text-[10px] bg-white/5 hover:bg-white/10">
                        {otra.modalidad}
                      </Badge>
                    </div>
                  </Link>
                ))}
                {(!otrasOfertas || otrasOfertas.length <= 1) && (
                  <p className="text-xs text-slate-500 italic">No hay otras vacantes recientes.</p>
                )}
                <Link to="/bolsa-de-trabajo">
                  <Button variant="link" className="text-congress-cyan p-0 h-auto text-xs font-bold mt-4">
                    Ver todas las ofertas
                    <ChevronRight size={14} className="ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
