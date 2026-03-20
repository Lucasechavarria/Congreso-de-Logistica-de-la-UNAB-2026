import { useState, useEffect } from 'react';
import { API_HOST } from '@/lib/api';

export interface Edicion {
  id: number;
  anio: number;
  nombre: string;
  activa: boolean;
}

export const useEdiciones = () => {
  const [ediciones, setEdiciones] = useState<Edicion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEdiciones = async () => {
      try {
        const response = await fetch(`${API_HOST}/api/ediciones/`);
        if (!response.ok) throw new Error('Error al cargar ediciones');
        const data = await response.json();
        setEdiciones(data);
      } catch (err) {
        console.error('Error fetching ediciones:', err);
        setError('Error al cargar ediciones');
      } finally {
        setLoading(false);
      }
    };
    fetchEdiciones();
  }, []);

  return { ediciones, loading, error };
};
