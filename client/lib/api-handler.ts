import { z } from "zod";

/**
 * Skill: Safe API Integration
 * Manejador genérico para peticiones API con validación de esquemas Zod y tipado fuerte.
 */
export async function safeApiRequest<T>(
  request: Promise<Response>,
  schema?: z.ZodSchema<T>
): Promise<{ data: T | null; error: string | null }> {
  try {
    const response = await request;
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { 
        data: null, 
        error: errorData.detail || errorData.message || `Error: ${response.status}` 
      };
    }

    const rawData = await response.json();

    if (schema) {
      const validation = schema.safeParse(rawData);
      if (!validation.success) {
        console.error("[API Skill] Validation Error:", validation.error);
        return { data: null, error: "La respuesta del servidor no coincide con el formato esperado." };
      }
      return { data: validation.data, error: null };
    }

    return { data: rawData as T, error: null };
  } catch (e) {
    console.error("[API Skill] Network Error:", e);
    return { data: null, error: "Error de conexión con el servidor." };
  }
}
