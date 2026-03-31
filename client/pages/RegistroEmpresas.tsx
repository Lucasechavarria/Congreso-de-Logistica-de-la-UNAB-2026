import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  FormInput,
  FormButton,
  FormCard,
  FormSection,
  FormFileInput,
  FormTextArea,
  FormCheckbox
} from "@/components/ui/modern-form";
import {
  Building2,
  Mail,
  Phone,
  User,
  CheckCircle,
  Briefcase,
  Globe
} from "lucide-react";
import { registrarEmpresa, verificarEmpresa } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { TermsAndConditionsModal } from "@/components/TermsAndConditionsModal";

const companyRegistrationSchema = z.object({
  companyName: z.string().min(1, "El nombre de la empresa es requerido"),
  companyEmail: z.string().email("Debe ser un correo electrónico válido"),
  contactPersonName: z.string().min(1, "El nombre de la persona de contacto es requerido"),
  contactPersonEmail: z.string().email("Debe ser un correo electrónico válido"),
  contactPersonPhone: z.string().min(1, "El teléfono de la persona de contacto es requerido"),
  cargoContacto: z.string().min(1, "El cargo en la empresa es requerido"),
  logo: z.any().optional(),
  participationOptions: z.array(z.string()).optional(),
  companyDescription: z.string().optional(),
  website: z.string().optional(),

  // Campos Logísticos
  participoEdicionAnterior: z.boolean().default(false),
  rubroLogistico: z.string().min(1, "El rubro de la empresa es requerido"),
  requiereElectricidad: z.boolean().default(false),
  computadoraOPantalla: z.boolean().default(false),
  tipoMobiliario: z.enum(["Mesa y dos sillas", "Solo mesa", "Solo dos sillas", "Ninguno"], {
    required_error: "Debe seleccionar una opción de mobiliario"
  }),
  gazeboPropio: z.boolean().default(false),
  estructuraAdicional: z.string().optional(),
  accionesStand: z.string().optional(),

  aceptaTyC: z.literal(true, {
    errorMap: () => ({ message: "Debes aceptar las Bases y Condiciones para continuar" }),
  }),
});

type CompanyRegistrationFormData = z.infer<typeof companyRegistrationSchema>;

