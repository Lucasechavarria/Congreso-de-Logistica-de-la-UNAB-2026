import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { 
  Building2, 
  MapPin, 
  Briefcase, 
  Calendar, 
  ArrowLeft, 
  ChevronRight,
  Clock,
  Globe,
  Share2,
  Facebook,
  Twitter,
  Linkedin,
  Copy,
  Send,
  FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { motion } from "framer-motion";
import { Helmet } from "react-helmet-async";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { getOfertaLaboral } from "@/lib/api";
import PostulacionModal from "@/components/PostulacionModal";
import { useToast } from "@/components/ui/use-toast";

// Icons personalizados para marcas
const WhatsAppIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" className="text-[#25D366]">
    <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766 0-3.187-2.59-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.747-2.874-2.512-2.96-2.626-.087-.115-.708-.941-.708-1.793 0-.852.448-1.271.607-1.441.159-.171.348-.215.465-.215.117 0 .234 0 .334.005.106.004.247-.04.386.299.144.348.491 1.2.533 1.287.043.087.072.188.014.304-.058.117-.087.188-.174.289l-.26.304c-.087.101-.177.211-.077.382.1.171.444.733.953 1.186.656.584 1.209.765 1.382.852.174.087.275.072.376-.043.102-.115.434-.506.549-.68.116-.174.232-.144.39-.087.158.058 1.002.472 1.175.558.173.087.289.129.333.202.043.073.043.419-.101.824z" />
    <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 21.162c-1.633 0-3.21-.433-4.58-1.252l-4.522 1.188 1.209-4.413c-.9-1.425-1.375-3.074-1.375-4.757 0-4.908 3.992-8.9 8.9-8.9 4.907 0 8.899 3.992 8.899 8.9 0 4.908-3.992 8.9-8.899 8.9z" />
  </svg>
);

const TelegramIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" className="text-[#0088cc]">
    <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm5.891 7.021l-2.32 10.941c-.171.757-.618.944-1.251.588l-3.53-2.601-1.703 1.638s-.225.215-.438.215c-.21 0-.175-.11-.175-.11l.653-5.312 9.68-8.74c.421-.375-.091-.584-.653-.213l-11.97 7.54-5.155-1.611s-.822-.26-.816-.761c.006-.5.733-.761.733-.761l20.015-7.712s.932-.346 1.171.22c.11.26.04.5.04.5z" />
  </svg>
);

export default function DetalleOferta() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();

  const { data: oferta, isLoading, error } = useQuery({
    queryKey: ['oferta', id],
    queryFn: () => getOfertaLaboral(id!),
    enabled: !!id,
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

  const shareUrl = window.location.href;
  const shareText = `¡Mira esta oportunidad laboral: ${oferta.titulo_puesto} en ${oferta.empresa_nombre}!`;

  const shareOptions = [
    { name: 'WhatsApp', icon: <WhatsAppIcon />, url: `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + shareUrl)}` },
    { name: 'Telegram', icon: <TelegramIcon />, url: `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}` },
    { name: 'LinkedIn', icon: <Linkedin className="text-blue-700 h-5 w-5" />, url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}` },
    { name: 'Twitter / X', icon: <Twitter className="text-slate-200 h-5 w-5" />, url: `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}` },
  ];

  return (
    <div className="min-h-screen bg-[#0f041e] text-white pb-20 pt-8 px-4 sm:px-6 relative">
      <Helmet>
        <title>{oferta.titulo_puesto} | Bolsa de Trabajo Congreso UNAB</title>
        <meta name="description" content={oferta.descripcion.substring(0, 160)} />
      </Helmet>

      {/* Hero Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-congress-cyan/5 blur-[150px] rounded-full" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#9b6dd7]/5 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Navigation / Header */}
        <div className="flex items-center justify-between mb-12">
          <Link 
            to="/bolsa-de-trabajo" 
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group text-sm font-bold uppercase tracking-widest"
          >
            <ArrowLeft size={18} className="transition-transform group-hover:-translate-x-1" />
            Ver todas las ofertas
          </Link>
          
          <nav className="hidden sm:flex items-center gap-2 text-xs text-slate-500 overflow-x-auto whitespace-nowrap">
            <Link to="/" className="hover:text-white transition-colors">Inicio</Link>
            <ChevronRight size={12} />
            <span className="text-congress-cyan font-medium truncate max-w-[150px]">{oferta.titulo_puesto}</span>
          </nav>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[40px] p-8 md:p-12 shadow-2xl relative overflow-hidden"
        >
          {/* Decorative accents */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-congress-cyan via-[#9b6dd7] to-congress-cyan opacity-50" />
          
          {/* Share Icon Top Right */}
          <div className="absolute top-8 right-8 z-20">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-all text-congress-cyan shadow-lg">
                  <Share2 size={18} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-[#1a0a2e]/95 backdrop-blur-xl border-white/10 p-3 rounded-2xl min-w-[140px]">
                <div className="grid grid-cols-2 gap-2">
                  {shareOptions.map((opt) => (
                    <DropdownMenuItem 
                      key={opt.name}
                      asChild
                      className="focus:bg-white/10 rounded-xl p-3 cursor-pointer flex justify-center items-center"
                    >
                      <a href={opt.url} target="_blank" rel="noopener noreferrer" title={opt.name}>
                        {opt.icon}
                      </a>
                    </DropdownMenuItem>
                  ))}
                </div>
                <div className="my-2 border-t border-white/5 w-full" />
                <DropdownMenuItem 
                  className="focus:bg-white/10 rounded-xl p-3 cursor-pointer flex items-center justify-center gap-2 text-xs font-bold text-slate-400"
                  onClick={() => {
                    navigator.clipboard.writeText(shareUrl);
                    toast({ title: "Link copiado" });
                  }}
                >
                  <Copy size={16} className="text-congress-cyan" />
                  COPIAR
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-12">
            <div className="space-y-6 max-w-[80%]">
              <Badge className="bg-congress-cyan/20 text-congress-cyan border-congress-cyan/20 px-4 py-1 text-xs font-bold tracking-widest uppercase">
                {oferta.modalidad}
              </Badge>
              <h1 className="text-4xl md:text-6xl font-black leading-tight tracking-tight">{oferta.titulo_puesto}</h1>
              <div className="flex flex-wrap items-center gap-8 text-slate-400">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-congress-cyan/10 flex items-center justify-center border border-congress-cyan/20">
                    <Building2 size={20} className="text-congress-cyan" />
                  </div>
                  <span className="font-black text-xl text-white/90">{oferta.empresa_nombre}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin size={18} className="text-slate-500" />
                  <span className="text-lg">{oferta.ubicacion}</span>
                </div>
              </div>
            </div>
            {oferta.empresa_logo && (
              <div className="w-32 h-32 bg-white/5 rounded-3xl flex items-center justify-center p-4 border border-white/10 shrink-0 shadow-inner">
                <img src={oferta.empresa_logo} alt={oferta.empresa_nombre} className="max-w-full max-h-full object-contain" />
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16 p-8 bg-white/[0.03] rounded-3xl border border-white/5">
            <div className="space-y-2">
              <span className="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-black">Publicado</span>
              <div className="flex items-center gap-2 text-base font-medium">
                <Clock size={16} className="text-congress-cyan" />
                {format(new Date(oferta.fecha_creacion), 'dd MMM yyyy', { locale: es })}
              </div>
            </div>
            <div className="space-y-2">
              <span className="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-black">Expiración</span>
              <div className="flex items-center gap-2 text-base font-medium">
                <Calendar size={16} className="text-[#9b6dd7]" />
                {oferta.fecha_expiracion ? format(new Date(oferta.fecha_expiracion), 'dd MMM yyyy', { locale: es }) : 'Abierta'}
              </div>
            </div>
            <div className="space-y-2">
              <span className="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-black">Modalidad</span>
              <div className="flex items-center gap-2 text-base font-bold text-congress-cyan uppercase">
                <Globe size={16} />
                {oferta.modalidad}
              </div>
            </div>
            <div className="space-y-2">
              <span className="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-black">Referencia</span>
              <div className="flex items-center gap-2 text-base font-mono text-slate-400">
                #{oferta.id.toString().padStart(4, '0')}
              </div>
            </div>
          </div>

          <div className="prose prose-invert max-w-none space-y-16 mb-16">
            <section className="relative">
              <div className="absolute -left-12 top-0 bottom-0 w-1 bg-gradient-to-b from-congress-cyan to-transparent rounded-full opacity-20 hidden md:block" />
              <h2 className="text-2xl font-black mb-6 flex items-center gap-3 text-congress-cyan uppercase tracking-wider">
                <Briefcase size={24} />
                Descripción del Puesto
              </h2>
              <p className="text-slate-300 text-lg leading-relaxed whitespace-pre-wrap">
                {oferta.descripcion}
              </p>
            </section>

            <section className="relative">
              <div className="absolute -left-12 top-0 bottom-0 w-1 bg-gradient-to-b from-[#9b6dd7] to-transparent rounded-full opacity-20 hidden md:block" />
              <h2 className="text-2xl font-black mb-6 flex items-center gap-3 text-[#9b6dd7] uppercase tracking-wider">
                <FileText size={24} />
                Requisitos
              </h2>
              <p className="text-slate-300 text-lg leading-relaxed whitespace-pre-wrap">
                {oferta.requisitos}
              </p>
            </section>
          </div>

          <div className="pt-12 border-t border-white/10 flex flex-col items-center text-center space-y-8">
            <div className="space-y-3">
              <h3 className="text-3xl font-black text-white">¿Estás listo para el siguiente paso?</h3>
              <p className="text-slate-400 text-lg max-w-xl mx-auto">
                No pierdas la oportunidad de formar parte de una de las empresas líderes en el sector.
              </p>
            </div>
            
            <PostulacionModal 
              ofertaId={id!} 
              ofertaTitulo={oferta.titulo_puesto} 
              empresaNombre={oferta.empresa_nombre}
            >
              <Button size="lg" className="bg-congress-cyan hover:bg-congress-cyan/80 text-congress-blue font-black px-16 py-10 text-xl rounded-[24px] shadow-[0_20px_40px_rgba(34,211,238,0.3)] transition-all transform hover:scale-[1.05] active:scale-[0.98] group">
                <Send size={24} className="mr-3 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                POSTULARME AHORA
              </Button>
            </PostulacionModal>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
