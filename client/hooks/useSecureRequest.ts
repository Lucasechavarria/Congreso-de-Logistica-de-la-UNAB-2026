import { useState, useCallback } from "react";
import { apiClient, RequestOptions, ApiResponse } from "../lib/api-client";
import { useToast } from "./use-toast";

export interface SecureRequestOptions<T> extends RequestOptions {
  successMessage?: string;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
}

/**
 * Hook personalizado para realizar llamadas de red seguras en React,
 * manejando automáticamente los estados de carga (loading), error, datos,
 * y mostrando notificaciones visuales (Toasts) automáticas e integradas.
 */
export function useSecureRequest<T, TBody = any>() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);
  const { toast } = useToast();

  const execute = useCallback(
    async (
      method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
      path: string,
      body?: TBody,
      options?: SecureRequestOptions<T>
    ): Promise<ApiResponse<T>> => {
      setLoading(true);
      setError(null);

      const showSuccessToast = options?.showSuccessToast ?? false;
      const showErrorToast = options?.showErrorToast ?? true;

      let result: ApiResponse<T>;
      
      if (method === "GET") {
        result = await apiClient.get<T>(path, options);
      } else if (method === "POST") {
        result = await apiClient.post<T>(path, body, options);
      } else if (method === "PUT") {
        result = await apiClient.put<T>(path, body, options);
      } else if (method === "PATCH") {
        result = await apiClient.patch<T>(path, body, options);
      } else {
        result = await apiClient.delete<T>(path, options);
      }

      setLoading(false);

      if (result.error) {
        setError(result.error);
        
        if (showErrorToast) {
          toast({
            title: "Error en la operación",
            description: result.error,
            variant: "destructive",
          });
        }
        
        if (options?.onError) {
          options.onError(result.error);
        }
      } else if (result.data !== null) {
        setData(result.data);
        
        if (showSuccessToast && options?.successMessage) {
          toast({
            title: "Operación exitosa",
            description: options.successMessage,
          });
        }

        if (options?.onSuccess) {
          options.onSuccess(result.data);
        }
      }

      return result;
    },
    [toast]
  );

  return {
    loading,
    error,
    data,
    execute,
    reset: () => {
      setLoading(false);
      setError(null);
      setData(null);
    },
  };
}
