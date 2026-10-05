import React, { useState, useRef, useCallback } from 'react';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  X,
  AlertCircle,
  RefreshCw,
  UserCheck,
  ServerCrash,
  FileX,
  Info
} from 'lucide-react';
import { API_BASE, postWithCsrf } from '../lib/api';

// Constantes de seguridad y validación de cliente
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_EXTENSION = '.xlsx';

// Estructuras de respuesta de la API de Django REST Framework
export interface ErrorDetalleFila {
  fila: number;
  columna: string;
  valor: string | number | null;
  mensaje: string;
}

export interface PersonalAcreditado {
  id: number;
  nombre: string;
  apellido: string;
  dni: string;
  cargo: string;
  email: string;
}

export interface RespuestaExito {
  mensaje: string;
  empresa: {
    id: number;
    nombre: string;
  };
  total_procesados: number;
  registros: PersonalAcreditado[];
}

export interface RespuestaErrorDetallada {
  error: string;
  detalles: ErrorDetalleFila[];
}

interface CargaPreacreditacionEmpresaProps {
  empresaId?: number | string;
  nombreEmpresa?: string;
  onSuccess?: (respuesta: RespuestaExito) => void;
  onCancel?: () => void;
}

export const CargaPreacreditacionEmpresa: React.FC<CargaPreacreditacionEmpresaProps> = ({
  empresaId,
  nombreEmpresa,
  onSuccess,
  onCancel
}) => {
  // Hooks de estado local (React state management)
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  
  // Estados de retroalimentación de la API
  const [clientError, setClientError] = useState<string | null>(null);
  const [serverValidationError, setServerValidationError] = useState<RespuestaErrorDetallada | null>(null);
  const [genericServerError, setGenericServerError] = useState<string | null>(null);
  const [exito, setExito] = useState<RespuestaExito | null>(null);

  // Hook useRef para manipular directamente el elemento <input type="file" />
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Limpia el input del archivo y resetea los estados de error/éxito
   */
  const limpiarInputArchivo = () => {
    setFile(null);
    setClientError(null);
    setServerValidationError(null);
    setGenericServerError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Validación del lado del cliente antes del POST HTTP:
   * 1. Extensión exclusivamente .xlsx
   * 2. Tamaño máximo de 5MB
   */
  const validarArchivoCliente = (archivo: File): boolean => {
    setClientError(null);
    setServerValidationError(null);
    setGenericServerError(null);

    // 1. Verificar Extensión
    const nombreMinusculas = archivo.name.toLowerCase();
    if (!nombreMinusculas.endsWith(ALLOWED_EXTENSION)) {
      setClientError(
        `Formato de archivo no válido. Se requiere un archivo de Excel con extensión ${ALLOWED_EXTENSION}.`
      );
      return false;
    }

    // 2. Verificar Tamaño Máximo (5 MB)
    if (archivo.size > MAX_FILE_SIZE_BYTES) {
      const tamanoMB = (archivo.size / (1024 * 1024)).toFixed(2);
      setClientError(
        `El archivo pesa ${tamanoMB} MB. El límite máximo de subida es de ${MAX_FILE_SIZE_MB} MB.`
      );
      return false;
    }

    return true;
  };

  // Manejo de eventos del Input tipo Archivo
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const archivoSeleccionado = e.target.files[0];
      if (validarArchivoCliente(archivoSeleccionado)) {
        setFile(archivoSeleccionado);
      } else {
        setFile(null);
      }
    }
  };

  // Manejo de eventos de Arrastrar y Soltar (Drag & Drop)
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) setIsDragging(true);
  }, [isDragging]);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (isUploading) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const archivoSoltado = e.dataTransfer.files[0];
      if (validarArchivoCliente(archivoSoltado)) {
        setFile(archivoSoltado);
      } else {
        setFile(null);
      }
      e.dataTransfer.clearData();
    }
  }, [isUploading]);

  /**
   * Envío del archivo a la API de Django REST Framework
   */
  const handleUpload = async () => {
    if (!file) {
      setClientError('Por favor selecciona el archivo PREACREDITACION EMPRESAS.xlsx para continuar.');
      return;
    }

    if (!validarArchivoCliente(file)) {
      return;
    }

    // Activar estado de carga y bloquear botones
    setIsUploading(true);
    setServerValidationError(null);
    setGenericServerError(null);
    setClientError(null);
    setExito(null);

    const formData = new FormData();
    formData.append('archivo', file);
    if (empresaId) {
      formData.append('empresa_id', String(empresaId));
    }

    const url = empresaId
      ? `${API_BASE}/empresas/${empresaId}/preacreditacion/`
      : `${API_BASE}/empresas/carga-preacreditacion/`;

    try {
      const response = await postWithCsrf(url, formData, true);
      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        // TAREA 1: Éxito -> Mostrar confirmación clara y LIMPIAR EL INPUT DEL ARCHIVO
        limpiarInputArchivo();
        setExito(data as RespuestaExito);
        if (onSuccess) {
          onSuccess(data as RespuestaExito);
        }
      } else if (response.status === 400) {
        // TAREA 2: Error 400 de Validación por Fila -> Renderizar detalles por fila
        if (data.detalles && Array.isArray(data.detalles)) {
          setServerValidationError({
            error: data.error || 'Se encontraron errores de validación en la plantilla de Excel.',
            detalles: data.detalles
          });
        } else if (typeof data.error === 'string') {
          setGenericServerError(data.error);
        } else {
          setGenericServerError('Error de validación en los datos del archivo Excel.');
        }
      } else if (response.status >= 500) {
        // TAREA 3: Error de Servidor (HTTP 500+) -> Mensaje genérico para reintentar más tarde
        setGenericServerError('Ocurrió un error interno en el servidor (HTTP 500). Por favor, intenta de nuevo más tarde.');
      } else {
        setGenericServerError(data.error || data.detail || `Ocurrió un error inesperado (Código ${response.status}). Intenta nuevamente más tarde.`);
      }
    } catch (error: unknown) {
      // TAREA 3: Error de Red -> Mensaje genérico para reintentar más tarde
      console.error('Error de red/servidor al procesar archivo:', error);
      setGenericServerError('No se pudo establecer conexión con el servidor. Por favor, verifica tu red e intenta más tarde.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden transition-all">
      {/* Header del Componente */}
      <div className="px-6 py-5 bg-gradient-to-r from-slate-950 via-indigo-950 to-slate-900 text-white flex items-center justify-between border-b border-indigo-900/40">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 bg-indigo-500/20 rounded-xl border border-indigo-400/30 shadow-inner">
            <FileSpreadsheet className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold tracking-tight">Carga de Preacreditación de Personal</h3>
            <p className="text-xs text-slate-300">
              {nombreEmpresa ? `Empresa: ${nombreEmpresa}` : 'Subida de archivo PREACREDITACION EMPRESAS.xlsx'}
            </p>
          </div>
        </div>
        {onCancel && (
          <button
            onClick={onCancel}
            disabled={isUploading}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50"
            title="Cerrar ventana"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="p-6 space-y-6">
        {/* TAREA 1: RENDERIZADO CONDICIONAL DE ÉXITO (HTTP 200) */}
        {exito ? (
          <div className="space-y-6 animate-fadeIn">
            {/* Banner de Éxito y Limpieza de Input */}
            <div className="p-5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-2xl flex items-start space-x-4 shadow-sm">
              <div className="p-2 bg-emerald-500 text-white rounded-xl shadow">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h4 className="font-extrabold text-emerald-950 dark:text-emerald-200 text-base">
                  ¡Preacreditación Procesada Exitosamente!
                </h4>
                <p className="text-sm text-emerald-800 dark:text-emerald-300 mt-1">
                  Se importaron correctamente <span className="font-extrabold text-emerald-950 dark:text-white">{exito.total_procesados}</span> empleado(s) pertenecientes a{' '}
                  <span className="font-bold">{exito.empresa?.nombre || 'la empresa'}</span>.
                </p>
                <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2 italic flex items-center gap-1">
                  <Info className="w-3.5 h-3.5" /> El input de archivo ha sido limpiado para evitar cargas duplicadas.
                </p>
              </div>
            </div>

            {/* Listado del Personal Registrado */}
            {exito.registros && exito.registros.length > 0 && (
              <div className="space-y-2.5">
                <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-emerald-500" />
                  Personal Registrado en la Base de Datos ({exito.registros.length})
                </h5>
                <div className="max-h-64 overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                  <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                    <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 uppercase text-[10px] tracking-wider sticky top-0 border-b border-slate-200 dark:border-slate-700">
                      <tr>
                        <th className="px-3 py-2.5 font-bold">DNI</th>
                        <th className="px-3 py-2.5 font-bold">Nombre y Apellido</th>
                        <th className="px-3 py-2.5 font-bold">Cargo</th>
                        <th className="px-3 py-2.5 font-bold">Email</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
                      {exito.registros.map((person) => (
                        <tr key={person.id} className="hover:bg-slate-100/60 dark:hover:bg-slate-800/40">
                          <td className="px-3 py-2 font-mono font-bold text-slate-900 dark:text-slate-100">{person.dni}</td>
                          <td className="px-3 py-2 font-medium">{person.nombre} {person.apellido}</td>
                          <td className="px-3 py-2 text-slate-600 dark:text-slate-400">{person.cargo}</td>
                          <td className="px-3 py-2 font-mono text-slate-500">{person.email}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Acción para Cargar Otro Archivo */}
            <div className="flex justify-end pt-2 border-t border-slate-200 dark:border-slate-800">
              <button
                onClick={() => setExito(null)}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold transition-all shadow-md flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Cargar Otro Archivo
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Input de Archivo y Zona de Drag & Drop */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !isUploading && fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
                isDragging
                  ? 'border-indigo-500 bg-indigo-50/60 dark:bg-indigo-950/40 scale-[1.01]'
                  : file
                  ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20'
                  : 'border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 bg-slate-50/50 dark:bg-slate-800/30'
              } ${isUploading ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`}
            >
              {/* Input HTML strictly accepts .xlsx */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                onChange={handleFileSelect}
                disabled={isUploading}
                className="hidden"
              />

              {!file ? (
                <div className="flex flex-col items-center justify-center space-y-3.5">
                  <div className="p-4 bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-2xl shadow-inner">
                    <Upload className="w-8 h-8 animate-bounce" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      Arrastra tu archivo Excel aquí o{' '}
                      <span className="text-indigo-600 dark:text-indigo-400 underline decoration-2 underline-offset-2">
                        haz clic para explorar
                      </span>
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5">
                      Solo se admite el archivo oficial <span className="font-bold text-slate-700 dark:text-slate-300">PREACREDITACION EMPRESAS.xlsx</span> (Máximo {MAX_FILE_SIZE_MB}MB)
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between p-3.5 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center space-x-3.5 truncate">
                    <FileSpreadsheet className="w-9 h-9 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                    <div className="text-left truncate">
                      <p className="text-sm font-bold text-slate-900 dark:text-white truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB • Archivo .xlsx seleccionado
                      </p>
                    </div>
                  </div>
                  {!isUploading && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        limpiarInputArchivo();
                      }}
                      className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/50 rounded-lg transition-colors"
                      title="Remover archivo"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Error de Validación Previa en Cliente */}
            {clientError && (
              <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 rounded-xl flex items-start space-x-3 text-amber-900 dark:text-amber-200 text-sm animate-fadeIn">
                <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Validación del Navegador:</span> {clientError}
                </div>
              </div>
            )}

            {/* TAREA 3: ERROR DE SERVIDOR (HTTP 500) O ERROR DE RED (Mensaje Genérico) */}
            {genericServerError && (
              <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 rounded-xl flex items-start space-x-3 text-rose-900 dark:text-rose-200 text-sm animate-fadeIn">
                <ServerCrash className="w-5 h-5 text-rose-600 dark:text-rose-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Atención:</span> {genericServerError}
                </div>
              </div>
            )}

            {/* TAREA 2: DETALLE DE ERRORES POR FILA (HTTP 400 Bad Request) */}
            {serverValidationError && (
              <div className="space-y-4 animate-fadeIn">
                {/* Banner de Transacción Cancelada (All-or-Nothing) */}
                <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 rounded-xl flex items-start space-x-3 text-rose-900 dark:text-rose-200 shadow-sm">
                  <AlertTriangle className="w-5 h-5 text-rose-600 dark:text-rose-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-extrabold text-sm text-rose-950 dark:text-rose-100">
                      Transacción Cancelada Completa (All-or-Nothing)
                    </h5>
                    <p className="text-xs text-rose-800 dark:text-rose-300 mt-0.5">
                      {serverValidationError.error || 'No se guardó ningún registro en la base de datos debido a que se encontraron discrepancias:'}
                    </p>
                  </div>
                </div>

                {/* Lista de Alertas Destacadas por Fila: 'Error en la Fila X: [Descripción]' */}
                <div className="space-y-2">
                  <h6 className="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400 flex items-center gap-1.5">
                    <FileX className="w-4 h-4" />
                    Alertas por Fila ({serverValidationError.detalles.length})
                  </h6>

                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {serverValidationError.detalles.map((det, index) => (
                      <div
                        key={index}
                        className="p-3 bg-rose-100/60 dark:bg-rose-950/50 border-l-4 border-rose-600 dark:border-rose-500 rounded-r-xl text-xs text-slate-800 dark:text-slate-200 flex items-start space-x-2.5 shadow-xs"
                      >
                        <span className="px-2 py-0.5 bg-rose-600 text-white font-mono font-bold rounded text-[11px] flex-shrink-0">
                          Error en la Fila {det.fila}
                        </span>
                        <div className="flex-1">
                          <span className="font-bold text-slate-900 dark:text-white">
                            [{det.columna}]:
                          </span>{' '}
                          {det.mensaje}{' '}
                          {det.valor !== null && det.valor !== undefined && String(det.valor) !== '' && (
                            <span className="font-mono text-slate-500 dark:text-slate-400">
                              (Valor ingresado: "{String(det.valor)}")
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tabla de Errores por Fila y Columna */}
                <div className="rounded-xl border border-rose-200 dark:border-rose-900 overflow-hidden bg-white dark:bg-slate-900 shadow-sm">
                  <div className="px-3 py-2 bg-rose-100/80 dark:bg-rose-950 text-rose-900 dark:text-rose-200 text-xs font-bold border-b border-rose-200 dark:border-rose-900">
                    Resumen Consolidado de Errores
                  </div>
                  <div className="max-h-52 overflow-y-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 uppercase text-[10px] tracking-wider sticky top-0 border-b border-slate-200 dark:border-slate-700">
                        <tr>
                          <th className="px-3 py-2 text-center w-20">Fila</th>
                          <th className="px-3 py-2">Columna</th>
                          <th className="px-3 py-2">Valor Falla</th>
                          <th className="px-3 py-2">Causa del Error</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                        {serverValidationError.detalles.map((err, idx) => (
                          <tr key={idx} className="hover:bg-rose-50/40 dark:hover:bg-rose-950/30">
                            <td className="px-3 py-2 text-center font-mono font-bold text-rose-600 dark:text-rose-400">
                              #{err.fila}
                            </td>
                            <td className="px-3 py-2 font-semibold text-slate-900 dark:text-slate-100">{err.columna}</td>
                            <td className="px-3 py-2 font-mono text-slate-500 dark:text-slate-400 max-w-[140px] truncate">
                              {err.valor !== null && err.valor !== undefined && String(err.valor) !== '' ? String(err.valor) : <span className="italic text-slate-400">(Vacío)</span>}
                            </td>
                            <td className="px-3 py-2 text-rose-700 dark:text-rose-300 font-medium">{err.mensaje}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* Spinner de Carga mientras Petición esté en Curso */}
            {isUploading && (
              <div className="p-4 bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 rounded-xl space-y-3">
                <div className="flex items-center justify-between text-xs text-indigo-700 dark:text-indigo-300 font-bold">
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-indigo-600 dark:text-indigo-400" />
                    Validando plantilla y procesando transacciones...
                  </span>
                  <span>En curso</span>
                </div>
                <div className="w-full bg-indigo-200 dark:bg-indigo-900 rounded-full h-2 overflow-hidden">
                  <div className="bg-indigo-600 h-2 rounded-full animate-pulse" />
                </div>
              </div>
            )}

            {/* Botones de Acción del Formulario */}
            <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-200 dark:border-slate-800">
              {onCancel && (
                <button
                  type="button"
                  onClick={onCancel}
                  disabled={isUploading}
                  className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors disabled:opacity-50"
                >
                  Cancelar
                </button>
              )}
              <button
                type="button"
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white rounded-xl text-sm font-semibold shadow-md hover:shadow-indigo-500/20 transition-all flex items-center space-x-2 disabled:cursor-not-allowed"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Procesando...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    <span>Subir y Procesar Archivo</span>
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CargaPreacreditacionEmpresa;
