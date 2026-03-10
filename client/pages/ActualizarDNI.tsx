import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle2, AlertCircle, Loader2, IdCard, Mail, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function ActualizarDNI() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [asistente, setAsistente] = useState<{ nombre_completo: string; email: string } | null>(null);
  const [dni, setDni] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("Token no proporcionado");
      setLoading(false);
      return;
    }

    // Verificar el token
    fetch(`/api/actualizar-dni/?token=${token}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setAsistente(data.asistente);
        } else {
          setError(data.message || "Token inválido o expirado");
        }
      })
      .catch(() => {
        setError("Error al verificar el token");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const res = await fetch("/api/actualizar-dni/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, dni }),
      });

      const data = await res.json();

      if (data.status === "success") {
        setSuccess(true);
        setTimeout(() => {
          navigate("/");
        }, 3000);
      } else {
        setError(data.message || "Error al actualizar el DNI");
      }
    } catch (err) {
      setError("Error al conectar con el servidor");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-violet-900 to-slate-900 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="w-full max-w-md border-violet-200 shadow-2xl">
            <CardContent className="pt-12 pb-12 text-center">
              <Loader2 className="w-16 h-16 mx-auto mb-6 animate-spin text-violet-600" />
              <p className="text-lg text-gray-600 font-medium">Verificando información...</p>
              <p className="text-sm text-gray-400 mt-2">Por favor espera un momento</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  if (error && !asistente) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-violet-900 to-slate-900 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="w-full max-w-md border-red-200 shadow-2xl">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-10 h-10 text-red-600" />
              </div>
              <CardTitle className="text-2xl text-red-600">Enlace Inválido</CardTitle>
              <CardDescription className="text-base mt-2">
                No pudimos verificar tu solicitud
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="destructive" className="bg-red-50 border-red-200">
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
              <p className="text-sm text-gray-600 text-center">
                Si crees que esto es un error, por favor contacta al equipo organizador.
              </p>
              <Button className="w-full bg-slate-900 hover:bg-slate-800" onClick={() => navigate("/")}>
                Volver al Inicio
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-violet-900 to-slate-900 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
        >
          <Card className="w-full max-w-md border-green-200 shadow-2xl">
            <CardHeader className="text-center pb-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="mx-auto mb-4 w-20 h-20 bg-green-100 rounded-full flex items-center justify-center"
              >
                <CheckCircle2 className="w-12 h-12 text-green-600" />
              </motion.div>
              <CardTitle className="text-2xl text-green-600">¡DNI Actualizado!</CardTitle>
              <CardDescription className="text-base mt-2">
                Tu información ha sido actualizada correctamente
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="bg-green-50 border-green-200">
                <ShieldCheck className="h-5 w-5 text-green-600" />
                <AlertDescription className="text-green-800 ml-2">
                  Tu DNI ha sido registrado exitosamente en nuestro sistema. Ya puedes asistir al congreso sin problemas.
                </AlertDescription>
              </Alert>
              <div className="text-center text-sm text-gray-500">
                <p>Serás redirigido al inicio en unos segundos...</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-violet-900 to-slate-900 p-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-lg"
      >
        <Card className="border-violet-200 shadow-2xl backdrop-blur">
          <CardHeader className="text-center space-y-4 pb-6">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-violet-500 to-violet-700 rounded-full flex items-center justify-center shadow-lg">
              <IdCard className="w-8 h-8 text-white" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold text-gray-900">
                Actualización de DNI
              </CardTitle>
              <CardDescription className="text-base mt-3">
                <span className="block text-gray-600">Congreso de Logística y Transporte</span>
                <span className="block text-gray-600 font-medium mt-1">Universidad Nacional Guillermo Brown</span>
              </CardDescription>
            </div>
            <div className="bg-violet-50 border border-violet-100 rounded-lg p-4 mt-4">
              <p className="text-sm text-gray-700 font-medium mb-1">Datos del Asistente</p>
              <p className="text-lg font-semibold text-violet-900">{asistente?.nombre_completo}</p>
              <div className="flex items-center justify-center gap-2 mt-2 text-sm text-gray-600">
                <Mail className="w-4 h-4" />
                <span>{asistente?.email}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-3">
                <label htmlFor="dni" className="block text-sm font-semibold text-gray-700">
                  Número de DNI
                </label>
                <Input
                  id="dni"
                  type="text"
                  placeholder="Ej: 12345678"
                  value={dni}
                  onChange={(e) => setDni(e.target.value.replace(/\D/g, "").slice(0, 8))}
                  maxLength={8}
                  required
                  className="text-center text-2xl tracking-widest font-mono h-14 border-2 focus:border-violet-500 focus:ring-violet-500"
                />
                <p className="text-xs text-gray-500 text-center flex items-center justify-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  Ingresa entre 7 y 8 dígitos numéricos sin puntos ni espacios
                </p>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Alert variant="destructive" className="bg-red-50 border-red-200">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="ml-2">{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}

              <Button
                type="submit"
                className="w-full h-12 text-base font-semibold bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-700 hover:to-violet-800 shadow-lg"
                disabled={submitting || (dni.length < 7 || dni.length > 8)}
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Actualizando...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5 mr-2" />
                    Confirmar DNI
                  </>
                )}
              </Button>

              <div className="text-center">
                <p className="text-xs text-gray-500">
                  Al confirmar, aceptas que la información proporcionada es correcta.
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="text-center mt-6">
          <p className="text-sm text-gray-300">
            ¿Necesitas ayuda? Contacta al equipo organizador a <a href="mailto:congresologisticaytransporte@unab.edu.ar">congresologisticaytransporte@unab.edu.ar</a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
