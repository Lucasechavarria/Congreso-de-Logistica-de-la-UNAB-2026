import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function groupWith<T>(
  arr: T[],
  predicate: (item: T) => string,
): Record<string, T[]> {
  return arr.reduce(
    (acc, item) => {
      const key = predicate(item);
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(item);
      return acc;
    },
    {} as Record<string, T[]>,
  );
}

// Helper para obtener el token CSRF de la cookie
export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Helper para eliminar una cookie específica
export function deleteCookie(name: string): void {
  if (typeof document === 'undefined') return;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname};`;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.${window.location.hostname};`;
}

// Helper para limpiar cookies de sesión antiguas
export function cleanupSessionCookies(): void {
  if (typeof document === 'undefined') return;
  const cookiesToClean = ['csrftoken', 'sessionid'];
  cookiesToClean.forEach(cookieName => {
    deleteCookie(cookieName);
  });
}
