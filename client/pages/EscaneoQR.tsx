import React, { useState } from "react";
import { useZxing } from "react-zxing";
import { registrarAsistencia } from "../lib/api";
import {
  FormInput,
  FormButton,
  FormCard,
  FormSection
} from "@/components/ui/modern-form";
import { API_HOST } from "@/lib/api";
import {
  QrCode,
  Camera,
  Mail,
  IdCard,
  CheckCircle,
  AlertCircle,
  Download,
  User
} from "lucide-react";

export default function EscaneoQR() {
  const [valor, setValor] = useState("");
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [asistencia, setAsistencia] = useState<any>(null);
  const [certId, setCertId] = useState<number | null>(null);
  const [showScanner, setShowScanner] = useState(false);

  const { ref } = useZxing({
    onDecodeResult(result) {
      setValor(result.getText());
      setShowScanner(false);
      handleSubmitQR(result.getText());
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleSubmitQR(valor);
  };

  const handleSubmitQR = async (scanValue: string) => {
    setMensaje(null);
    setError(null);
    setAsistencia(null);

    let payload: any = {};
    let cleanValor = scanValue;

    // Si el valor viene en formato 'asistente:<id>:<email>', extraer solo el email
    if (cleanValor.startsWith("asistente:")) {
      const partes = cleanValor.split(":");
      if (partes.length === 3) {
        cleanValor = partes[2];
      } else if (partes.length === 2) {
        cleanValor = partes[1];
      }
    }

    if (/^\d+$/.test(cleanValor)) {
      payload.attendee_id = Number(cleanValor);
    } else if (cleanValor.includes("@")) {
      payload.email = cleanValor;
    } else {
      setError("Debes ingresar un email o ID válido.");
      return;
    }

    try {
      const resp = await registrarAsistencia(payload);
      if (resp.message) {
        setMensaje(resp.message);
        setAsistencia(resp);
        if (resp.certificate_id) {
          setCertId(resp.certificate_id);
        } else {
          setCertId(null);
        }
      } else {
        setError("Respuesta inesperada del servidor.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Error al conectar con el servidor.");
    }
  };

  const descargarCertificado = () => {
    if (certId) {
      const url = `${API_HOST}/api/certificado/${certId}/`;
      window.open(url, "_blank");
    }
  };

  return (
    <div className="min-h-screen form-bg-gradient py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <FormCard
          title="Registro de Asistencia"
          description="Escanee el código QR o ingrese el email/ID del participante para confirmar su asistencia"
        >
          <div className="space-y-8">
            {/* Scanner QR */}
            <FormSection
              title="Escaneo de Código QR"
              description="Use la cámara para escanear códigos QR de los participantes"
            >
              <div className="flex flex-col items-center space-y-4">
                {!showScanner ? (
                  <FormButton
                    type="button"
                    onClick={() => setShowScanner(true)}
                    variant="outline"
                    icon={<Camera className="h-5 w-5" />}
                    fullWidth
                  >
                    Activar Cámara para Escanear QR
                  </FormButton>
                ) : (
                  <div className="space-y-4 w-full">
                    <div className="relative bg-black rounded-xl overflow-hidden">
                      <video
                        ref={ref}
                        className="w-full h-64 object-cover"
                        style={{ maxWidth: '100%' }}
                      />
                      <div className="absolute inset-0 border-2 border-congress-cyan rounded-xl opacity-50"></div>
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                        <div className="w-32 h-32 border-4 border-congress-cyan rounded-lg animate-pulse"></div>
                      </div>
                    </div>
                    <FormButton
                      type="button"
                      onClick={() => setShowScanner(false)}
                      variant="ghost"
                      fullWidth
                    >
                      Cerrar Cámara
                    </FormButton>
                  </div>
                )}
              </div>
            </FormSection>

            {/* Separador */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-slate-600 font-medium">o ingrese manualmente</span>
              </div>
            </div>

            {/* Formulario manual */}
            <FormSection
              title="Registro Manual"
              description="Ingrese el email o ID del participante"
            >
              <form onSubmit={handleSubmit} className="space-y-6">
                <FormInput
                  label="Email o ID del Participante"
                  icon={<QrCode className="h-4 w-4" />}
                  placeholder="correo@ejemplo.com o 12345"
                  value={valor}
                  onChange={(e) => setValor(e.target.value)}
                  hint="Ingrese el email registrado o el ID numérico del participante"
                />

                <FormButton
                  type="submit"
                  fullWidth
                  icon={<CheckCircle className="h-5 w-5" />}
                >
                  Registrar Asistencia
                </FormButton>
              </form>
            </FormSection>

            {/* Resultados */}
            {(mensaje || error || asistencia) && (
              <FormSection title="Resultado del Registro">
                {/* Mensaje de éxito */}
                {mensaje && (
                  <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                    <div className="flex items-start">
                      <CheckCircle className="h-6 w-6 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-green-900 mb-2">¡Asistencia Registrada!</h3>
                        <p className="text-green-800">{mensaje}</p>

                        {asistencia && (
                          <div className="mt-4 bg-white rounded-lg p-4 border border-green-200">
                            <h4 className="font-medium text-slate-900 mb-2 flex items-center">
                              <User className="h-4 w-4 mr-2" />
                              Información del Participante
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                              {asistencia.attendee_name && (
                                <p><strong>Nombre:</strong> {asistencia.attendee_name}</p>
                              )}
                              {asistencia.attendee_email && (
                                <p><strong>Email:</strong> {asistencia.attendee_email}</p>
                              )}
                              {asistencia.attendee_id && (
                                <p><strong>ID:</strong> {asistencia.attendee_id}</p>
                              )}
                              {asistencia.attendance_time && (
                                <p><strong>Hora:</strong> {new Date(asistencia.attendance_time).toLocaleString('es-AR')}</p>
                              )}
                            </div>
                          </div>
                        )}

                        {certId && (
                          <div className="mt-4">
                            <FormButton
                              type="button"
                              onClick={descargarCertificado}
                              variant="secondary"
                              icon={<Download className="h-4 w-4" />}
                            >
                              Descargar Certificado
                            </FormButton>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Mensaje de error */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                    <div className="flex items-start">
                      <AlertCircle className="h-6 w-6 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-red-900 mb-2">Error en el Registro</h3>
                        <p className="text-red-800">{error}</p>
                      </div>
                    </div>
                  </div>
                )}
              </FormSection>
            )}

            {/* Información adicional */}
            <div className="bg-violet-50 border border-violet-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-violet-900 mb-3">Instrucciones de Uso</h3>
              <ul className="text-violet-800 space-y-2 text-sm">
                <li className="flex items-start">
                  <QrCode className="h-4 w-4 mt-0.5 mr-2 flex-shrink-0" />
                  Escanee el código QR del participante con la cámara
                </li>
                <li className="flex items-start">
                  <Mail className="h-4 w-4 mt-0.5 mr-2 flex-shrink-0" />
                  O ingrese manualmente el email de registro
                </li>
                <li className="flex items-start">
                  <IdCard className="h-4 w-4 mt-0.5 mr-2 flex-shrink-0" />
                  También puede usar el ID numérico del participante
                </li>
              </ul>
            </div>
          </div>
        </FormCard>
      </div>
    </div>
  );
}
