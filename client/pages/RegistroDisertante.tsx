import React, { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
    FormInput,
    FormButton,
    FormCard,
    FormSection,
    FormTextArea,
    FormCheckbox,
    FormSelect
} from "@/components/ui/modern-form";
import {
    User,
    Mail,
    Phone,
    MapPin,
    Briefcase,
    Building2,
    Presentation,
    CheckCircle,
    IdCard,
    Link as LinkIcon
} from "lucide-react";
import { postularDisertante, verificarDisertante } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { TermsAndConditionsModal } from "@/components/TermsAndConditionsModal";

const ejesOpciones = [
    "Gestión de la Cadena de Suministro (Suministro)",
    "Transporte y Distribución",
    "Tecnología e Innovación en Logística",
    "Sostenibilidad y Logística Verde",
    "Infraestructura Logística",
    "Logística Urbana y Última Milla",
    "Comercio Internacional y Aduanas"
];

const publicoOpciones = ["Estudiantes", "Académicos/Investigadores", "Profesionales Técnicos", "Empresarios/Directivos"];
const modalidadOpciones = ["Conferencia individual", "Panel", "Entrevista"];
const participacionOpciones = ["A título personal", "En representación de una empresa/institución"];

const disertanteSchema = z.object({
    // Personal & Profesional
    nombreApellido: z.string().min(1, "El nombre completo es requerido"),
    dni: z.string().min(1, "El DNI es requerido").regex(/^\d{7,8}$/, "El DNI debe tener entre 7 y 8 dígitos numéricos").transform((val) => val.replace(/\D/g, "").slice(0, 8)),
    email: z.string().email("Debe ser un correo válido"),
    telefono: z.string().min(1, "El teléfono es requerido"),
    ciudadProvincia: z.string().min(1, "La ciudad y provincia son requeridas"),
    profesionCargo: z.string().min(1, "La profesión o cargo es requerido"),
    empresaInstitucion: z.string().min(1, "La institución a la que pertenece es requerida"),
    linkedin: z.string().optional(),

    // Propuesta de Charla
    tituloCharla: z.string().min(1, "El título de la charla es requerido"),
    ejesTematicos: z.string().min(1, "Debes seleccionar un eje temático"),
    ejeOtro: z.string().optional(),

    resumenCharla: z.string()
        .min(10, "El resumen debe tener al menos 10 caracteres")
        .refine((val) => val.split(" ").length <= 300, {
            message: "El resumen no debe exceder las 300 palabras",
        }),
    objetivosCharla: z.string().min(10, "Los objetivos son requeridos"),
    publicoDirigido: z.array(z.string()).min(1, "Debes seleccionar el público al que va dirigido"),

    // Modalidad y Participación
    modalidad: z.string().min(1, "Selecciona el formato preferido para la presentación"),
    participacionTipo: z.string().min(1, "Selecciona tu tipo de participación"),

    aceptaTyC: z.literal(true, {
        errorMap: () => ({ message: "Debes aceptar las Bases y Condiciones para continuar" }),
    }),
});

type DisertanteFormData = z.infer<typeof disertanteSchema>;

