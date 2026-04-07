import { useState } from "react";
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
  CheckCircle2
} from "lucide-react";
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

const postulacionSchema = z.object({
  nombre_completo: z.string().min(3, "Nombre muy corto"),
  email: z.string().email("Email inválido"),
  telefono: z.string().min(8, "Teléfono inválido"),
  mensaje: z.string().optional(),
  cv: z.any().refine((file) => file && file.length > 0, "El CV es obligatorio"),
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
    defaultValues: {
      nombre_completo: "",
      email: "",
      telefono: "",
      mensaje: "",
    },
  });

  const onSubmit = async (values: PostulacionValues) => {
    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("oferta", ofertaId.toString());
      formData.append("nombre_completo", values.nombre_completo);
      formData.append("email", values.email);
      formData.append("telefono", values.telefono);
      if (values.mensaje) formData.append("mensaje", values.mensaje);
      formData.append("cv", values.cv[0]);

      await postularCandidato(formData);
      setIsSuccess(true);
      toast({
        title: "¡Postulación enviada!",
        description: "Recibirás un email de confirmación a la brevedad.",
      });
      setTimeout(() => {
        setIsOpen(false);
        setIsSuccess(false);
        form.reset();
      }, 3000);
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "No se pudo enviar la postulación.",
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