const RegistroEmpresas: React.FC = () => {
  const { toast } = useToast();
  const [showModal, setShowModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [participationType, setParticipationType] = useState<string>("");
  const [otraParticipacion, setOtraParticipacion] = useState("");
  const [isCheckingCRM, setIsCheckingCRM] = useState(false);
  const [crmMode, setCrmMode] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setValue,
    watch,
  } = useForm<CompanyRegistrationFormData>({
    resolver: zodResolver(companyRegistrationSchema),
  });

  const watchedEmail = watch("companyEmail");

  const participationOptions = [
    { id: "stand", label: "Stand/Exhibición", description: "Espacio para mostrar productos y servicios" },
    { id: "sponsorship", label: "Patrocinio", description: "Apoyo financiero con beneficios de marca" },
    { id: "speaking", label: "Ponencia/Charla", description: "Presentación técnica o caso de éxito" },
    { id: "visitor", label: "Visitante", description: "Participación como asistente al evento" },
    { id: "otra", label: "Otra (especificar)", description: "Otra modalidad, escribir abajo" },
  ];

  React.useEffect(() => {
    const checkCRM = async () => {
      if (watchedEmail && watchedEmail.includes('@') && watchedEmail.includes('.')) {
        setIsCheckingCRM(true);
        try {
          const response = await verificarEmpresa(watchedEmail);
          if (response && response.status === 'success' && response.empresa) {
            const e = response.empresa;

            reset({
              companyName: e.nombre_empresa || "",
              companyEmail: e.email_empresa || watchedEmail,
              website: e.sitio_web || "",
              companyDescription: e.descripcion || "",
              contactPersonName: e.nombre_contacto || "",
              contactPersonEmail: e.email_contacto || "",
              contactPersonPhone: e.celular_contacto || "",
              cargoContacto: e.cargo_contacto || "",
              participoEdicionAnterior: e.participo_edicion_anterior || false,
              rubroLogistico: e.rubro_logistico || "",
              requiereElectricidad: e.requiere_electricidad || false,
              computadoraOPantalla: e.computadora_o_pantalla || false,
              tipoMobiliario: e.tipo_mobiliario || "Ninguno",
              gazeboPropio: e.gazebo_propio || false,
              estructuraAdicional: e.estructura_adicional || "",
              accionesStand: e.acciones_stand || "",
              aceptaTyC: true
            });

            if (e.participacion_opciones) {
              try {
                const parsedOpt = Array.isArray(e.participacion_opciones)
                  ? e.participacion_opciones[0]
                  : JSON.parse(e.participacion_opciones)[0];
                if (parsedOpt) {
                  setParticipationType(parsedOpt);
                }
              } catch { }
            }
            if (e.participacion_otra) {
              setOtraParticipacion(e.participacion_otra);
            }

            setCrmMode(true);
            toast({
              title: "✅ Perfil Encontrado",
              description: "Hemos cargado los datos de la empresa de ediciones anteriores.",
              variant: "default",
            });
          }
        } catch (error) {
          setCrmMode(false);
        } finally {
          setIsCheckingCRM(false);
        }
      } else {
        setCrmMode(false);
      }
    };

    const timeoutId = setTimeout(() => {
      checkCRM();
    }, 1000);

    return () => clearTimeout(timeoutId);
  }, [watchedEmail, reset, toast]);

  const onSubmit = async (data: CompanyRegistrationFormData) => {
    try {
      const formData = new FormData();
      formData.append("nombre_empresa", data.companyName);
      formData.append("email_empresa", data.companyEmail);
      formData.append("sitio_web", data.website || "");
      formData.append("descripcion", data.companyDescription || "");
      formData.append("nombre_contacto", data.contactPersonName);
      formData.append("email_contacto", data.contactPersonEmail);
      formData.append("celular_contacto", data.contactPersonPhone);
      formData.append("cargo_contacto", data.cargoContacto);
      formData.append("participo_edicion_anterior", String(data.participoEdicionAnterior));
      formData.append("rubro_logistico", data.rubroLogistico);
      formData.append("requiere_electricidad", String(data.requiereElectricidad));
      formData.append("computadora_o_pantalla", String(data.computadoraOPantalla));
      formData.append("tipo_mobiliario", data.tipoMobiliario);
      formData.append("gazebo_propio", String(data.gazeboPropio));
      formData.append("estructura_adicional", data.estructuraAdicional || "");
      formData.append("acciones_stand", data.accionesStand || "");
      formData.append("acepta_tyc", String(data.aceptaTyC));
      formData.append("participacion_opciones", JSON.stringify([participationType || "stand"]));

      if (otraParticipacion) {
        formData.append("participacion_otra", otraParticipacion);
      }

      if (data.logo && data.logo[0]) {
        formData.append("logo", data.logo[0]);
      }

      const response = await registrarEmpresa(formData);
      if (response && (response.status === "success" || response.id)) {
        const msg = response.message || "Tu registro empresarial ha sido procesado correctamente.";
        toast({
          title: "✅ Empresa Registrada",
          description: msg,
          variant: "default",
        });
        setSuccessMessage(msg);
        setShowModal(true);
        reset();
      } else {
        toast({
          title: "❌ Error en el registro",
          description: response?.message || "Ocurrió un error inesperado.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "❌ Error de conexión",
        description: "No se pudo conectar con el servidor.",
        variant: "destructive",
      });
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    window.location.href = "/seleccion-registro";
  };

  return (
    <div className="form-bg-gradient py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center transform animate-in slide-in-from-bottom-4 duration-300">
              <div className="mx-auto flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">¡Registro Exitoso!</h2>
              <p className="text-slate-600 mb-8 leading-relaxed">
                {successMessage || "Su empresa ha sido registrada exitosamente. Nos contactaremos pronto."}
              </p>
              <FormButton onClick={handleCloseModal} fullWidth>
                Continuar
              </FormButton>
            </div>
          </div>
        )}

        <FormCard
          title="Registro Empresarial"
          description="Registre su empresa para participar como expositor, patrocinador o ponente en el Congreso."
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <FormSection title="Información de la Empresa" description="Datos básicos de la organización">
              <div className="relative mb-6">
                <FormInput
                  type="email"
                  label="Email Corporativo"
                  icon={<Mail className="h-4 w-4" />}
                  placeholder="contacto@empresa.com"
                  {...register("companyEmail")}
                  error={errors.companyEmail?.message}
                />
                {isCheckingCRM && (
                  <div className="absolute right-3 top-9">
                    <div className="animate-spin h-5 w-5 border-2 border-congress-blue border-t-transparent rounded-full" />
                  </div>
                )}
              </div>

              <FormInput
                label="Nombre de la Empresa"
                icon={<Building2 className="h-4 w-4" />}
                placeholder="Ej: Logística Integral S.A."
                {...register("companyName")}
                error={errors.companyName?.message}
              />

              <FormInput
                label="Sitio Web (Opcional)"
                icon={<Globe className="h-4 w-4" />}
                placeholder="www.empresa.com"
                {...register("website")}
                error={errors.website?.message}
              />

              <FormTextArea
                label="Descripción"
                placeholder="Breve descripción..."
                {...register("companyDescription")}
                error={errors.companyDescription?.message}
              />

              <FormInput
                label="Rubro"
                icon={<Briefcase className="h-4 w-4" />}
                placeholder="Ej: Transporte"
                {...register("rubroLogistico")}
                error={errors.rubroLogistico?.message}
              />
            </FormSection>

            <FormSection title="Contacto" description="Persona responsable">
              <FormInput
                label="Nombre y Apellido"
                icon={<User className="h-4 w-4" />}
                placeholder="Juan Pérez"
                {...register("contactPersonName")}
                error={errors.contactPersonName?.message}
              />
              <FormInput
                label="Cargo"
                placeholder="Gerente"
                {...register("cargoContacto")}
                error={errors.cargoContacto?.message}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormInput label="Email" {...register("contactPersonEmail")} error={errors.contactPersonEmail?.message} />
                <FormInput label="Teléfono" {...register("contactPersonPhone")} error={errors.contactPersonPhone?.message} />
              </div>
            </FormSection>

            <FormSection title="Participación" description="Modalidad de interés">
              <div className="space-y-4">
                <select
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-congress-blue outline-none"
                  value={participationType}
                  onChange={e => setParticipationType(e.target.value)}
                  required
                >
                  <option value="">Seleccione una opción...</option>
                  {participationOptions.map(opt => (
                    <option key={opt.id} value={opt.id}>{opt.label}</option>
                  ))}
                </select>
                {participationType === "otra" && (
                  <FormInput
                    label="Especifique otra modalidad"
                    placeholder="Escriba aquí..."
                    value={otraParticipacion}
                    onChange={e => setOtraParticipacion(e.target.value)}
                  />
                )}
              </div>
            </FormSection>

            <FormSection title="Logística y Necesidades" description="Detalles para la organización del espacio">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormCheckbox
                  label="¿Participó en ediciones anteriores?"
                  {...register("participoEdicionAnterior")}
                />
                <FormCheckbox
                  label="¿Requiere conexión eléctrica?"
                  {...register("requiereElectricidad")}
                />
                <FormCheckbox
                  label="¿Traerá pantalla/computadora propia?"
                  {...register("computadoraOPantalla")}
                />
                <FormCheckbox
                  label="¿Cuenta con gazebo propio?"
                  {...register("gazeboPropio")}
                />
              </div>

              <div className="mt-6">
                <label className="text-sm font-semibold text-slate-800 mb-2 block">Tipo de Mobiliario Requerido</label>
                <select
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-congress-blue outline-none"
                  {...register("tipoMobiliario")}
                >
                  <option value="Ninguno">No requiere mobiliario</option>
                  <option value="Mesa y dos sillas">Mesa y dos sillas</option>
                  <option value="Solo mesa">Solo mesa</option>
                  <option value="Solo dos sillas">Solo dos sillas</option>
                </select>
              </div>

              <div className="mt-6 space-y-6">
                <FormTextArea
                  label="Estructura Adicional"
                  placeholder="Describa si traerá banners, back de prensa, etc."
                  {...register("estructuraAdicional")}
                />
                <FormTextArea
                  label="Acciones en el Stand"
                  placeholder="Sorteos, entrega de merchandising, juegos, etc."
                  {...register("accionesStand")}
                />
              </div>

              <div className="mt-6">
                <FormFileInput
                  label="Logo de la Empresa (Opcional)"
                  {...register("logo")}
                  accept="image/*"
                  helperText="Formatos soportados: JPG, PNG. Máx 2MB."
                />
              </div>
            </FormSection>

            <div className="pt-6 border-t border-slate-200">
              <div className="mb-6 bg-blue-50/50 p-4 rounded-xl border border-blue-100/50">
                <FormCheckbox
                  id="aceptaTyC"
                  label={
                    <span className="text-sm text-slate-700 leading-relaxed">
                      Declaro que la información es verídica y confirmo que he leído y acepto las <TermsAndConditionsModal type="stand" /> para empresas participantes.
                    </span>
                  }
                  {...register("aceptaTyC")}
                  error={errors.aceptaTyC?.message}
                />
              </div>
              <FormButton
                type="submit"
                fullWidth
                isLoading={isSubmitting}
                className="shadow-xl shadow-congress-blue/20"
              >
                {isSubmitting ? "Enviando Registro..." : "Registrar Empresa"}
              </FormButton>
            </div>
          </form>
        </FormCard>
      </div>
    </div>
  );
};

export default RegistroEmpresas;