const RegistroDisertante: React.FC = () => {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [isCheckingCRM, setIsCheckingCRM] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [crmMode, setCrmMode] = useState(false); // Indica si estamos editando un existente

    const {
        register,
        handleSubmit,
        control,
        watch,
        formState: { errors, isSubmitting },
        reset,
    } = useForm<DisertanteFormData>({
        resolver: zodResolver(disertanteSchema),
        defaultValues: {
            ejesTematicos: "",
            publicoDirigido: [],
            modalidad: "",
            participacionTipo: ""
        }
    });

    const selectedEjes = watch("ejesTematicos");
    const watchedDni = watch("dni");

    // Efecto para buscar en el CRM cuando el DNI tiene 8 dígitos
    React.useEffect(() => {
        const checkCRM = async () => {
            if (watchedDni && watchedDni.length >= 7) {
                setIsCheckingCRM(true);
                try {
                    const response = await verificarDisertante(watchedDni);
                    if (response && response.status === 'success' && response.disertante) {
                        const d = response.disertante;

                        // Parsear modalidad y participación si vienen como strings (el backend los guarda así o como array)
                        const rawModalidad = d.modalidad || "";
                        const parseadoModalidad = rawModalidad.replace(/[\[\]'"]/g, '');
                        const rawParticipacion = d.participacion_tipo || "";
                        const parseadoParticipacion = rawParticipacion.replace(/[\[\]'"]/g, '');

                        // Extraer el eje
                        let ejePrincipal = "";
                        const rawEjes = d.ejes_tematicos || "";
                        try {
                            const ejes = Array.isArray(rawEjes) ? rawEjes : (typeof rawEjes === 'string' && (rawEjes.startsWith('[') || rawEjes.startsWith('{')) ? JSON.parse(rawEjes) : [rawEjes]);
                            if (ejes && ejes.length > 0) {
                                // Buscar si el eje existe en nuestras opciones
                                const foundEje = ejesOpciones.find(opt => ejes.includes(opt));
                                ejePrincipal = foundEje || (ejes[0] === "otro" ? "otro" : "");
                                if (!foundEje && ejes[0] && ejes[0] !== "otro") {
                                    ejePrincipal = "otro";
                                    // El valor de ejeOtro se asignará en el reset general abajo
                                }
                            }
                        } catch (e) {
                            console.error("Error parseando ejes:", e);
                        }

                        // Formatear público objetivo
                        let publico = [];
                        try {
                            publico = Array.isArray(d.publico_dirigido) ? d.publico_dirigido : JSON.parse(d.publico_dirigido?.replace(/'/g, '"') || "[]");
                        } catch {
                            // Fallback para strings simples o nulos
                            if (d.publico_dirigido && typeof d.publico_dirigido === 'string') {
                                publico = [d.publico_dirigido];
                            }
                        }

                        reset({
                            nombreApellido: d.nombre_apellido || "",
                            dni: d.dni || watchedDni,
                            email: d.email || "",
                            telefono: d.telefono || "",
                            ciudadProvincia: d.ciudad_provincia || "",
                            profesionCargo: d.profesion_cargo || "",
                            empresaInstitucion: d.empresa_institucion || "",
                            linkedin: d.linkedin || "",
                            tituloCharla: d.titulo_charla || "",
                            resumenCharla: d.resumen_charla || "",
                            objetivosCharla: d.objetivos_charla || "",
                            modalidad: modalidadOpciones.find(m => parseadoModalidad.includes(m)) || "",
                            participacionTipo: participacionOpciones.find(p => parseadoParticipacion.includes(p)) || "",
                            publicoDirigido: publico,
                            ejesTematicos: ejePrincipal,
                            ejeOtro: d.eje_otro || (ejePrincipal === "otro" ? (Array.isArray(rawEjes) ? rawEjes[0] : rawEjes) : ""),
                            aceptaTyC: true
                        });

                        setCrmMode(true);
                        toast({
                            title: "✅ Perfil Encontrado",
                            description: "Hemos cargado sus datos como disertante de ediciones anteriores.",
                            variant: "default",
                        });
                    }
                } catch (error) {
                    setCrmMode(false);
                    // No mostrar toaster de error si es un nuevo usuario
                    console.log("No registrado anteriormente");
                } finally {
                    setIsCheckingCRM(false);
                }
            } else {
                setCrmMode(false);
            }
        };

        const timeoutId = setTimeout(() => {
            checkCRM();
        }, 800);

        return () => clearTimeout(timeoutId);
    }, [watchedDni, reset, toast]);

    const onSubmit = async (data: DisertanteFormData) => {
        // Preparar el DTO para el backend
        const dataToSend: any = {
            nombre_apellido: data.nombreApellido,
            dni: data.dni,
            email: data.email,
            telefono: data.telefono,
            ciudad_provincia: data.ciudadProvincia,
            profesion_cargo: data.profesionCargo,
            empresa_institucion: data.empresaInstitucion,
            titulo_charla: data.tituloCharla,
            ejes_tematicos: [data.ejesTematicos],
            eje_otro: data.ejeOtro || "",
            resumen_charla: data.resumenCharla,
            objetivos_charla: data.objetivosCharla,
            publico_dirigido: data.publicoDirigido,
            modalidad: [data.modalidad],
            participacion_tipo: [data.participacionTipo],
            acepta_tyc: data.aceptaTyC
        };

        if (data.linkedin && data.linkedin.trim()) {
            dataToSend.linkedin = data.linkedin.trim();
        }

        try {
            const response = await postularDisertante(dataToSend);
            if (response && response.status === "success" || response.id) {
                const msg = response.message || "Hemos recibido tu propuesta. Nuestro equipo académico se contactará contigo.";
                toast({
                    title: "✅ ¡Postulación Registrada!",
                    description: msg,
                    variant: "default",
                });
                setSuccessMessage(msg);
                setShowModal(true);
                reset();
            } else {
                let errorMsg = "Ocurrió un error inesperado al procesar su solicitud.";
                if (response?.message) {
                    if (typeof response.message === "object") {
                        // Mapear campos a nombres legibles
                        const fieldMap: Record<string, string> = {
                            'linkedin': 'LinkedIn',
                            'email': 'Correo electrónico',
                            'dni': 'DNI',
                            'telefono': 'Teléfono móvil',
                            'resumen_charla': 'Resumen de la charla',
                            'objetivos_charla': 'Objetivos',
                            'titulo_charla': 'Título de la exposición'
                        };

                        errorMsg = Object.entries(response.message).map(([field, msgs]: [string, any]) => {
                            const fieldName = fieldMap[field] || field;
                            const message = Array.isArray(msgs) ? msgs[0] : msgs;
                            return `• ${fieldName}: ${message}`;
                        }).join('\n');
                    } else {
                        errorMsg = String(response.message);
                    }
                }

                toast({
                    title: "❌ Error en el registro",
                    description: errorMsg,
                    variant: "destructive",
                });
            }
        } catch (err: any) {
            toast({
                title: "❌ Error de conexión",
                description: err?.message || "No se pudo conectar con el servidor.",
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

    // Helper renderizador para múltiples checkboxes vinculados a react-hook-form
    const MultiCheckboxList = ({ options, name }: { options: string[], name: any }) => (
        <Controller
            control={control}
            name={name}
            render={({ field }) => (
                <div className="space-y-2 mt-2">
                    {options.map((option) => {
                        const isChecked = field.value?.includes(option);
                        return (
                            <div key={option} className="flex items-start space-x-3">
                                <input
                                    type="checkbox"
                                    id={`${name}-${option}`}
                                    className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                                    checked={isChecked}
                                    onChange={(e) => {
                                        const valueCopy = [...(field.value || [])];
                                        if (e.target.checked) {
                                            valueCopy.push(option);
                                        } else {
                                            const idx = valueCopy.indexOf(option);
                                            if (idx > -1) valueCopy.splice(idx, 1);
                                        }
                                        field.onChange(valueCopy);
                                    }}
                                />
                                <label htmlFor={`${name}-${option}`} className="text-sm text-slate-700 font-medium">
                                    {option}
                                </label>
                            </div>
                        );
                    })}
                </div>
            )}
        />
    );

    // Helper renderizador para selección única vinculada a react-hook-form
    const SingleSelectionList = ({ options, name }: { options: string[], name: any }) => (
        <Controller
            control={control}
            name={name}
            render={({ field }) => (
                <div className="space-y-2 mt-2">
                    {options.map((option) => (
                        <div key={option} className="flex items-start space-x-3">
                            <input
                                type="radio"
                                id={`${name}-${option}`}
                                name={name}
                                className="mt-1 h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
                                checked={field.value === option}
                                onChange={() => field.onChange(option)}
                            />
                            <label htmlFor={`${name}-${option}`} className="text-sm text-slate-700 font-medium">
                                {option}
                            </label>
                        </div>
                    ))}
                </div>
            )}
        />
    );

    return (
        <div className="form-bg-gradient py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                {showModal && (
                    <div
                        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50"
                        onClick={handleCloseModal}
                    >
                        <div
                            className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center transform animate-in slide-in-from-bottom-4 duration-300"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="mx-auto flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                                <CheckCircle className="w-8 h-8 text-blue-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 mb-3">¡Postulación Enviada!</h2>
                            <p className="text-slate-600 mb-8 leading-relaxed">
                                {successMessage || "Se ha enviado un email de confirmación a la dirección registrada con todos los detalles del congreso."}
                            </p>
                            <FormButton onClick={handleCloseModal} fullWidth>
                                Continuar
                            </FormButton>
                        </div>
                    </div>
                )}

                <FormCard
                    title="Call for Papers - Disertantes"
                    description={
                        <div className="flex flex-col gap-4 mt-3">
                            <span>Detalles técnicos y estructuración de su disertación.</span>
                            <div className="p-4 bg-blue-50 border border-blue-200 text-blue-700 text-base sm:text-lg font-semibold rounded-xl shadow-sm text-center">
                                La Comisión Académica evaluará las postulaciones recibidas y comunicará a cada disertante, vía correo electrónico, la confirmación oficial de su participación en el Congreso.
                            </div>
                        </div>
                    }
                >
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">

                        {/* Información Personal y Profesional */}
                        <FormSection
                            title="1. Datos Personales y Profesionales"
                            description="Ingrese su DNI para comenzar. Si ya participó antes, recuperaremos sus datos."
                        >
                            <div className="relative mb-6">
                                <FormInput
                                    label="DNI / Documento de Identidad"
                                    icon={<IdCard className="h-4 w-4" />}
                                    placeholder="12345678"
                                    maxLength={8}
                                    onInput={(e: React.FormEvent<HTMLInputElement>) => {
                                        const target = e.target as HTMLInputElement;
                                        target.value = target.value.replace(/\D/g, "").slice(0, 8);
                                    }}
                                    {...register("dni")}
                                    error={errors.dni?.message}
                                    helperText={crmMode ? "¡Perfil recuperado del sistema!" : "Ingrese su DNI para validar sus datos."}
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

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <FormInput
                                    label="Nombre y Apellido"
                                    icon={<User className="h-4 w-4" />}
                                    placeholder="Ej: Laura Martínez"
                                    {...register("nombreApellido")}
                                    error={errors.nombreApellido?.message}
                                />
                                <FormInput
                                    type="email"
                                    label="Email de Contacto"
                                    icon={<Mail className="h-4 w-4" />}
                                    placeholder="laura@ejemplo.com"
                                    {...register("email")}
                                    error={errors.email?.message}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <FormInput
                                    type="tel"
                                    label="Teléfono Móvil"
                                    icon={<Phone className="h-4 w-4" />}
                                    placeholder="11 1234-5678"
                                    {...register("telefono")}
                                    error={errors.telefono?.message}
                                />
                                <FormInput
                                    label="Ciudad y Provincia"
                                    icon={<MapPin className="h-4 w-4" />}
                                    placeholder="Ej: Almirante Brown, Buenos Aires"
                                    {...register("ciudadProvincia")}
                                    error={errors.ciudadProvincia?.message}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <FormInput
                                    label="Profesión / Cargo Actual"
                                    icon={<Briefcase className="h-4 w-4" />}
                                    placeholder="Ej: Ingeniera en Logística"
                                    {...register("profesionCargo")}
                                    error={errors.profesionCargo?.message}
                                />
                                <FormInput
                                    label="Empresa o Institución"
                                    icon={<Building2 className="h-4 w-4" />}
                                    placeholder="EJ: Universidad Nacional Guillermo Brown"
                                    {...register("empresaInstitucion")}
                                    error={errors.empresaInstitucion?.message}
                                />
                            </div>

                            <FormInput
                                label="Enlace a LinkedIn"
                                icon={<LinkIcon className="h-4 w-4" />}
                                placeholder="https://linkedin.com/in/perfil (opcional)"
                                {...register("linkedin")}
                                error={errors.linkedin?.message}
                            />
                        </FormSection>

                        {/* Propuesta de Charla */}
                        <FormSection
                            title="2. Propuesta de Charla"
                            description="Detalles técnicos y estructuración de su disertación"
                        >
                            <FormInput
                                label="Título de la Exposición"
                                icon={<Presentation className="h-4 w-4" />}
                                placeholder="Un título atractivo y claro de su charla"
                                {...register("tituloCharla")}
                                error={errors.tituloCharla?.message}
                            />

                            <div className="mt-4 border border-slate-200 rounded-lg p-4 bg-slate-50/50">
                                <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                                    Eje Temático al que se vincula (Seleccione uno)
                                </label>
                                <SingleSelectionList options={ejesOpciones} name="ejesTematicos" />

                                <div className="mt-4 flex items-start space-x-3 pt-3 border-t border-slate-200">
                                    <Controller
                                        control={control}
                                        name="ejesTematicos"
                                        render={({ field }) => (
                                            <input
                                                type="radio"
                                                id="ejes-otro-check"
                                                className="mt-1 h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
                                                checked={field.value === "otro"}
                                                onChange={() => field.onChange("otro")}
                                            />
                                        )}
                                    />
                                    <div className="flex-1">
                                        <label htmlFor="ejes-otro-check" className="text-sm text-slate-700 font-medium">Otro (especificar)</label>
                                        <textarea
                                            className="mt-2 w-full p-2 border rounded-md text-sm border-slate-300 focus:ring-blue-500 max-h-24"
                                            placeholder="Indique el nombre del nuevo eje temático"
                                            {...register("ejeOtro")}
                                        />
                                    </div>
                                </div>
                                {errors.ejesTematicos && (
                                    <p className="text-xs text-red-600 font-medium mt-2">{errors.ejesTematicos.message}</p>
                                )}
                            </div>

                            <div className="mt-6">
                                <FormTextArea
                                    label="Resumen / Abstract de la charla (Máx. 300 palabras)"
                                    placeholder="Detalle con claridad los puntos fundamentales de su exposición..."
                                    {...register("resumenCharla")}
                                    error={errors.resumenCharla?.message}
                                />
                            </div>

                            <div className="mt-6">
                                <FormTextArea
                                    label="Objetivos de la Exposición"
                                    placeholder="¿Qué espera que el público aprenda o reflexione tras su charla?"
                                    {...register("objetivosCharla")}
                                    error={errors.objetivosCharla?.message}
                                />
                            </div>

                            <div className="mt-6 border border-slate-200 rounded-lg p-4">
                                <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                                    Público al que está dirigida la charla (Seleccione uno o más)
                                </label>
                                <MultiCheckboxList options={publicoOpciones} name="publicoDirigido" />
                                {errors.publicoDirigido && (
                                    <p className="text-xs text-red-600 font-medium mt-2">{errors.publicoDirigido.message}</p>
                                )}
                            </div>
                        </FormSection>

                        {/* Formato y Logística */}
                        <FormSection
                            title="3. Modalidad y Tipo de Participación"
                            description="Conozca las opciones para estructurar su actuación"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                                        Formato Orientativo Preferido
                                    </label>
                                    <SingleSelectionList options={modalidadOpciones} name="modalidad" />
                                    {errors.modalidad && (
                                        <p className="text-xs text-red-600 font-medium mt-2">{errors.modalidad.message}</p>
                                    )}
                                </div>
                                <div>
                                    <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                                        Tipo de Participación
                                    </label>
                                    <SingleSelectionList options={participacionOpciones} name="participacionTipo" />
                                    {errors.participacionTipo && (
                                        <p className="text-xs text-red-600 font-medium mt-2">{errors.participacionTipo.message}</p>
                                    )}
                                </div>
                            </div>
                        </FormSection>

                        {/* TyC y Botón de envío */}
                        <div className="pt-6 border-t border-slate-200">
                            <div className="mb-6 bg-blue-50/50 p-4 rounded-xl border border-blue-100/50">
                                <FormCheckbox
                                    id="aceptaTyC"
                                    label={
                                        <span className="text-sm text-slate-700 leading-relaxed">
                                            Declaro que la información es verídica y confirmo que he leído y acepto expresamente las <TermsAndConditionsModal type="disertante" /> del Congreso de Logística y Transporte.
                                        </span>
                                    }
                                    {...register("aceptaTyC")}
                                    error={errors.aceptaTyC?.message}
                                />
                            </div>

                            <FormButton
                                type="submit"
                                fullWidth
                                size="lg"
                                isLoading={isSubmitting}
                                className="shadow-xl shadow-congress-blue/20"
                            >
                                {isSubmitting ? "Enviando Postulación..." : crmMode ? "Actualizar Mi Postulación" : "Enviar Mi Postulación"}
                            </FormButton>
                        </div>
                    </form>
                </FormCard>
            </div>
        </div>
    );
};

export default RegistroDisertante;
