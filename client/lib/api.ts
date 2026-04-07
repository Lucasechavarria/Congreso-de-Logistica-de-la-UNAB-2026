import { getCookie, cleanupSessionCookies } from './utils';

// Compute API base consistently: VITE_API_URL should be the host (no trailing /api)
// and we append /api here. Falls back to localhost for development.
// API URL resolver
// VITE_API_URL can be either the host (e.g. https://www.example.com) or the full /api base
// We normalize it so API_HOST = scheme://host[:port] and API_BASE = API_HOST + /api
function normalizeUrl(url: string) {
  return url.replace(/\/$/, "");
}

function resolveApiHost(): string {
  const env = (import.meta.env?.VITE_API_URL as string | undefined)?.trim();
  if (env) {
    // If env already ends with /api, strip it to get the host
    const cleaned = normalizeUrl(env);
    const host = cleaned.endsWith('/api') ? cleaned.slice(0, -4) : cleaned;
    const normalized = normalizeUrl(host);
    // If env points to localhost/127/0.0.0.0 but we're in a browser with a non-local origin, prefer window origin
    if (
      typeof window !== 'undefined' &&
      window.location?.origin &&
      !/^(https?:\/\/)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?$/i.test(window.location.origin) &&
      /^(https?:\/\/)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?$/i.test(normalized)
    ) {
      return normalizeUrl(window.location.origin);
    }
    return normalized;
  }
  // Fallback to current site origin when running in the browser
  if (typeof window !== 'undefined' && window.location?.origin) {
    return normalizeUrl(window.location.origin);
  }
  // Last resort: localhost for dev tools without a window
  return 'http://127.0.0.1:8000';
}

export const API_HOST = resolveApiHost();
export const API_BASE = `${API_HOST}/api`;

/**
 * Obtiene un token CSRF fresco del servidor
 * Esto ayuda a evitar problemas con cookies antiguas o tokens expirados
 */
