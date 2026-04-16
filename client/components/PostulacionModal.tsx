import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { 
  Briefcase, 
  Send,
  User,
  Mail,
  Phone,
  FileText,
  CheckCircle2,
  GraduationCap,
  School
} from "lucide-react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger,
  DialogDescription 
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { motion, AnimatePresence } from "framer-motion";
import { postularCandidato } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_FILE_TYPES = ["application/pdf"];

const postulacionSchema = z.object({
  nombre_completo: z.string().min(3, "Nombre muy corto"),
  email: z.string().email("Email inválido"),
  telefono: z.string().min(8, "Teléfono inválido"),
  mensaje: z.string().optional(),
  cv: z.any()
    .refine((files) => files && files.length > 0, "El CV es obligatorio")
    .refine((files) => !files || files.length === 0 || files[0].size <= MAX_FILE_SIZE, `El archivo es demasiado grande (máx. 5MB). Por favor use un archivo más ligero o envíelo por email a congresologisticaytransporte@unab.edu.ar.`)
    .refine((files) => !files || files.length === 0 || ACCEPTED_FILE_TYPES.includes(files[0].type), "Solo se aceptan archivos PDF"),
  es_estudiante: z.enum(["si", "no"], {
    required_error: "Debes seleccionar una opción",
  }),
  institucion: z.string().optional(),
}).refine((data) => {
  if (data.es_estudiante === "si" && (!data.institucion || data.institucion.trim() === "")) {
    return false;
  }
  return true;
}, {
  message: "Debes especificar la institución",
  path: ["institucion"],
});

type PostulacionValues = z.infer<typeof postulacionSchema>;

interface PostulacionModalProps {
  ofertaId: number | string;
  ofertaTitulo: string;
  empresaNombre: string;
  children: React.ReactNode;
}

