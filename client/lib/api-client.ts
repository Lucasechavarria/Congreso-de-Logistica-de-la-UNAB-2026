import { z } from "zod";
import { getCookie, cleanupSessionCookies } from "./utils";
import { API_BASE } from "./api";

export interface RequestOptions {
  headers?: Record<string, string>;
  credentials?: "include" | "omit" | "same-origin";
  retries?: number;
  retryDelayMs?: number;
  schema?: z.ZodSchema<any>;
}

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Configuración de petición segura que omite el body y headers restrictivos de RequestInit
 * para permitir cualquier payload (objeto JSON, FormData, etc.) y headers clave-valor simples.
 */
export interface SecureRequestConfig extends Omit<RequestInit, "body" | "headers">, RequestOptions {
  body?: any;
}

/**
 * Método unificado de bajo nivel para realizar peticiones HTTP de forma segura.
 * Se separa de la definición del objeto literal para evitar errores de contexto de 'this' en TypeScript.
 */
async function executeRequest<T>(
  path: string,
  config: SecureRequestConfig
): Promise<ApiResponse<T>> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const retries = config.retries ?? 2;
  const retryDelayMs = config.retryDelayMs ?? 300;
  const method = config.method || "GET";

  // Manejo transparente de token CSRF para operaciones de modificación
  let csrfToken = "";
  if (method !== "GET" && method !== "HEAD") {
    csrfToken = getCookie("csrftoken") || "";
  }

  const headers = {
    Accept: "application/json",
    ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
    ...config.headers,
  } as Record<string, string>;

  const isFormData = config.body instanceof FormData;
  
  // No agregar Content-Type si es FormData (el navegador lo establece con las fronteras del boundary)
  if (!isFormData && config.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const fetchOptions: RequestInit = {
    method,
    headers,
    credentials: config.credentials || "include",
    body: isFormData ? config.body : (config.body ? JSON.stringify(config.body) : undefined),
  };

  let attempt = 0;
  while (attempt <= retries) {
    try {
      const response = await fetch(url, fetchOptions);

      // Si obtenemos error 403 por CSRF, limpiamos cookies y reintentamos una vez
      if (response.status === 403 && method !== "GET") {
        const text = await response.clone().text();
        if (text.includes("CSRF") || text.includes("csrf")) {
          console.warn("[API Client] Error CSRF. Limpiando cookies y reintentando...");
          cleanupSessionCookies();
          const freshCsrf = getCookie("csrftoken") || "";
          if (headers) {
            headers["X-CSRFToken"] = freshCsrf;
          }
          attempt++;
          continue; // Reintentar inmediatamente
        }
      }

      // Si es un error de servidor (5xx) o de tasa límite (429), reintentar con backoff exponencial
      if ((response.status >= 500 || response.status === 429) && attempt < retries) {
        attempt++;
        const backoff = retryDelayMs * Math.pow(2, attempt);
        console.warn(`[API Client] Error ${response.status}. Reintentando en ${backoff}ms...`);
        await delay(backoff);
        continue;
      }

      // Procesar respuesta exitosa o error HTTP controlado (4xx)
      const contentType = response.headers.get("content-type");
      const isJson = contentType && contentType.includes("application/json");

      if (!response.ok) {
        if (isJson) {
          const errorData = await response.json();
          const errorMsg = errorData.detail || errorData.message || `Error ${response.status}`;
          return {
            data: null,
            error: typeof errorMsg === "object" ? JSON.stringify(errorMsg) : errorMsg,
            status: response.status,
          };
        }
        const text = await response.text();
        return {
          data: null,
          error: text.substring(0, 100) || `Error ${response.status}`,
          status: response.status,
        };
      }

      const rawData = isJson ? await response.json() : null;

      // Validar esquema Zod si se proporciona uno
      if (config.schema && rawData) {
        const validation = config.schema.safeParse(rawData);
        if (!validation.success) {
          console.error("[API Client] Error de Validación Zod:", validation.error);
          return {
            data: null,
            error: "La respuesta del servidor no tiene un formato válido.",
            status: response.status,
          };
        }
        return { data: validation.data as T, error: null, status: response.status };
      }

      return { data: rawData as T, error: null, status: response.status };
    } catch (error: unknown) {
      attempt++;
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      if (attempt <= retries) {
        const backoff = retryDelayMs * Math.pow(2, attempt);
        console.warn(`[API Client] Error de conexión: ${errorMessage}. Reintentando en ${backoff}ms...`);
        await delay(backoff);
      } else {
        console.error("[API Client] Falla de conexión definitiva:", error);
        return {
          data: null,
          error: "Error de red: No se pudo conectar con el servidor.",
          status: 0,
        };
      }
    }
  }

  return {
    data: null,
    error: "Error inesperado al realizar la petición.",
    status: 0,
  };
}

/**
 * Cliente API premium, ciberseguro, estructurado y de bajo impacto.
 * Cuenta con manejo transparente de CSRF, reintentos automáticos con exponencial backoff,
 * tipado fuerte mediante TypeScript y esquemas Zod.
 */
export const apiClient = {
  async get<T>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return executeRequest<T>(path, { method: "GET", ...options });
  },

  async post<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return executeRequest<T>(path, { method: "POST", body, ...options });
  },

  async put<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return executeRequest<T>(path, { method: "PUT", body, ...options });
  },

  async patch<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return executeRequest<T>(path, { method: "PATCH", body, ...options });
  },

  async delete<T>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return executeRequest<T>(path, { method: "DELETE", ...options });
  },

  /**
   * Método core unificado para realizar peticiones HTTP de forma segura
   */
  request: executeRequest,
};
