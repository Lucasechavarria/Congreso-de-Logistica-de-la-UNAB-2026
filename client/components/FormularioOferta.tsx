import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { 
  Building2, 
  Mail, 
  MapPin, 
  Briefcase, 
  Send, 
  CheckCircle2, 
  AlertCircle,
  Hash,
  Link as LinkIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { postularOfertaLaboral } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

const formSchema = z.object({
  nombre_empresa: z.string().min(2, "El nombre de la empresa es obligatorio"),
  cuit: z.string().optional().nullable(),
  email_contacto: z.string().email("Ingrese un email válido"),
  titulo_puesto: z.string().min(5, "El título del puesto debe ser más descriptivo"),
  descripcion: z.string().min(20, "Proporcione una descripción detallada"),
  requisitos: z.string().min(10, "Los requisitos son obligatorios"),
  modalidad: z.enum(["PRESENCIAL", "REMOTO", "HIBRIDO"], {
    required_error: "Seleccione una modalidad",
  }),
  ubicacion: z.string().min(3, "La ubicación es obligatoria"),
  canal_postulacion: z.string().min(3, "Indique cómo deben postularse (Email, Link, etc.)"),
});

type FormValues = z.infer<typeof formSchema>;

export default function FormularioOferta() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      nombre_empresa: "",
      cuit: "",
      email_contacto: "",
      titulo_puesto: "",
      descripcion: "",
      requisitos: "",
      modalidad: "PRESENCIAL",
      ubicacion: "",
      canal_postulacion: "",
    },
  });

  const onSubmit = async (values: FormValues) => {
    setIsSubmitting(true);
    setError(null);
    try {
      await postularOfertaLaboral(values);
      setIsSuccess(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Ocurrió un error al enviar la propuesta. Reintente más tarde.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSuccess) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[40px] p-12 text-center shadow-2xl"
      >
        <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-8">
          <CheckCircle2 className="w-12 h-12 text-green-500" />
        </div>
        <h2 className="text-3xl font-black mb-4">¡Propuesta Recibida!</h2>
        <p className="text-slate-400 text-lg max-w-md mx-auto mb-10">
          Tu oferta laboral ha sido enviada con éxito. Nuestro equipo la revisará y se pondrá en contacto contigo a la brevedad para su aprobación.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            onClick={() => window.location.href = "/bolsa-de-trabajo"}
            className="bg-congress-blue hover:bg-congress-blue/80 text-white px-8 py-6 rounded-2xl font-bold"
          >
            Volver a la Bolsa
          </Button>
          <Button 
            variant="outline"
            onClick={() => {
              setIsSuccess(false);
              form.reset();
            }}
            className="border-congress-cyan/30 text-congress-cyan hover:bg-congress-cyan/10 px-8 py-6 rounded-2xl font-bold transition-all"
          >
            Publicar otra vacante
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-[40px] p-8 md:p-12 shadow-2xl relative overflow-hidden">
      {/* Decorative pulse */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-congress-cyan/5 blur-[100px] rounded-full pointer-events-none" />
      
      <div className="mb-10">
        <h2 className="text-3xl font-black mb-2 flex items-center gap-3">
          <Briefcase className="text-congress-cyan" />
          Nueva Vacante
        </h2>
        <p className="text-slate-400">
          Complete los detalles de la posición para que podamos publicarla en nuestra plataforma.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/20 p-4 rounded-2xl flex items-center gap-3 text-red-500 text-sm"
            >
              <AlertCircle size={20} />
              {error}
            </motion.div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Empresa Info */}
            <div className="space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-widest text-[#9b6dd7] border-b border-white/5 pb-2">
                Datos de la Empresa
              </h3>
              
              <FormField
                control={form.control}
                name="nombre_empresa"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Nombre de la Empresa</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                        <Input placeholder="Ej: Tech Logistics S.A." {...field} className="pl-12 bg-white/[0.03] border-white/10 rounded-xl focus:ring-congress-cyan/40" />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="cuit"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">CUIT (Opcional)</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Hash className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                          <Input placeholder="30-XXXXXXXX-X" {...field} value={field.value || ""} className="pl-12 bg-white/[0.03] border-white/10 rounded-xl" />
                        </div>
                      </FormControl>
                      <FormDescription className="text-[10px]">Ayuda a vincular su empresa automáticamente.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="email_contacto"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Email de Contacto</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                          <Input placeholder="rrhh@empresa.com" {...field} className="pl-12 bg-white/[0.03] border-white/10 rounded-xl" />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Puesto Info */}
            <div className="space-y-6">
              <h3 className="text-sm font-bold uppercase tracking-widest text-congress-cyan border-b border-white/5 pb-2">
                Detalles del Puesto
              </h3>

              <FormField
                control={form.control}
                name="titulo_puesto"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Título del Puesto</FormLabel>
                    <FormControl>
                      <Input placeholder="Ej: Analista de Logística Sr." {...field} className="bg-white/[0.03] border-white/10 rounded-xl" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="modalidad"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Modalidad</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="bg-white/[0.03] border-white/10 rounded-xl">
                            <SelectValue placeholder="Seleccione" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="bg-[#1a0a2e] border-white/10 text-white">
                          <SelectItem value="PRESENCIAL">Presencial</SelectItem>
                          <SelectItem value="REMOTO">Remoto</SelectItem>
                          <SelectItem value="HIBRIDO">Híbrido</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="ubicacion"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Ubicación</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                          <Input placeholder="Ej: Burzaco, GBA" {...field} className="pl-12 bg-white/[0.03] border-white/10 rounded-xl" />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
          </div>

          <div className="space-y-6 bg-white/[0.01] p-6 rounded-3xl border border-white/5">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 border-b border-white/5 pb-2">
              Contenido de la Propuesta
            </h3>
            
            <FormField
              control={form.control}
              name="descripcion"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Descripción del Puesto</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Describa las tareas y responsabilidades..." 
                      className="min-h-[120px] bg-white/[0.03] border-white/10 rounded-xl resize-none" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="requisitos"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Requisitos</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Experiencia, estudios, habilidades técnicas..." 
                      className="min-h-[100px] bg-white/[0.03] border-white/10 rounded-xl resize-none" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="canal_postulacion"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Canal de Postulación</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                      <Input placeholder="Ej: Enviar CV a rrhh@tech.com o link a LinkedIn" {...field} className="pl-12 bg-white/[0.03] border-white/10 rounded-xl" />
                    </div>
                  </FormControl>
                  <FormDescription className="text-[11px] text-slate-500">
                    Instrucciones claras para los interesados en aplicar.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-white/5">
            <p className="text-xs text-slate-500 italic">
              Al enviar, acepta que la propuesta será revisada por el equipo del Congreso antes de su publicación.
            </p>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="bg-congress-cyan hover:bg-congress-cyan/80 text-congress-blue font-black px-10 py-6 rounded-2xl shadow-[0_0_20px_rgba(34,211,238,0.2)] transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              {isSubmitting ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-congress-blue border-t-transparent rounded-full animate-spin" />
                  Enviando...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Send size={18} />
                  Enviar Propuesta
                </div>
              )}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
