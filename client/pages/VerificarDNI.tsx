import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { CheckCircle, AlertCircle } from "lucide-react";
import { API_HOST } from "@/lib/api";

export default function VerificarDNI() {
  const navigate = useNavigate();
  const [dni, setDni] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [confirmed, setConfirmed] = useState<boolean>(false);
  const [asistente, setAsistente] = useState<any>(null);
  const [showModal, setShowModal] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!dni.trim()) {
      toast.error("Por favor ingresa tu DNI");
      return;
    }

    if (!/^\d{7,8}$/.test(dni)) {
      toast.error("DNI inválido. Debe tener 8 dígitos");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_HOST}/api/verificar-dni/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ dni: dni.trim() }),
      });

      const result = await response.json();

      if (response.status === 404) {
        setShowModal(true);
        return;
      }
      if (!response.ok) {
        throw new Error(result.message || "Error desconocido en la verificación");
      }
      setConfirmed(true);
      setAsistente(result.asistente);
      toast.success("¡Asistencia Confirmada!", {
        description: `Bienvenido/a ${result.asistente.nombre_completo}. Tu certificado ha sido enviado por email.`,
      });
    } catch (error) {
      toast.error("Error en la verificación", {
        description:
          error instanceof Error
            ? error.message
            : "No se pudo verificar el DNI.",
      });
    } finally {
      setLoading(false);
    }
  };

  if (confirmed && asistente) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="flex justify-center mb-6">
            <CheckCircle className="h-16 w-16 text-green-500" />
          </div>
          <h1 className="text-4xl font-bold text-green-600 mb-4">
            ¡Asistencia Confirmada!
          </h1>
          <Card className="mt-8">
            <CardContent className="pt-6">
              <div className="space-y-4 text-left">
                <div>
                  <strong>Nombre:</strong> {asistente.nombre_completo}
                </div>
                <div>
                  <strong>Email:</strong> {asistente.email}
                </div>
                <div>
                  <strong>DNI:</strong> {asistente.dni}
                </div>
              </div>
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <p className="text-green-800 text-center">
                  Tu certificado de asistencia ha sido enviado a tu correo
                  electrónico.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Confirmar Asistencia</h1>
        <p className="text-xl text-gray-600">
          Ingresa tu DNI para confirmar tu asistencia al congreso y recibir tu certificado.
        </p>
      </div>
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="text-center">Verificación de DNI</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dni">Número de DNI</Label>
              <Input
                id="dni"
                type="text"
                placeholder="Ej: 12345678"
                value={dni}
                onChange={(e) => setDni(e.target.value)}
                maxLength={8}
                pattern="[0-9]*"
              />
              <p className="text-sm text-gray-500">Ingresa tu DNI sin puntos ni espacios</p>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Verificando..." : "Confirmar Asistencia"}
            </Button>
          </form>
          <div className="mt-4 p-4 bg-violet-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-violet-500 mt-0.5" />
              <div className="text-sm text-violet-800">
                <p className="font-semibold">Importante:</p>
                <p>
                  Solo puedes confirmar tu asistencia una vez. Tu certificado será enviado automáticamente a tu email registrado.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Modal para DNI no encontrado */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8 text-center animate-fade-in">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-600 mb-2">DNI no registrado</h2>
            <p className="text-gray-700 mb-6">
              No encontramos tu DNI en la base de datos.<br />
              Por favor, realiza tu inscripción rápida para poder confirmar tu asistencia.
            </p>
            <Button
              className="w-full bg-violet-600 hover:bg-violet-700 text-white text-lg py-2 rounded"
              onClick={() => {
                setShowModal(false);
                navigate("/seleccion-registro");
              }}
            >
              Ir a Selección de Registro
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