export default function PostulacionModal({ ofertaId, ofertaTitulo, empresaNombre, children }: PostulacionModalProps) {
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const form = useForm<PostulacionValues>({
    resolver: zodResolver(postulacionSchema),
    mode: "onChange",
    defaultValues: {
      nombre_completo: "",
      email: "",
      telefono: "",
      mensaje: "",
      es_estudiante: undefined,
      institucion: "",
    },
  });

  const { errors } = form.formState;

  // Alerta inmediata para el CV
  React.useEffect(() => {
    if (errors.cv && errors.cv.message) {
      toast({
        title: "⚠️ Archivo no permitido",
        description: String(errors.cv.message),
        variant: "destructive",
      });
    }
  }, [errors.cv, toast]);

  const esEstudiante = form.watch("es_estudiante");

  const onSubmit = async (values: PostulacionValues) => {
    setIsSubmitting(true);
    console.log('[Postulación] Iniciando envío...', values);
    
    // Controlador de aborto para implementar un timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 segundos timeout

    try {
      const formData = new FormData();
      formData.append("oferta", ofertaId.toString());
      formData.append("nombre_completo", values.nombre_completo);
      formData.append("email", values.email);
      formData.append("telefono", values.telefono);
      formData.append("es_estudiante", values.es_estudiante === "si" ? "true" : "false");
      
      if (values.es_estudiante === "si" && values.institucion) {
        formData.append("institucion", values.institucion);
      }
      
      if (values.mensaje) formData.append("mensaje", values.mensaje);
      
      if (values.cv && values.cv.length > 0) {
        formData.append("cv", values.cv[0]);
      } else {
        throw new Error("El archivo CV es obligatorio");
      }

      console.log('[Postulación] Enviando a API...');
      
      // Pasar el signal al fetch no es posible con mi wrapper actual, 
      // pero el wrapper parsea la respuesta y arroja error si no es OK.
      const response = await postularCandidato(formData);
      clearTimeout(timeoutId);
      
      console.log('[Postulación] Éxito:', response);
      setIsSuccess(true);
      
      toast({
        title: "¡Postulación enviada!",
        description: "Gracias por tu interés. Hemos recibido tus datos.",
      });

      setTimeout(() => {
        setIsOpen(false);
        setIsSuccess(false);
        form.reset();
      }, 4000);
      
    } catch (err: any) {
      console.error('[Postulación] Fallo:', err);
      clearTimeout(timeoutId);
      
      let errorMsg = "No se pudo procesar la solicitud.";
      if (err.name === 'AbortError') {
        errorMsg = "La conexión tardó demasiado. Revisa tu internet o intenta de nuevo.";
      } else {
        errorMsg = err.message || errorMsg;
      }

      toast({
        variant: "destructive",
        title: "Error al postular",
        description: errorMsg,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] bg-[#1a0a2e] border-white/10 text-white p-0 overflow-hidden rounded-[32px] overflow-y-auto max-h-[90vh]">
        <DialogHeader className="p-8 bg-white/5 border-b border-white/5 text-left">
          <DialogTitle className="text-2xl font-black flex items-center gap-3">
            <Briefcase className="text-congress-cyan" />
            Postulación Rápida
          </DialogTitle>
          <DialogDescription className="text-slate-400 pt-2">
            Te estás postulando para <strong>{ofertaTitulo}</strong> en <strong>{empresaNombre}</strong>.
          </DialogDescription>
        </DialogHeader>

        <AnimatePresence mode="wait">
          {isSuccess ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="p-12 text-center"
            >
              <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-10 h-10 text-green-500" />
              </div>
              <h3 className="text-2xl font-bold mb-2">¡Todo listo!</h3>
              <p className="text-slate-400">Tu postulación ha sido enviada con éxito.</p>
            </motion.div>
          ) : (
            <div className="p-8">
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                  <FormField
                    control={form.control}
                    name="nombre_completo"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nombre Completo</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                            <Input {...field} placeholder="Juan Pérez" className="pl-10 bg-white/5 border-white/10 rounded-xl" />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <div className="relative">
                              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                              <Input {...field} placeholder="juan@email.com" className="pl-10 bg-white/5 border-white/10 rounded-xl" />
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="telefono"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Teléfono</FormLabel>
                          <FormControl>
                            <div className="relative">
                              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                              <Input {...field} placeholder="11 2345 6789" className="pl-10 bg-white/5 border-white/10 rounded-xl" />
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <FormField
                    control={form.control}
                    name="cv"
                    render={({ field: { value, onChange, ...fieldProps } }) => (
                      <FormItem>
                        <FormLabel>Adjuntar Curriculum (PDF)</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <FileText className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                            <Input 
                              {...fieldProps}
                              type="file" 
                              accept=".pdf"
                              onChange={(e) => onChange(e.target.files)}
                              className="pl-10 bg-white/5 border-white/10 file:bg-transparent file:text-congress-cyan file:text-xs file:border-0 hover:border-congress-cyan/50 transition-colors rounded-xl" 
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="space-y-4 py-2 border-y border-white/5">
                    <FormField
                      control={form.control}
                      name="es_estudiante"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <div className="flex items-center gap-2">
                            <GraduationCap className="h-4 w-4 text-congress-cyan" />
                            <FormLabel className="text-base font-bold">¿Sos estudiante?</FormLabel>
                          </div>
                          <FormControl>
                            <RadioGroup
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                              className="flex gap-6"
                            >
                              <div className="flex items-center space-x-2 cursor-pointer group">
                                <RadioGroupItem value="si" id="r1" className="border-white/20 text-congress-cyan" />
                                <Label htmlFor="r1" className="cursor-pointer group-hover:text-congress-cyan transition-colors">Sí</Label>
                              </div>
                              <div className="flex items-center space-x-2 cursor-pointer group">
                                <RadioGroupItem value="no" id="r2" className="border-white/20 text-congress-cyan" />
                                <Label htmlFor="r2" className="cursor-pointer group-hover:text-congress-cyan transition-colors">No</Label>
                              </div>
                            </RadioGroup>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <AnimatePresence>
                      {esEstudiante === "si" && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="overflow-hidden"
                        >
                          <FormField
                            control={form.control}
                            name="institucion"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="flex items-center gap-2">
                                  <School className="h-4 w-4 text-congress-cyan" />
                                  ¿De qué institución?
                                </FormLabel>
                                <FormControl>
                                  <Input {...field} placeholder="Nombre de la institución..." className="bg-white/5 border-white/10 rounded-xl" />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  <FormField
                    control={form.control}
                    name="mensaje"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Breve Mensaje (Opcional)</FormLabel>
                        <FormControl>
                          <Textarea {...field} placeholder="Cuéntanos brevemente sobre ti..." className="bg-white/5 border-white/10 resize-none h-24 rounded-xl" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button 
                    type="submit" 
                    disabled={isSubmitting}
                    className="w-full bg-congress-cyan hover:bg-congress-cyan/90 text-congress-blue font-bold py-7 rounded-2xl shadow-lg transition-all hover:scale-[1.02]"
                  >
                    {isSubmitting ? "Enviando..." : "ENVIAR POSTULACIÓN"}
                  </Button>
                </form>
              </Form>
            </div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
}
