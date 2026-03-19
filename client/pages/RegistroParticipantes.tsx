import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Select from "react-select";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { inscribirIndividual, inscribirGrupal, inscribirParticipante, verificarAsistente } from "../lib/api";
import {
  FormInput,
  FormSelect,
  FormButton,
  FormCheckbox,
  FormCard,
  FormSection
} from "@/components/ui/modern-form";
import {
  User,
  Mail,
  Phone,
  Building2,
  GraduationCap,
  Briefcase,
  Users,
  IdCard,
  CheckCircle,
  Loader2,
  UploadCloud,
  FileSpreadsheet,
  Trash2
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useDropzone } from "react-dropzone";
import * as XLSX from "xlsx";
import { TermsAndConditionsModal } from "@/components/TermsAndConditionsModal";

// Schemas de validación con validación de DNI argentino
const participantSchema = z.object({
  firstName: z.string().min(1, "El nombre es requerido"),
  lastName: z.string().min(1, "El apellido es requerido"),
  dni: z
    .string()
    .min(1, "El DNI es requerido")
    .regex(/^\d{7,8}$/, "El DNI debe tener entre 7 y 8 dígitos numéricos")
    .transform((val) => val.replace(/\D/g, "").slice(0, 8)),
  email: z.string().email("Debe ser un correo electrónico válido"),
  phone: z.string().min(1, "El teléfono es requerido"),
  aceptaTyC: z.literal(true, {
    errorMap: () => ({ message: "Debes aceptar las Bases y Condiciones para continuar" }),
  }),
});

const studentSchema = participantSchema.extend({
  profileType: z.literal("student"),
  isUnabStudent: z.boolean().optional(),
  institution: z.string().optional(),
  career: z.string().optional(),
  yearOfStudy: z.number().optional(),
});

const teacherSchema = participantSchema.extend({
  profileType: z.literal("teacher"),
  institution: z.string().min(1, "La institución es requerida"),
  careerTaught: z
    .string()
    .min(1, "La carrera que dicta es requerida para docentes."),
});

const professionalSchema = participantSchema.extend({
  profileType: z.literal("professional"),
  workArea: z.string().min(1, "El área de trabajo es requerida"),
  occupation: z.string().min(1, "El cargo es requerido"),
});

const groupMemberSchema = z.object({
  firstName: z.string().min(1, "El nombre del integrante es requerido"),
  lastName: z.string().min(1, "El apellido del integrante es requerido"),
  dni: z
    .string()
    .min(1, "El DNI del integrante es requerido")
    .regex(/^\d{7,8}$/, "El DNI debe tener 8 dígitos numéricos")
    .transform((val) => val.replace(/\D/g, "").slice(0, 8)),
  email: z.string().email("Debe ser un correo electrónico válido"),
});

const groupRepresentativeSchema = participantSchema.extend({
  profileType: z.literal("groupRepresentative"),
  groupName: z.string().min(1, "El nombre del grupo es requerido"),
  groupMunicipality: z.string().optional(),
  institutionOrWorkplace: z.string().optional(),
  groupSize: z.number().min(1, "Debe especificar al menos 1 integrante"),
  groupMembers: z
    .array(groupMemberSchema)
    .min(1, "Debe haber al menos un integrante en el grupo"),
});

const visitorSchema = participantSchema.extend({
  profileType: z.literal("visitor"),
});

const pressSchema = participantSchema.extend({
  profileType: z.literal("PRESS"),
});

const formSchema = z
  .discriminatedUnion("profileType", [
    visitorSchema,
    studentSchema,
    teacherSchema,
    professionalSchema,
    pressSchema,
    groupRepresentativeSchema,
  ])
  .superRefine((data, ctx) => {
    if (data.profileType === "student") {
      if (data.isUnabStudent === false && !data.institution) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "La institución es requerida si no perteneces a la UNaB.",
          path: ["institution"],
        });
      }
      if (!data.career) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "La carrera es requerida para estudiantes.",
          path: ["career"],
        });
      }
      if (!data.yearOfStudy) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "El año de cursada es requerido para estudiantes.",
          path: ["yearOfStudy"],
        });
      }
    }

    if (data.profileType === "groupRepresentative") {
      // Asegurar que la cantidad de miembros coincida con groupSize
      if (!Array.isArray(data.groupMembers) || data.groupMembers.length !== data.groupSize) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "La cantidad de integrantes debe coincidir con el número especificado",
          path: ["groupMembers"],
        });
      }
    }
  });

