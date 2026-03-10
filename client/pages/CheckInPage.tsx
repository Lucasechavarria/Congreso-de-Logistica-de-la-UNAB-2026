import { useState } from "react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { QrReader } from "react-qr-reader";
import { Label } from "@/components/ui/label";
import { API_HOST } from "@/lib/api";

export default function CheckInPage() {
  const [qrCode, setQrCode] = useState<string>("");
  const [manualCode, setManualCode] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleScan = async (data: string | null) => {
    if (data) {
      setQrCode(data);
      await processCheckIn(data);
    }
  };

  const handleError = (err: Error) => {
    console.error(err);
    toast.error("Error al escanear QR", {
      description: "Asegúrate de que la cámara esté funcionando correctamente.",
    });
  };

  const processCheckIn = async (code: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_HOST}/api/checkin/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ codigo: code }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Error desconocido en el check-in");
      }

      toast.success("Check-in Exitoso", {
        description: `Bienvenido/a ${result.asistente.nombre_completo}!`,
      });
    } catch (error) {
      toast.error("Error en el Check-in", {
        description:
          error instanceof Error
            ? error.message
            : "No se pudo completar el check-in.",
      });
    } finally {
      setLoading(false);
      setQrCode(""); // Limpiar el código QR después de procesar
      setManualCode(""); // Limpiar el código manual
    }
  };

  const handleManualCheckIn = async () => {
    if (manualCode) {
      await processCheckIn(manualCode);
    } else {
      toast.warning("Ingresa un código para el check-in manual.");
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Panel de Check-in
          </h1>
          <p className="text-xl text-gray-600">
            Escanea el código QR o ingresa el código manualmente para registrar
            la asistencia.
          </p>
        </div>

        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Realizar Check-in</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col items-center space-y-4">
              <p className="text-lg font-semibold">Escáner de Código QR</p>
              <div className="w-full max-w-sm border rounded-lg overflow-hidden">
                <QrReader
                  onResult={(result, error) => {
                    if (!!result) {
                      handleScan(result?.getText());
                    }

                    if (!!error) {
                      // handleError(error);
                    }
                  }}
                  constraints={{ facingMode: "environment" }}
                  scanDelay={500} // Retraso para evitar múltiples escaneos rápidos
                  videoContainerStyle={{ width: "100%", paddingTop: "100%" }} // Para mantener el aspecto cuadrado
                  videoStyle={{ objectFit: "cover" }} // Para que el video ocupe todo el espacio
                />
              </div>
              {qrCode && (
                <p className="text-sm text-gray-500">
                  Código Escaneado: {qrCode}
                </p>
              )}
            </div>

            <div className="relative flex items-center">
              <div className="flex-grow border-t border-gray-300"></div>
              <span className="flex-shrink mx-4 text-gray-500">O</span>
              <div className="flex-grow border-t border-gray-300"></div>
            </div>

            <div className="space-y-4">
              <Label htmlFor="manual-code">Ingreso Manual de Código</Label>
              <Input
                id="manual-code"
                placeholder="Ingresa el código QR aquí"
                value={manualCode}
                onChange={(e) => setManualCode(e.target.value)}
              />
              <Button
                onClick={handleManualCheckIn}
                className="w-full"
                disabled={loading}
              >
                {loading ? "Procesando..." : "Realizar Check-in Manual"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
