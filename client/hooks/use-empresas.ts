import { useState, useEffect } from 'react';
import { API_BASE } from '@/lib/api';

export interface EmpresaAPI {
  id: number;
  nombre_empresa: string;
  logo: string;
  sitio_web?: string;
  descripcion?: string;
}

export interface LogoItem {
  src: string;
  alt: string;
  heightClass?: string;
}

// API base normalizada (siempre termina en /api)
const API_BASE_URL = API_BASE;

// Caché en memoria básico fuera del ciclo de vida del componente
let empresasCache: EmpresaAPI[] | null = null;
let lastFetchTime: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos de caché

export const useEmpresas = (edicionId?: number | null) => {
  const [empresas, setEmpresas] = useState<EmpresaAPI[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchEmpresas = async () => {
      // 1. Usar caché si existe, es válido y NO estamos pidiendo una edición específica
      const now = Date.now();
      if (!edicionId && empresasCache && (now - lastFetchTime < CACHE_DURATION)) {
        if (isMounted) {
          setEmpresas(empresasCache);
          setLoading(false);
        }
        return;
      }

      if (isMounted) {
        setLoading(true);
      }
      if (isMounted) setError(null);

      // 2. Sistema de Timeout usando AbortController
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 segundos

      try {
        const url = edicionId 
          ? `${API_BASE_URL}/empresas/?edicion_id=${edicionId}`
          : `${API_BASE_URL}/empresas/`;
          
        const response = await fetch(url, {
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        // 3. Manejo de Errores Resiliente (Traducción de status)
        if (!response.ok) {
          if (response.status >= 500) {
            throw new Error('El servicio web está temporalmente fuera de línea. Por favor, intente más tarde.');
          } else if (response.status === 404) {
            throw new Error('No se encontraron empresas registradas.');
          } else {
            throw new Error('Hubo un problema al cargar los datos. Por favor, intente nuevamente.');
          }
        }

        const data = await response.json();

        // Actualizar caché solo si es la petición general (sin edicionId)
        if (!edicionId) {
          empresasCache = data;
          lastFetchTime = Date.now();
        }

        if (isMounted) {
          setEmpresas(data);
          setError(null);
        }
      } catch (err: any) {
        if (!isMounted) return;

        let errorMessage = 'Error al cargar la información';
        if (err.name === 'AbortError') {
          errorMessage = 'El servidor tardó demasiado en responder. Por favor, intente más tarde.';
        } else if (err instanceof Error) {
          errorMessage = err.message;
        }

        // Estrategia de Fallback: Si falló pero tenemos data cacheada (aunque esté "stale" o caduca), 
        // simplemente no rompemos la UI, usamos la cacheada y loggeamos el fallo.
        if (!empresasCache) {
          setError(errorMessage);
        } else {
          console.warn("Retrying failed, maintaining stale cache data:", errorMessage);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchEmpresas();

    return () => {
      isMounted = false;
    };
  }, [edicionId]);

  // Convertir empresas de la API al formato LogoItem esperado por los componentes
  const DOMAIN_PROD = "https://www.congresologistica.unab.edu.ar";
  const logosForCarousel: LogoItem[] = empresas.map(empresa => {
    let src = "";
    const foto = empresa.logo;

    if (foto && typeof foto === "string" && foto.length > 5) {
      if (foto.startsWith("http")) {
        src = foto;
      } else {
        // Cleaning potential double 'media/' paths and prepend API_BASE_URL (or just API host)
        const cleanPath = foto.replace(/^\/?(media\/)?/, "");
        src = `${API_BASE_URL.replace('/api', '')}/media/${cleanPath}`;
      }
    }

    // Force HTTPS if applicable
    if (src.startsWith('http://') && !src.includes("localhost") && !src.includes("127.0.0.1")) {
      src = src.replace('http://', 'https://');
    }
    return {
      src,
      alt: empresa.nombre_empresa,
      heightClass: "h-12"
    };
  });

  return {
    empresas,
    logosForCarousel,
    loading,
    error
  };
};