async function ensureCsrfToken(): Promise<string> {
  // Primero intentar obtener el token de la cookie
  let token = getCookie('csrftoken');

  // Si no hay token o está vacío, obtenerlo del servidor
  if (!token) {
    try {
      console.log('[CSRF] No se encontró token en cookie, obteniendo del servidor...');

      // Usar el endpoint dedicado para obtener el token CSRF
      const response = await fetch(`${API_BASE}/csrf/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('[CSRF] Error al obtener token. Status:', response.status);
      }

      // Intentar obtener el token de la respuesta JSON (fallback si cookie tiene HTTPOnly)
      try {
        const data = await response.json();
        if (data.csrfToken) {
          console.log('[CSRF] Token obtenido de respuesta JSON (fallback)');
          return data.csrfToken;
        }
      } catch (e) {
        // Si no hay JSON o no tiene el token, continuar con el método de cookies
      }

      // Esperar un momento para que la cookie se establezca
      await new Promise(resolve => setTimeout(resolve, 150));

      token = getCookie('csrftoken');

      if (!token) {
        console.error('[CSRF] No se pudo obtener token después de GET al endpoint /csrf/');
        console.error('[CSRF] Cookies actuales:', document.cookie);
      } else {
        console.log('[CSRF] Token obtenido exitosamente de cookie');
      }
    } catch (error) {
      console.error('[CSRF] Error al obtener token del servidor:', error);
    }
  }

  if (!token) {
    console.warn('[CSRF] Advertencia: No se pudo obtener token CSRF. Las peticiones POST podrían fallar.');
  }

  return token || '';
}

/**
 * Wrapper para peticiones POST con manejo robusto de CSRF
 */
async function postWithCsrf(url: string, data: any, isFormData: boolean = false): Promise<Response> {
  // Obtener token CSRF fresco
  const csrfToken = await ensureCsrfToken();

  const headers: HeadersInit = {
    'X-CSRFToken': csrfToken,
  };

  // Solo agregar Content-Type si no es FormData
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: isFormData ? data : JSON.stringify(data),
  });

  // Si obtenemos un error 403 de CSRF, limpiar cookies y reintentar UNA vez
  if (response.status === 403) {
    const text = await response.text();
    if (text.includes('CSRF') || text.includes('csrf')) {
      console.warn('Error CSRF detectado. Limpiando cookies y reintentando...');
      cleanupSessionCookies();

      // Obtener un token completamente nuevo
      const newCsrfToken = await ensureCsrfToken();
      headers['X-CSRFToken'] = newCsrfToken;

      // Reintentar la petición
      return await fetch(url, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: isFormData ? data : JSON.stringify(data),
      });
    }
  }

  return response;
}

/**
 * Helper para parsear respuestas JSON con manejo de errores robusto
 */
async function parseResponse(response: Response): Promise<any> {
  const contentType = response.headers.get('content-type');

  // Si no es JSON, intentar leer como texto para ver qué devolvió el servidor
  if (!contentType || !contentType.includes('application/json')) {
    const text = await response.text();
    console.error('Respuesta no es JSON:', text.substring(0, 500));
    throw new Error(`El servidor devolvió ${contentType || 'contenido no JSON'}. Puede ser un error del servidor.`);
  }

  try {
    return await response.json();
  } catch (error) {
    console.error('Error al parsear JSON:', error);
    throw new Error('Error al procesar la respuesta del servidor.');
  }
}

// Función para registrar empresa
// Función para registrar empresa con archivos
export async function registrarEmpresa(data: FormData) {
  const res = await postWithCsrf(`${API_BASE}/registro-empresas/`, data, true);
  return await parseResponse(res);
}

// Función para verificar DNI y confirmar asistencia
export async function verificarDNI(dni: string) {
  const res = await postWithCsrf(`${API_BASE}/verificar-dni/`, { dni });
  return await parseResponse(res);
}

// Función para recuperar datos de asistente por DNI (CRM)
export async function verificarAsistente(dni: string) {
  const res = await fetch(`${API_BASE}/verificar-asistente/${dni}/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  return await parseResponse(res);
}

// Función para recuperar datos de empresa por Email (CRM)
export async function verificarEmpresa(email: string) {
  const res = await fetch(`${API_BASE}/verificar-empresa/${encodeURIComponent(email)}/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  return await parseResponse(res);
}

// Función para recuperar datos de postulante disertante por DNI (CRM)
export async function verificarDisertante(dni: string) {
  const res = await fetch(`${API_BASE}/verificar-disertante/${dni}/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  return await parseResponse(res);
}

// Función para registro rápido in-situ
export async function registroRapido(data: any) {
  const res = await postWithCsrf(`${API_BASE}/registro-rapido/`, data);
  return await parseResponse(res);
}

// Función para generar QRs estáticos
export async function generarQRsEstaticos() {
  const res = await fetch(`${API_BASE}/generar-qrs/`);
  return await parseResponse(res);
}

export async function registrarAsistencia(data: any) {
  const res = await postWithCsrf(`${API_BASE}/registrar-asistencia/`, data);
  return await parseResponse(res);
}

// Utilidades para consumir la API del backend
export async function inscribirIndividual(data: any) {
  const res = await postWithCsrf(`${API_BASE}/registro/`, data);
  return await parseResponse(res);
}

export async function inscribirGrupal(data: any) {
  const res = await postWithCsrf(`${API_BASE}/registro/`, data);
  return await parseResponse(res);
}

// Nueva función para el sistema mejorado de inscripción grupal
export async function inscribirParticipante(data: any) {
  const res = await postWithCsrf(`${API_BASE}/registro/`, data);
  return await parseResponse(res);
}

// Función para registro de disertantes
export async function postularDisertante(data: any) {
  const res = await postWithCsrf(`${API_BASE}/postulaciones-disertantes/`, data);
  return await parseResponse(res);
}

// Función para obtener ofertas laborales con filtros
export async function getOfertasLaborales(params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/bolsa-trabajo/ofertas/${query ? `?${query}` : ''}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });
  return await parseResponse(res);
}

// Función para obtener lista de empresas (para filtros)
export async function getEmpresas() {
  const res = await fetch(`${API_BASE}/empresas/`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });
  return await parseResponse(res);
}
