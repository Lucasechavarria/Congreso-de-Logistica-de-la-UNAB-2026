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
  FormTextArea
} from "@/components/ui/modern-form";
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  User,
  FileText,
  CheckCircle,
  Briefcase,
  Crown,
  Users,
  Globe
} from "lucide-react";
import { registrarEmpresa, verificarEmpresa } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { TermsAndConditionsModal } from "@/components/TermsAndConditionsModal";
import { FormCheckbox } from "@/components/ui/modern-form";

const companyRegistrationSchema = z.object({
  companyName: z.string().min(1, "El nombre de la empresa es requerido"),
  companyCUIT: z.string()
    .min(1, "El CUIT de la empresa es requerido")
    .regex(/^\d{2}-\d{8}-\d{1}$/, "El CUIT debe tener el formato XX-XXXXXXXX-X (ej: 20-32764773-4)"),
  companyAddress: z.string().min(1, "La dirección de la empresa es requerida"),
  companyPhone: z.string().min(1, "El teléfono de la empresa es requerido"),
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
              companyCUIT: e.cuit || "",
              companyAddress: e.direccion || "",
              companyPhone: e.telefono_empresa || "",
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
            });

            // Manejar tipo de participacion
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
  }, [watchedEmail, reset, toast]); const onSubmit = async (data: CompanyRegistrationFormData) => {
    // Crear FormData para enviar datos y archivo
    const formData = new FormData();
    formData.append("nombre_empresa", data.companyName);
    formData.append("cuit", data.companyCUIT);
    formData.append("direccion", data.companyAddress);
    formData.append("telefono_empresa", data.companyPhone);
    formData.append("email_empresa", data.companyEmail);
    // Manejo robusto del sitio web opcional
    const sitioWebValue = data.website?.trim();
    if (sitioWebValue) {
      let finalUrl = sitioWebValue;
      if (!/^https?:\/\//i.test(finalUrl)) {
        finalUrl = "https://" + finalUrl;
      }
      formData.append("sitio_web", finalUrl);
    }
    // No anexamos nada si está vacío para evitar errores de validación en el backend
    formData.append("descripcion", data.companyDescription || "");
    formData.append("nombre_contacto", data.contactPersonName);
    formData.append("email_contacto", data.contactPersonEmail);
    formData.append("celular_contacto", data.contactPersonPhone);
    formData.append("cargo_contacto", data.cargoContacto);

    // Enviar solo la opción seleccionada
    formData.append("participacion_opciones", participationType);
    formData.append("participacion_otra", participationType === "otra" ? otraParticipacion : "");

    // Anexar campos logísticos al formData
    formData.append("participo_edicion_anterior", data.participoEdicionAnterior ? "true" : "false");
    formData.append("rubro_logistico", data.rubroLogistico);
    formData.append("requiere_electricidad", data.requiereElectricidad ? "true" : "false");
    formData.append("computadora_o_pantalla", data.computadoraOPantalla ? "true" : "false");
    formData.append("tipo_mobiliario", data.tipoMobiliario);
    formData.append("gazebo_propio", data.gazeboPropio ? "true" : "false");
    formData.append("estructura_adicional", data.estructuraAdicional || "");
    formData.append("acciones_stand", data.accionesStand || "");
    formData.append("acepta_tyc", data.aceptaTyC === true ? "true" : "false");

    if (data.logo && data.logo[0]) {
      formData.append("logo", data.logo[0]);
    }
    try {
      const response = await registrarEmpresa(formData);
      if (response.status === "success") {
        toast({
          title: "✅ ¡Empresa registrada exitosamente!",
          description: "Hemos recibido tu solicitud. Te contactaremos pronto.",
          variant: "default",
        });
        setShowModal(true);
        reset();
        setParticipationType("");
      } else {
        let errorMsg = "Por favor verifica los datos e intenta nuevamente.";
        if (response.message) {
          if (typeof response.message === "object") {
            const fieldMap: Record<string, string> = {
              'nombre_empresa': 'Nombre de la empresa',
              'cuit': 'CUIT',
              'direccion': 'Dirección',
              'telefono_empresa': 'Teléfono corporativo',
              'email_empresa': 'Email corporativo',
              'sitio_web': 'Sitio web',
              'logo': 'Logo corporativo'
            };

            const errorsList = Object.entries(response.message).map(([field, msgs]: [string, any]) => {
              const fieldName = fieldMap[field] || field;
              let message = Array.isArray(msgs) ? msgs[0] : msgs;
              if (typeof message === 'object' && message !== null) {
                message = JSON.stringify(message);
              }
              return `• ${fieldName}: ${message}`;
            }).join('\n');
            errorMsg = errorsList;
          } else {
            errorMsg = response.message;
          }
        }
        toast({
          title: "❌ Error al registrar la empresa",
          description: errorMsg,
          variant: "destructive",
        });
      }
    } catch (err: any) {
      toast({
        title: "❌ Error de conexión",
        description: err?.message || "No se pudo conectar con el servidor. Verifica tu conexión a internet.",
        variant: "destructive",
      });
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setTimeout(() => {
      window.location.href = "/seleccion-registro";
    }, 300);
  };

  return (
    <div className="form-bg-gradient py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Modal de confirmación modernizado */}
        {showModal && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={handleCloseModal}
          >
            <div
              className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center transform animate-in slide-in-from-bottom-4 duration-300"
              onClick={e => e.stopPropagation()}
            >
              <div className="mx-auto flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">¡Inscripción Exitosa!</h2>
              <p className="text-slate-600 mb-8 leading-relaxed">
                Su empresa ha sido registrada exitosamente. Nos contactaremos pronto para coordinar los detalles de su participación.
              </p>
              <FormButton onClick={handleCloseModal} fullWidth>
                Continuar
              </FormButton>
            </div>
          </div>
        )}
        <FormCard
          title="Registro Empresarial"
          description="Registre su empresa para participar como expositor, patrocinador o ponente en el Congreso de Logística y Transporte UNaB 2025"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {/* Información de la Empresa */}
            <FormSection
              title="Información de la Empresa"
              description="Ingrese el email corporativo para comenzar. Si ya están registrados, recuperaremos sus datos."
            >
              <div className="relative mb-6">
                <FormInput
                  type="email"
                  label="Email Corporativo"
                  icon={<Mail className="h-4 w-4" />}
                  placeholder="contacto@empresa.com"
                  {...register("companyEmail")}
                  error={errors.companyEmail?.message}
                  helperText={crmMode ? "¡Perfil recuperado del sistema!" : "Ingrese el email para validar la empresa."}
                />
                {isCheckingCRM && (
                  <div className="absolute right-3 top-9">
                    <div className="animate-spin h-5 w-5 border-2 border-congress-blue border-t-transparent rounded-full" />
                  </div>
                )}
                {crmMode && (
                  <div className="absolute right-3 top-9 text-green-500">
                    <CheckCircle className="h-5 w-5" />
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <FormInput
                  label="Nombre de la Empresa"
                  icon={<Building2 className="h-4 w-4" />}
                  placeholder="Ej: Logística Integral S.A."
                  {...register("companyName")}
                  error={errors.companyName?.message}
                />
                <FormInput
                  label="CUIT"
                  icon={<FileText className="h-4 w-4" />}
                  placeholder="20-32764773-4"
                  maxLength={13}
                  {...register("companyCUIT")}
                  onInput={(e: React.FormEvent<HTMLInputElement>) => {
                    const target = e.target as HTMLInputElement;
                    let value = target.value.replace(/\D/g, "");
                    if (value.length > 2) value = value.substring(0, 2) + "-" + value.substring(2);
                    if (value.length > 11) value = value.substring(0, 11) + "-" + value.substring(11, 12);
                    target.value = value;
                  }}
                  error={errors.companyCUIT?.message}
                />
              </div>
              <FormInput
                label="Dirección"
                icon={<MapPin className="h-4 w-4" />}
                placeholder="Dirección, numeración, partido, provincia / estado, país"
                {...register("companyAddress")}
                error={errors.companyAddress?.message}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormInput
                  label="Teléfono Corporativo"
                  icon={<Phone className="h-4 w-4" />}
                  placeholder="11 1234-5678"
                  {...register("companyPhone")}
                  error={errors.companyPhone?.message}
                />
                <FormInput
                  label="Sitio Web (Opcional)"
                  icon={<Globe className="h-4 w-4" />}
                  placeholder="www.empresa.com"
                  {...register("website")}
                  error={errors.website?.message}
                />
              </div>
              <FormTextArea
                label="Descripción de la Empresa"
                placeholder="Breve descripción de la empresa, productos y servicios (opcional)"
                {...register("companyDescription")}
                error={errors.companyDescription?.message}
              />
              <FormInput
                label="Rubro Logístico/Transporte"
                icon={<Briefcase className="h-4 w-4" />}
                placeholder="Ej: Transporte de carga, software marítimo, etc."
                {...register("rubroLogistico")}
                error={errors.rubroLogistico?.message}
              />
            </FormSection>
            {/* Persona de Contacto */}
            <FormSection
              title="Persona de Contacto"
              description="Datos del responsable para coordinar la participación"
            >
              <FormInput
                label="Nombre y Apellido"
                icon={<User className="h-4 w-4" />}
                placeholder="Juan Pérez"
                {...register("contactPersonName")}
                error={errors.contactPersonName?.message}
              />
              <FormInput
                label="Cargo en la Empresa"
                icon={<Briefcase className="h-4 w-4" />}
                placeholder="Ej: Gerente de RRHH"
                {...register("cargoContacto")}
                error={errors.cargoContacto?.message}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormInput
                  type="email"
                  label="Email"
                  icon={<Mail className="h-4 w-4" />}
                  placeholder="juan.perez@empresa.com"
                  {...register("contactPersonEmail")}
                  error={errors.contactPersonEmail?.message}
                />
                <FormInput
                  type="tel"
                  label="Teléfono"
                  icon={<Phone className="h-4 w-4" />}
                  placeholder="11 1234-5678"
                  {...register("contactPersonPhone")}
                  error={errors.contactPersonPhone?.message}
                />
              </div>
            </FormSection>
            {/* Logo de la Empresa */}
            <FormSection
              title="Identidad Visual de la Empresa"
              description="Suba el logo institucional para los materiales de difusión del congreso"
            >
              <FormFileInput
                label="Logo Corporativo"
                accept=".png,.jpg,.jpeg,.svg,.pdf,.ai,.eps,.psd"
                hint="Formatos: PNG, JPG, SVG, PDF, AI, EPS, PSD. Soporta formatos de diseño profesional. Máx: 50MB."
                error={errors.logo?.message as string}
                onChange={e => {
                  setValue("logo", e.target.files);
                }}
              />
            </FormSection>
            {/* Tipo de Participación */}
            <FormSection
              title="Tipo de Participación"
              description="Seleccione la modalidad de participación de su interés"
            >
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-800 tracking-wide">
                  Modalidad de Participación
                </label>
                <select
                  className="w-full p-3 border rounded-lg"
                  value={participationType}
                  onChange={e => {
                    setParticipationType(e.target.value);
                    setValue("participationOptions", [e.target.value]);
                    if (e.target.value !== "otra") setOtraParticipacion("");
                  }}
                  required
                >
                  <option value="">Seleccione una opción...</option>
                  {participationOptions.map(option => (
                    <option key={option.id} value={option.id}>{option.label}</option>
                  ))}
                </select>
                {participationType === "otra" && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-slate-800 mb-1">Especifique la modalidad</label>
                    <input
                      type="text"
                      className="w-full p-3 border rounded-lg"
                      value={otraParticipacion}
                      onChange={e => setOtraParticipacion(e.target.value)}
                      placeholder="Describa la modalidad de participación"
                      required
                    />
                  </div>
                )}
                {participationType && participationType !== "otra" && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">
                      ✓ Modalidad seleccionada: {participationOptions.find(opt => opt.id === participationType)?.label}
                    </p>
                  </div>
                )}
              </div>
            </FormSection>

            {/* SECCIÓN LOGÍSTICA PARA STAND */}
            {participationType === "stand" && (
              <FormSection
                title="Logística del Stand"
                description="Complete estos datos para ayudarnos a organizar su espacio"
              >
                <div className="space-y-4">
                  <FormCheckbox
                    label="¿Ha participado en ediciones anteriores de este Congreso?"
                    {...register("participoEdicionAnterior")}
                  />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormCheckbox
                      label="¿Requiere conexión eléctrica?"
                      description="Indispensable para computadoras, pantallas o iluminación propia."
                      {...register("requiereElectricidad")}
                    />
                    <FormCheckbox
                      label="¿Llevará computadora o pantalla LCD/LED para su stand?"
                      {...register("computadoraOPantalla")}
                    />
                  </div>

                  <div className="mt-6 mb-4">
                    <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                      ¿Qué mobiliario requerirá la Organización? (Seleccione una)
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                      {["Mesa y dos sillas", "Solo mesa", "Solo dos sillas", "Ninguno"].map(tipo => (
                        <div key={tipo} className="flex items-center space-x-2">
                          <input
                            type="radio"
                            id={`mob-${tipo}`}
                            value={tipo}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                            {...register("tipoMobiliario")}
                          />
                          <label htmlFor={`mob-${tipo}`} className="text-sm text-gray-700">{tipo}</label>
                        </div>
                      ))}
                    </div>
                    {errors.tipoMobiliario && (
                      <p className="text-xs text-red-600 font-medium mt-1">
                        {errors.tipoMobiliario.message}
                      </p>
                    )}
                  </div>

                  <FormCheckbox
                    label="¿Cuenta con Gazebo Propio?"
                    description="Si la exposición es al exterior, preferimos que utilicen su propia estructura si la tienen."
                    {...register("gazeboPropio")}
                  />

                  <FormTextArea
                    label="Detalle de estructura adicional"
                    placeholder="Especifique si llevará banners (y su tamaño), cartelería, back de prensa o algún mueble propio extra."
                    {...register("estructuraAdicional")}
                  />
                  <FormTextArea
                    label="Activaciones o Acciones en el Stand"
                    placeholder="Describa si realizará sorteos, juegos, entrega de merchandising u otras dinámicas de interacción con el público."
                    {...register("accionesStand")}
                  />
                </div>
              </FormSection>
            )}

            {/* TyC y Botón de envío */}
            <div className="pt-6 border-t border-slate-200">
              <div className="mb-6 flex items-start gap-3 bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                <input
                  type="checkbox"
                  id="aceptaTyC"
                  className="mt-1 h-5 w-5 rounded border-gray-300 text-congress-blue focus:ring-congress-blue"
                  {...register("aceptaTyC")}
                />
                <div className="flex-1">
                  <label htmlFor="aceptaTyC" className="text-sm text-gray-700">
                    He leído y acepto las <TermsAndConditionsModal type="stand" /> del Congreso de Logística y Transporte.
                  </label>
                  {errors.aceptaTyC && (
                    <p className="text-xs text-red-600 font-medium mt-1">
                      {errors.aceptaTyC.message}
                    </p>
                  )}
                </div>
              </div>
              <FormButton
                type="submit"
                fullWidth
                size="lg"
                isLoading={isSubmitting}
                icon={<Building2 className="h-5 w-5" />}
              >
                {isSubmitting ? "Registrando Empresa..." : crmMode ? "Actualizar Empresa" : "Registrar Empresa"}
              </FormButton>
            </div>
          </form>
        </FormCard>
      </div>
    </div >


  )
}

export default RegistroEmpresas;