type FormData = z.infer<typeof formSchema>;

const RegistroParticipantes: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [showModal, setShowModal] = useState(false);
  const [profileType, setProfileType] = useState<FormData["profileType"]>("visitor");

  // Estado para el archivo Excel
  const [excelFile, setExcelFile] = useState<File | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        handleFileUpload(acceptedFiles[0]);
      }
    }
  } as any);

  const handleFileUpload = (file: File) => {
    setExcelFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        const workbook = XLSX.read(data, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const json: any[] = XLSX.utils.sheet_to_json(worksheet);

        if (json && json.length > 0) {
          // Filtrar filas vacías
          const validRows = json.filter(row => row.DNI || row.Nombre);
          if (validRows.length === 0) {
            toast({
              title: "❌ Archivo vacío",
              description: "El archivo no contiene registros válidos.",
              variant: "destructive",
            });
            setExcelFile(null);
            return;
          }

          setValue("groupSize", validRows.length);
          const mappedMembers = validRows.map(row => ({
            firstName: String(row.NOMBRE || row.Nombre || row.nombre || row.FirstName || ""),
            lastName: String(row.Apellido || row.apellido || row.LastName || ""),
            dni: String(row.DNI || row.dni || "").replace(/\D/g, "").slice(0, 8),
            email: String(row["CORREO ELECTRONICO"] || row.Email || row.email || row.Correo || "")
          }));

          replace(mappedMembers);

          toast({
            title: "✅ Archivo Procesado",
            description: `Se han cargado ${mappedMembers.length} integrantes exitosamente. Favor de revisar los datos.`,
            variant: "default",
          });
        }
      } catch (error) {
        console.error("Error al leer Excel:", error);
        toast({
          title: "❌ Error",
          description: "Hubo un problema procesando el archivo. Asegúrese de usar la plantilla correcta.",
          variant: "destructive",
        });
        setExcelFile(null);
      }
    };
    reader.readAsBinaryString(file);
  };

  const removeFile = () => {
    setExcelFile(null);
    setValue("groupSize", 0);
    replace([]);
  };
  const [isSearchingDni, setIsSearchingDni] = useState(false);
  const [asistenteEncontrado, setAsistenteEncontrado] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { profileType: "visitor" },
  });

  const groupSize = watch("groupSize") || 0;
  const hasDeclaredGroupSize = !!groupSize && groupSize > 0;

  // Cargar instituciones desde JSON
  const [instituciones, setInstituciones] = useState<{ label: string; value: string }[]>([]);
  // Estado para input personalizado de institución
  const [otraInstitucion, setOtraInstitucion] = useState("");
  const selectedInstitution = watch("institution");

  useEffect(() => {
    import("../data/instituciones-argentina.json").then((data) => {
      const lista = (data.default || data).map((nombre: string) => ({ label: nombre, value: nombre }));
      lista.push({ label: "Otra", value: "Otra" });
      setInstituciones(lista);
    });
  }, []);

  const handleVerifyDni = async (dniStr: string) => {
    if (!dniStr || dniStr.length < 7) return;
    setIsSearchingDni(true);
    try {
      const response = await verificarAsistente(dniStr);
      if (response && response.status === 'success' && response.asistente) {
        const data = response.asistente;
        setAsistenteEncontrado(true);
        toast({
          title: "¡Hola de nuevo!",
          description: "Hemos encontrado tus datos. Por favor, verifica y actualiza si es necesario.",
        });

        let newProfile = profileType;
        if (data.profile_type) {
          const backendToFrontendMap: Record<string, any> = {
            'VISITOR': 'visitor',
            'STUDENT': 'student',
            'TEACHER': 'teacher',
            'PROFESSIONAL': 'professional',
            'PRESS': 'press',
            'GROUP_REPRESENTATIVE': 'groupRepresentative'
          };
          if (backendToFrontendMap[data.profile_type]) {
            newProfile = backendToFrontendMap[data.profile_type];
            setProfileType(newProfile);
          }
        }

        const currentValues = watch();
        const updateData: any = {
          ...currentValues,
          firstName: data.first_name || currentValues.firstName,
          lastName: data.last_name || currentValues.lastName,
          email: data.email || currentValues.email,
          phone: data.phone || currentValues.phone,
          profileType: newProfile,
          // Nuevos campos para auto-completado
          institution: data.institution || (currentValues as any).institution,
          isUnabStudent: data.is_unab_student !== undefined ? data.is_unab_student : (currentValues as any).isUnabStudent,
          career: data.career || (currentValues as any).career,
          yearOfStudy: data.year_of_study || (currentValues as any).yearOfStudy,
          careerTaught: data.career_taught || (currentValues as any).careerTaught,
          workArea: data.work_area || (currentValues as any).workArea,
          occupation: data.occupation || (currentValues as any).occupation,
          groupName: data.group_name || (currentValues as any).groupName,
          groupMunicipality: data.group_municipality || (currentValues as any).groupMunicipality,
          groupSize: data.group_size || (currentValues as any).groupSize,
          institutionOrWorkplace: data.institution_or_workplace || data.institution || (currentValues as any).institutionOrWorkplace,
        };
        (reset as any)(updateData);

      } else {
        setAsistenteEncontrado(false);
      }
    } catch (error) {
      setAsistenteEncontrado(false);
    } finally {
      setIsSearchingDni(false);
    }
  };

  // Watch for profileType changes to conditionally reset fields
  React.useEffect(() => {
    const currentValues = watch();

    if (profileType === "groupRepresentative") {
      setValue("groupSize", 0);
      reset({
        ...currentValues,
        profileType,
        groupSize: 0,
        groupMembers: [],
      } as FormData);
    } else if (profileType === "student") {
      reset({
        ...currentValues,
        profileType,
        isUnabStudent: false,
      } as FormData);
    } else {
      reset({
        firstName: currentValues.firstName || "",
        lastName: currentValues.lastName || "",
        dni: currentValues.dni || "",
        email: currentValues.email || "",
        phone: currentValues.phone || "",
        aceptaTyC: currentValues.aceptaTyC,
        profileType,
      } as FormData);
    }
  }, [profileType, reset, watch]);

  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: "groupMembers" as const,
  });

  // Función para actualizar la cantidad de miembros
  const handleGroupSizeChange = (newSize: number) => {
    setValue("groupSize", newSize);

    // Crear array de miembros vacíos según la cantidad especificada
    const emptyMembers = Array(newSize).fill(null).map(() => ({
      firstName: "",
      lastName: "",
      dni: "",
      email: ""
    }));

    replace(emptyMembers);
  };

  const onSubmit = async (data: FormData) => {
    try {
      let response;
      if (data.profileType === "groupRepresentative") {
        // Validación adicional en el frontend
        const membersWithData = data.groupMembers.filter(member =>
          member.firstName && member.lastName && member.dni && member.email
        );

        if (membersWithData.length !== data.groupSize) {
          toast({
            title: "❌ Datos incompletos",
            description: `Has especificado ${data.groupSize} integrantes, pero solo has completado los datos de ${membersWithData.length}. Por favor completa todos los campos.`,
            variant: "destructive",
          });
          return;
        }
        // Estructura para el nuevo sistema de inscripción grupal
        // Enviamos directamente al endpoint de participantes
        const dataToSend = {
          first_name: data.firstName,
          last_name: data.lastName,
          dni: data.dni,
          email: data.email,
          phone: data.phone,
          profile_type: "GROUP_REPRESENTATIVE",
          group_name: data.groupName,
          group_municipality: data.groupMunicipality || "",
          group_size: data.groupSize,
          terminos_aceptados: data.aceptaTyC,
          miembros_grupo_nuevos: data.groupMembers.map(member => ({
            first_name: member.firstName,
            last_name: member.lastName,
            dni: member.dni,
            email: member.email
          }))
        };

        // Usar la nueva función de API para inscripción con participantes
        response = await inscribirParticipante(dataToSend);
      } else {
        // Estructura esperada por el backend
        const profileTypeMap: Record<string, string> = {
          visitor: "VISITOR",
          student: "STUDENT",
          teacher: "TEACHER",
          professional: "PROFESSIONAL",
          press: "PRESS",
          groupRepresentative: "GROUP_REPRESENTATIVE",
        };

        const asistenteData: any = {
          first_name: data.firstName,
          last_name: data.lastName,
          dni: data.dni,
          email: data.email,
          phone: data.phone,
          profile_type: profileTypeMap[data.profileType?.toLowerCase()] || data.profileType,
          terminos_aceptados: data.aceptaTyC,
        };

        // Agregar campos específicos según el tipo de participante
        if (data.profileType === "student") {
          asistenteData.is_unab_student = data.isUnabStudent || false;
          if (data.institution) asistenteData.institution = data.institution;
          if (data.career) asistenteData.career = data.career;
          if (data.yearOfStudy) asistenteData.year_of_study = data.yearOfStudy;
        } else if (data.profileType === "teacher") {
          if (data.institution) asistenteData.institution = data.institution;
          if (data.careerTaught) asistenteData.career_taught = data.careerTaught;
        } else if (data.profileType === "professional") {
          if (data.workArea) asistenteData.work_area = data.workArea;
          if (data.occupation) asistenteData.occupation = data.occupation;
        }

        const dataToSend = {
          asistente: asistenteData,
        };
        response = await inscribirIndividual(dataToSend);
      }

      if (response && response.status === "success") {
        toast({
          title: "✅ ¡Registro exitoso!",
          description: response.message || "Tu inscripción ha sido procesada correctamente.",
          variant: "default",
        });
        setShowModal(true);
        reset();
        setValue("groupSize", 0);
      } else {
        // Procesar errores del backend de forma más detallada
        let errorTitle = "Error en el registro";
        let errorMsg = "";

        if (response && response.message && typeof response.message === "object") {
          // Errores de validación estructurados por campo
          const errors = response.message;
          const fieldTranslations: Record<string, string> = {
            'dni': 'DNI',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'Teléfono',
            'group_size': 'Cantidad de miembros',
            'miembros_grupo_nuevos': 'Datos de miembros del grupo',
            'institution': 'Institución',
            'career': 'Carrera',
            'year_of_study': 'Año de cursada',
            'work_area': 'Área de trabajo',
            'occupation': 'Cargo',
            'group_name': 'Nombre del grupo',
            'profile_type': 'Tipo de participante'
          };

          const errorList = Object.entries(errors).map(([field, msgs]: [string, any]) => {
            const fieldName = fieldTranslations[field] || field;
            let message = Array.isArray(msgs) ? msgs[0] : msgs;

            // Si el mensaje es un objeto, intentar extraer el string
            if (typeof message === 'object' && message !== null) {
              message = message.message || message.string || JSON.stringify(message);
            }

            return `${fieldName}: ${message}`;
          });

          errorTitle = "Por favor corrige los siguientes errores";
          errorMsg = errorList.join('\n\n');
        } else if (typeof response?.message === 'string') {
          errorMsg = response.message;
        } else if (response && typeof response === "object") {
          errorMsg = "Error al procesar la solicitud. Por favor verifica que todos los campos estén completos y correctos.";
        } else {
          errorMsg = "No se pudo completar la inscripción. Por favor, revisa los datos e intenta nuevamente.";
        }

        toast({
          title: errorTitle,
          description: errorMsg,
          variant: "destructive",
          duration: 8000, // Más tiempo para leer errores múltiples
        });
      }
    } catch (error) {
      console.error("Error en la inscripción:", error);
      toast({
        title: "Error de conexión",
        description: "No se pudo conectar con el servidor. Por favor verifica tu conexión a internet y vuelve a intentarlo.",
        variant: "destructive",
        duration: 6000,
      });
    }
  };

  // Helper function to safely access error messages
  const getErrorMessage = (fieldPath: string): string | undefined => {
    const pathArray = fieldPath.split(".");
    let current: any = errors;

    for (const key of pathArray) {
      if (current && typeof current === "object" && key in current) {
        current = current[key];
      } else {
        return undefined;
      }
    }

    return current?.message;
  };

  return (
    <div className="form-bg-gradient py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Modal de confirmación modernizado */}
        {showModal && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => {
              setShowModal(false);
              navigate("/seleccion-registro");
            }}
          >
            <div
              className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 text-center transform animate-in slide-in-from-bottom-4 duration-300"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mx-auto flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">¡Inscripción Exitosa!</h2>
              <p className="text-slate-600 mb-8 leading-relaxed">
                Se ha enviado un email de confirmación a la dirección registrada con todos los detalles del congreso.
              </p>
              <FormButton
                onClick={() => {
                  setShowModal(false);
                  navigate("/seleccion-registro");
                }}
                fullWidth
              >
                Continuar
              </FormButton>
            </div>
          </div>
        )}

        <FormCard>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <FormSection title="Información Personal" description="Ingrese su DNI para comenzar. Si ya participó antes, recuperaremos sus datos automáticamente.">
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <FormInput
                    label="DNI"
                    icon={<IdCard className="h-4 w-4" />}
                    placeholder="12345678"
                    error={getErrorMessage("dni")}
                    maxLength={8}
                    helperText={asistenteEncontrado ? "¡Perfil encontrado!" : "Ingrese su DNI para validar su perfil."}
                    {...(() => {
                      const { onChange, onBlur, name, ref } = register("dni");
                      return {
                        onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
                          e.target.value = e.target.value.replace(/\D/g, "").slice(0, 8);
                          onChange(e);
                        },
                        onBlur: (e: React.FocusEvent<HTMLInputElement>) => {
                          onBlur(e);
                          if (e.target.value.length >= 7) {
                            handleVerifyDni(e.target.value);
                          }
                        },
                        name,
                        ref
                      };
                    })()}
                  />
                </div>
                {isSearchingDni && (
                  <div className="mb-2 pb-1">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  </div>
                )}
                {asistenteEncontrado && !isSearchingDni && (
                  <div className="mb-2 pb-1">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                )}
              </div>

              <FormSelect
                label="Tipo de Participante"
                icon={<Users className="h-4 w-4" />}
                options={[
                  { value: "visitor", label: "Visitante" },
                  { value: "student", label: "Estudiante" },
                  { value: "teacher", label: "Docente" },
                  { value: "professional", label: "Profesional" },
                  { value: "PRESS", label: "Prensa" },
                  { value: "groupRepresentative", label: "Representante de Grupo" }
                ]}
                {...register("profileType")}
                onChange={(e) => setProfileType(e.target.value as FormData["profileType"])}
                error={getErrorMessage("profileType")}
              />
              <FormInput
                label="Nombre"
                icon={<User className="h-4 w-4" />}
                placeholder="Ingrese su nombre"
                {...register("firstName")}
                error={getErrorMessage("firstName")}
              />
              <FormInput
                label="Apellido"
                icon={<User className="h-4 w-4" />}
                placeholder="Ingrese su apellido"
                {...register("lastName")}
                error={getErrorMessage("lastName")}
              />
              <FormInput
                label="Teléfono"
                icon={<Phone className="h-4 w-4" />}
                placeholder="11 1234-5678"
                {...register("phone")}
                error={getErrorMessage("phone")}
              />
              <FormInput
                type="email"
                label="Email"
                icon={<Mail className="h-4 w-4" />}
                placeholder="ejemplo@correo.com"
                {...register("email")}
                error={getErrorMessage("email")}
                helperText="Se enviará la confirmación de inscripción a este email"
              />
            </FormSection>

            {/* Campos condicionales por tipo de participante */}
            {profileType === "student" && (
              <FormSection title="Información Académica" description="Complete los datos sobre su formación académica">
                <FormCheckbox
                  label="¿Perteneces a la Universidad Nacional Guillermo Brown (UNaB)?"
                  description="Marque si es estudiante de UNaB"
                  {...register("isUnabStudent")}
                  error={getErrorMessage("isUnabStudent")}
                />

                {!watch("isUnabStudent") && (
                  <div>
                    <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                      ¿En qué institución estudias?
                    </label>
                    <Select
                      options={instituciones}
                      placeholder="Buscar institución..."
                      onChange={(option) => {
                        setValue("institution", option?.value || "");
                        if (option?.value !== "Otra") setOtraInstitucion("");
                      }}
                      value={instituciones.find(opt => opt.value === selectedInstitution) || null}
                      className="react-select-container"
                      classNamePrefix="react-select"
                      isClearable
                      noOptionsMessage={() => "Si tu institución no aparece, elige 'Otra' y escribe el nombre"}
                      filterOption={(option, inputValue) => {
                        if (option.value === "Otra") return true;
                        if (!inputValue) return true;
                        return option.label.toLowerCase().includes(inputValue.toLowerCase());
                      }}
                      styles={{
                        control: (base, state) => ({
                          ...base,
                          height: '48px',
                          borderRadius: '12px',
                          border: state.isFocused ? '2px solid hsl(197, 88%, 44%)' : '1px solid hsl(214, 32%, 91%)',
                          boxShadow: state.isFocused ? '0 0 0 4px rgba(14, 165, 233, 0.1)' : '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                          '&:hover': {
                            border: '1px solid hsl(214, 32%, 85%)'
                          }
                        }),
                        placeholder: (base) => ({
                          ...base,
                          color: 'hsl(215, 16%, 47%)'
                        })
                      }}
                    />
                    {selectedInstitution === "Otra" && (
                      <input
                        type="text"
                        className="mt-2 w-full border rounded-lg px-3 py-2"
                        placeholder="Escriba el nombre de la institución..."
                        value={otraInstitucion}
                        onChange={e => setOtraInstitucion(e.target.value)}
                        onBlur={() => setValue("institution", otraInstitucion)}
                      />
                    )}
                    {getErrorMessage("institution") && (
                      <p className="text-xs text-red-600 font-medium mt-1">
                        {getErrorMessage("institution")}
                      </p>
                    )}
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormInput
                    label="¿En qué carrera estás cursando actualmente?"
                    icon={<GraduationCap className="h-4 w-4" />}
                    placeholder="Ej: Ingeniería en Logística"
                    {...register("career")}
                    error={getErrorMessage("career")}
                  />
                  <FormInput
                    type="number"
                    label="¿En qué año te encuentras?"
                    icon={<GraduationCap className="h-4 w-4" />}
                    placeholder="1"
                    min="1"
                    max="6"
                    {...register("yearOfStudy", { valueAsNumber: true })}
                    error={getErrorMessage("yearOfStudy")}
                  />
                </div>
              </FormSection>
            )}

            {profileType === "teacher" && (
              <FormSection title="Información Profesional" description="Complete los datos sobre su actividad docente">
                <div>
                  <label className="text-sm font-semibold text-slate-800 tracking-wide mb-2 block">
                    Institución donde dicta clases
                  </label>
                  <Select
                    options={instituciones}
                    placeholder="Buscar institución..."
                    onChange={(option) => {
                      setValue("institution", option?.value || "");
                      if (option?.value !== "Otra") setOtraInstitucion("");
                    }}
                    value={instituciones.find(opt => opt.value === selectedInstitution) || null}
                    className="react-select-container"
                    classNamePrefix="react-select"
                    isClearable
                    noOptionsMessage={() => "Si tu institución no aparece, elige 'Otra' y escribe el nombre"}
                    filterOption={(option, inputValue) => {
                      if (option.value === "Otra") return true;
                      if (!inputValue) return true;
                      return option.label.toLowerCase().includes(inputValue.toLowerCase());
                    }}
                    styles={{
                      control: (base, state) => ({
                        ...base,
                        height: '48px',
                        borderRadius: '12px',
                        border: state.isFocused ? '2px solid hsl(197, 88%, 44%)' : '1px solid hsl(214, 32%, 91%)',
                        boxShadow: state.isFocused ? '0 0 0 4px rgba(14, 165, 233, 0.1)' : '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                        '&:hover': {
                          border: '1px solid hsl(214, 32%, 85%)'
                        }
                      }),
                      placeholder: (base) => ({
                        ...base,
                        color: 'hsl(215, 16%, 47%)'
                      })
                    }}
                  />
                  {selectedInstitution === "Otra" && (
                    <input
                      type="text"
                      className="mt-2 w-full border rounded-lg px-3 py-2"
                      placeholder="Escriba el nombre de la institución..."
                      value={otraInstitucion}
                      onChange={e => setOtraInstitucion(e.target.value)}
                      onBlur={() => setValue("institution", otraInstitucion)}
                    />
                  )}
                  {getErrorMessage("institution") && (
                    <p className="text-xs text-red-600 font-medium mt-1">
                      {getErrorMessage("institution")}
                    </p>
                  )}
                </div>
                <FormInput
                  label="Carrera que dicta"
                  icon={<Building2 className="h-4 w-4" />}
                  placeholder="Ej: Ingeniería en Transporte"
                  {...register("careerTaught")}
                  error={getErrorMessage("careerTaught")}
                />
              </FormSection>
            )}

            {profileType === "professional" && (
              <FormSection title="Información Laboral" description="Complete los datos sobre su actividad profesional">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormInput
                    label="Área de trabajo"
                    icon={<Briefcase className="h-4 w-4" />}
                    placeholder="Ej: Logística, Supply Chain, Transporte"
                    {...register("workArea")}
                    error={getErrorMessage("workArea")}
                  />
                  <FormInput
                    label="Cargo"
                    icon={<Briefcase className="h-4 w-4" />}
                    placeholder="Ej: Gerente de Logística"
                    {...register("occupation")}
                    error={getErrorMessage("occupation")}
                  />
                </div>
              </FormSection>
            )}

            {profileType === "groupRepresentative" && (
              <FormSection title="Información del Grupo" description="Complete los datos del grupo que representa">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormInput
                    label="Nombre del grupo"
                    icon={<Users className="h-4 w-4" />}
                    placeholder="Ej: Asociación de Transportistas"
                    {...register("groupName")}
                    error={getErrorMessage("groupName")}
                  />
                  <FormInput
                    label="Municipio del grupo"
                    icon={<Building2 className="h-4 w-4" />}
                    placeholder="Opcional"
                    {...register("groupMunicipality")}
                    error={getErrorMessage("groupMunicipality")}
                  />
                </div>
                <FormInput
                  label="Institución o lugar de trabajo"
                  icon={<Building2 className="h-4 w-4" />}
                  placeholder="Opcional"
                  {...register("institutionOrWorkplace")}
                  error={getErrorMessage("institutionOrWorkplace")}
                />

                <div className="border-t border-slate-200 pt-6">
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Cantidad de Integrantes</h3>
                    <div className="mb-4">
                      <label htmlFor="groupSize" className="block text-sm font-medium text-slate-700 mb-2">
                        ¿Cuántos integrantes tiene el grupo? (sin incluirse usted)
                      </label>
                      <input
                        id="groupSize"
                        type="number"
                        min="1"
                        max="50"
                        value={groupSize || ""}
                        onChange={(e) => {
                          const newSize = parseInt(e.target.value) || 0;
                          if (newSize > 0) {
                            handleGroupSizeChange(newSize);
                          }
                        }}
                        className="w-32 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                        placeholder="0"
                      />
                    </div>
                    {getErrorMessage("groupSize") && (
                      <p className="text-xs text-red-600 font-medium">
                        {getErrorMessage("groupSize")}
                      </p>
                    )}
                  </div>

                  {hasDeclaredGroupSize ? (
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900 mb-4">
                        Datos de los {groupSize} Integrantes
                      </h3>
                      <p className="text-sm text-slate-600 mb-4">
                        Complete los datos de cada integrante. Cada uno recibirá su QR y certificado individual.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-blue-50/50 p-6 rounded-xl border border-blue-100 mb-6 transition-all">
                      <h3 className="text-lg font-semibold text-slate-900 mb-2">Carga Masiva (Recomendado)</h3>
                      <p className="text-sm text-slate-600 mb-4">
                        Para acelerar el registro, puede descargar nuestra plantilla, completarla y subirla aquí. Si lo prefiere, indique el número de integrantes arriba para cargarlos a mano.
                      </p>

                      {excelFile ? (
                        <div className="bg-white p-4 rounded-lg border border-slate-200 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <FileSpreadsheet className="text-green-600 w-8 h-8" />
                            <div>
                              <p className="font-semibold text-slate-800 text-sm">{excelFile.name}</p>
                              <p className="text-xs text-slate-500">{(excelFile.size / 1024).toFixed(1)} KB</p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={removeFile}
                            className="p-2 text-red-500 hover:bg-red-50 rounded-full transition-colors"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <div
                            {...getRootProps()}
                            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors duration-200 ${isDragActive ? 'border-congress-blue bg-blue-50/80' : 'border-blue-200 hover:border-congress-blue/50 hover:bg-white/50'
                              }`}
                          >
                            <input {...getInputProps()} />
                            <UploadCloud className="mx-auto h-12 w-12 text-congress-blue/60 mb-3" />
                            <p className="font-medium text-slate-800">
                              {isDragActive ? "Suelte el archivo aquí" : "Arrastre el archivo Excel o haga clic para buscar"}
                            </p>
                            <p className="text-xs text-slate-500 mt-2">Solo .xlsx, .xls o .csv</p>
                          </div>
                          <div className="text-center">
                            <a
                              href="/plantilla_inscripcion_grupos.xlsx"
                              download
                              className="inline-flex items-center gap-2 text-sm font-semibold text-congress-blue hover:text-congress-cyan transition-colors"
                            >
                              <FileSpreadsheet className="w-4 h-4" />
                              Descargar Plantilla Oficial
                            </a>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {hasDeclaredGroupSize && groupSize > 0 && (
                    <div className="space-y-6">
                      {fields.map((item, index) => {
                        const member = watch(`groupMembers.${index}`);
                        const completedFields = [member?.firstName, member?.lastName, member?.dni, member?.email].filter(Boolean).length;
                        const isComplete = completedFields === 4;

                        return (
                          <div key={item.id} className={`rounded-xl p-6 space-y-4 ${isComplete ? 'bg-green-50 border-2 border-green-200' : 'bg-slate-50'}`}>
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium text-slate-900">
                                Integrante #{index + 1}
                                {isComplete && <span className="ml-2 text-green-600">✓</span>}
                              </h4>
                              <span className="text-sm text-slate-500">
                                {completedFields}/4 campos completos
                              </span>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <FormInput
                                label="Nombre"
                                icon={<User className="h-4 w-4" />}
                                {...register(`groupMembers.${index}.firstName`)}
                                error={getErrorMessage(`groupMembers.${index}.firstName`)}
                              />
                              <FormInput
                                label="Apellido"
                                icon={<User className="h-4 w-4" />}
                                {...register(`groupMembers.${index}.lastName`)}
                                error={getErrorMessage(`groupMembers.${index}.lastName`)}
                              />
                              <FormInput
                                label="DNI"
                                icon={<IdCard className="h-4 w-4" />}
                                {...register(`groupMembers.${index}.dni`)}
                                error={getErrorMessage(`groupMembers.${index}.dni`)}
                                maxLength={8}
                                placeholder="12345678"
                                onInput={(e: React.FormEvent<HTMLInputElement>) => {
                                  const target = e.target as HTMLInputElement;
                                  target.value = target.value.replace(/\D/g, "").slice(0, 8);
                                }}
                              />
                              <FormInput
                                type="email"
                                label="Email"
                                icon={<Mail className="h-4 w-4" />}
                                {...register(`groupMembers.${index}.email`)}
                                error={getErrorMessage(`groupMembers.${index}.email`)}
                              />
                            </div>
                          </div>
                        );
                      })}

                      {getErrorMessage("groupMembers") && (
                        <p className="text-xs text-red-600 font-medium mt-4">
                          {getErrorMessage("groupMembers")}
                        </p>
                      )}
                    </div>
                  )}
                  {excelFile && hasDeclaredGroupSize && (
                    <div className="mt-6 flex justify-end">
                      <button
                        type="button"
                        onClick={removeFile}
                        className="flex items-center gap-2 text-sm font-medium text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        Descartar archivo y lista
                      </button>
                    </div>
                  )}
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
                    He leído y acepto las <TermsAndConditionsModal type="asistente" /> del Congreso de Logística y Transporte.
                  </label>
                  {getErrorMessage("aceptaTyC") && (
                    <p className="text-xs text-red-600 font-medium mt-1">
                      {getErrorMessage("aceptaTyC")}
                    </p>
                  )}
                </div>
              </div>
              <FormButton
                type="submit"
                fullWidth
                size="lg"
                isLoading={isSubmitting}
                icon={<CheckCircle className="h-5 w-5" />}
              >
                {isSubmitting ? "Registrando..." : "Registrar Participante"}
              </FormButton>
            </div>
          </form>
        </FormCard>
      </div>
    </div>
  );
};

export default RegistroParticipantes;
