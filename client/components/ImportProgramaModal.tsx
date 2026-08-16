import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Checkbox,
  CircularProgress,
  Alert,
  IconButton,
  Divider,
  Stack
} from '@mui/material';
import {
  CloudUpload,
  FileDownload,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Close,
  Refresh,
  SystemUpdateAlt,
  AddCircleOutline
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { API_HOST } from '@/lib/api';

type RowAnalysis = {
  num_fila: number;
  id_actividad: number | null;
  titulo: string;
  hora_inicio: string;
  hora_fin: string;
  aula: string;
  categoria: string;
  disertantes: string;
  empresas: string;
  descripcion: string;
  estado: string;
  estado_fila: 'SIN_CAMBIOS' | 'NUEVO' | 'MODIFICADO' | 'ERROR';
  diff?: Record<string, { antes: string; ahora: string }>;
  errores: string[];
  advertencias: string[];
};

type AnalysisResumen = {
  total: number;
  sin_cambios: number;
  nuevos: number;
  modificados: number;
  errores: number;
  advertencias: number;
};

interface ImportProgramaModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportProgramaModal: React.FC<ImportProgramaModalProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [importing, setImporting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [resumen, setResumen] = useState<AnalysisResumen | null>(null);
  const [filas, setFilas] = useState<RowAnalysis[]>([]);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);

  // Limpiar estado al abrir/cerrar
  const handleReset = () => {
    setFile(null);
    setLoading(false);
    setImporting(false);
    setErrorMsg(null);
    setSuccessMsg(null);
    setResumen(null);
    setFilas([]);
    setSelectedRows([]);
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  // Subir archivo para Pre-flight Analysis (dry-run)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      analyzeFile(selectedFile);
    }
  };

  const analyzeFile = async (targetFile: File) => {
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    setResumen(null);
    setFilas([]);

    const formData = new FormData();
    formData.append('file', targetFile);

    try {
      const res = await fetch(`${API_HOST}/api/programa/preview-excel/`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (res.ok && data.success) {
        setResumen(data.resumen);
        setFilas(data.filas);

        // Auto-seleccionar todas las filas que NO sean ERROR ni SIN_CAMBIOS
        const defaultSelected = data.filas
          .filter((f: RowAnalysis) => f.estado_fila === 'NUEVO' || f.estado_fila === 'MODIFICADO')
          .map((f: RowAnalysis) => f.num_fila);
        setSelectedRows(defaultSelected);

        // Si todo es 100% verde sin errores ni advertencias, notificar
        if (data.resumen.errores === 0 && data.resumen.advertencias === 0) {
          setSuccessMsg("🟢 Análisis completado: Todas las filas son 100% válidas.");
        }
      } else {
        setErrorMsg(data.error || "Ocurrió un error al analizar la planilla Excel.");
      }
    } catch (err: any) {
      setErrorMsg("Error de conexión al servidor: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  // Confirmar Importación de las filas seleccionadas (commit=True)
  const handleConfirmImport = async () => {
    if (!file) return;

    setImporting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('filas_aprobadas', JSON.stringify(selectedRows));

    try {
      const res = await fetch(`${API_HOST}/api/programa/import-excel/`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (res.ok && data.success) {
        setSuccessMsg(`✅ ${data.mensaje}`);
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      } else {
        setErrorMsg(data.error || "Ocurrió un error al guardar las filas en el sistema.");
      }
    } catch (err: any) {
      setErrorMsg("Error de conexión al procesar la importación: " + (err.message || err));
    } finally {
      setImporting(false);
    }
  };

  // Handlers para selección de filas
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allValid = filas
        .filter(f => f.estado_fila !== 'ERROR')
        .map(f => f.num_fila);
      setSelectedRows(allValid);
    } else {
      setSelectedRows([]);
    }
  };

  const handleToggleRow = (numFila: number) => {
    setSelectedRows(prev =>
      prev.includes(numFila) ? prev.filter(r => r !== numFila) : [...prev, numFila]
    );
  };

  // Descargar Plantilla
  const handleDownloadTemplate = () => {
    window.open(`${API_HOST}/api/programa/plantilla-excel/`, '_blank');
  };

  // Exportar Actual
  const handleExportCurrent = () => {
    window.open(`${API_HOST}/api/programa/exportar-excel/`, '_blank');
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        style: {
          borderRadius: 16,
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          color: '#f8fafc',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              display: 'flex'
            }}
          >
            <CloudUpload sx={{ color: '#fff' }} />
          </Box>
          <Box>
            <Typography variant="h6" fontWeight="700" sx={{ color: '#fff' }}>
              Ingesta e Importación del Programa (.xlsx)
            </Typography>
            <Typography variant="caption" sx={{ color: '#94a3b8' }}>
              Análisis Pre-flight & Sincronización Diferencial Inteligente
            </Typography>
          </Box>
        </Box>
        <IconButton onClick={handleClose} sx={{ color: '#94a3b8' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />

      <DialogContent sx={{ p: 3 }}>
        {/* Barra superior de plantillas y exportación */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" mb={3}>
          <Button
            variant="outlined"
            startIcon={<FileDownload />}
            onClick={handleDownloadTemplate}
            sx={{
              borderColor: '#38bdf8',
              color: '#38bdf8',
              '&:hover': { borderColor: '#7dd3fc', backgroundColor: 'rgba(56, 189, 248, 0.1)' }
            }}
          >
            Descargar Plantilla Oficial (.xlsx)
          </Button>

          <Button
            variant="outlined"
            startIcon={<SystemUpdateAlt />}
            onClick={handleExportCurrent}
            sx={{
              borderColor: '#a855f7',
              color: '#c084fc',
              '&:hover': { borderColor: '#e9d5ff', backgroundColor: 'rgba(168, 85, 247, 0.1)' }
            }}
          >
            Exportar Grilla Actual (.xlsx)
          </Button>
        </Stack>

        {/* Zona de Carga de Archivo */}
        {!file && (
          <Box
            component="label"
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 4,
              border: '2px dashed rgba(56, 189, 248, 0.4)',
              borderRadius: 4,
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.05)'
              }
            }}
          >
            <input type="file" accept=".xlsx, .xls" hidden onChange={handleFileChange} />
            <CloudUpload sx={{ fontSize: 48, color: '#38bdf8', mb: 1 }} />
            <Typography variant="subtitle1" fontWeight="600" sx={{ color: '#f8fafc' }}>
              Arrastra tu archivo Excel aquí o haz clic para seleccionar
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', mt: 0.5 }}>
              Soporta planillas .xlsx estructuradas con horarios y salas
            </Typography>
          </Box>
        )}

        {/* Spinner de Análisis */}
        {loading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 5 }}>
            <CircularProgress size={48} sx={{ color: '#38bdf8', mb: 2 }} />
            <Typography variant="body1" sx={{ color: '#cbd5e1' }}>
              Ejecutando Pre-flight Analysis & Smart Delta Sync...
            </Typography>
          </Box>
        )}

        {/* Mensajes de Alerta */}
        {errorMsg && (
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }} onClose={() => setErrorMsg(null)}>
            {errorMsg}
          </Alert>
        )}

        {successMsg && (
          <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }} onClose={() => setSuccessMsg(null)}>
            {successMsg}
          </Alert>
        )}

        {/* Resumen del Análisis */}
        {resumen && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Box
              sx={{
                p: 2,
                mb: 3,
                borderRadius: 3,
                backgroundColor: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.08)'
              }}
            >
              <Typography variant="subtitle2" sx={{ color: '#94a3b8', mb: 1.5, textTransform: 'uppercase', letterSpacing: 1 }}>
                Resumen de Análisis Pre-flight:
              </Typography>
              <Stack direction="row" spacing={1.5} flexWrap="wrap">
                <Chip label={`Total: ${resumen.total}`} variant="outlined" sx={{ color: '#fff', borderColor: '#64748b' }} />
                <Chip label={`🟢 Nuevos: ${resumen.nuevos}`} sx={{ backgroundColor: 'rgba(34, 197, 94, 0.2)', color: '#4ade80' }} />
                <Chip label={`🟡 Modificados: ${resumen.modificados}`} sx={{ backgroundColor: 'rgba(234, 179, 8, 0.2)', color: '#fde047' }} />
                <Chip label={`⚪ Sin Cambios: ${resumen.sin_cambios}`} sx={{ backgroundColor: 'rgba(148, 163, 184, 0.2)', color: '#cbd5e1' }} />
                {resumen.errores > 0 && (
                  <Chip label={`🔴 Errores: ${resumen.errores}`} sx={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5' }} />
                )}
                {resumen.advertencias > 0 && (
                  <Chip label={`⚠️ Advertencias: ${resumen.advertencias}`} sx={{ backgroundColor: 'rgba(249, 115, 22, 0.2)', color: '#ffedd5' }} />
                )}
              </Stack>

              {/* Botón cambiar archivo */}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Button size="small" startIcon={<Refresh />} onClick={() => setFile(null)} sx={{ color: '#94a3b8' }}>
                  Cambiar Archivo Excel
                </Button>
              </Box>
            </Box>

            {/* Tabla de Filas Analizadas */}
            <TableContainer component={Paper} sx={{ maxHeight: 380, backgroundColor: 'rgba(15, 23, 42, 0.8)', borderRadius: 2 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { backgroundColor: '#0f172a', color: '#94a3b8', fontWeight: 700 } }}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        size="small"
                        indeterminate={
                          selectedRows.length > 0 &&
                          selectedRows.length < filas.filter(f => f.estado_fila !== 'ERROR').length
                        }
                        checked={
                          filas.filter(f => f.estado_fila !== 'ERROR').length > 0 &&
                          selectedRows.length === filas.filter(f => f.estado_fila !== 'ERROR').length
                        }
                        onChange={e => handleSelectAll(e.target.checked)}
                        sx={{ color: '#64748b', '&.Mui-checked': { color: '#38bdf8' } }}
                      />
                    </TableCell>
                    <TableCell>Fila</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Título de la Actividad</TableCell>
                    <TableCell>Horario</TableCell>
                    <TableCell>Aula</TableCell>
                    <TableCell>Disertantes</TableCell>
                    <TableCell>Observaciones / Diff</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filas.map(row => {
                    const isSelected = selectedRows.includes(row.num_fila);
                    const isError = row.estado_fila === 'ERROR';

                    return (
                      <TableRow
                        key={row.num_fila}
                        hover
                        selected={isSelected}
                        sx={{
                          '&:nth-of-type(odd)': { backgroundColor: 'rgba(255, 255, 255, 0.02)' },
                          opacity: isError ? 0.7 : 1
                        }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            size="small"
                            disabled={isError}
                            checked={isSelected}
                            onChange={() => handleToggleRow(row.num_fila)}
                            sx={{ color: '#64748b', '&.Mui-checked': { color: '#38bdf8' } }}
                          />
                        </TableCell>

                        <TableCell sx={{ color: '#cbd5e1', fontWeight: 600 }}>{row.num_fila}</TableCell>

                        <TableCell>
                          {row.estado_fila === 'NUEVO' && (
                            <Chip size="small" icon={<AddCircleOutline />} label="NUEVO" color="success" variant="outlined" />
                          )}
                          {row.estado_fila === 'MODIFICADO' && (
                            <Chip size="small" icon={<Warning />} label="MODIFICADO" color="warning" variant="outlined" />
                          )}
                          {row.estado_fila === 'SIN_CAMBIOS' && (
                            <Chip size="small" icon={<CheckCircle />} label="SIN CAMBIOS" color="default" variant="outlined" />
                          )}
                          {row.estado_fila === 'ERROR' && (
                            <Chip size="small" icon={<ErrorIcon />} label="ERROR" color="error" />
                          )}
                        </TableCell>

                        <TableCell sx={{ color: '#f8fafc', fontWeight: 600, maxWidth: 220 }}>
                          {row.titulo || <em style={{ color: '#ef4444' }}>Vacío</em>}
                        </TableCell>

                        <TableCell sx={{ color: '#cbd5e1', whiteSpace: 'nowrap' }}>
                          {row.hora_inicio && row.hora_fin ? `${row.hora_inicio} - ${row.hora_fin}` : '-'}
                        </TableCell>

                        <TableCell sx={{ color: '#cbd5e1' }}>{row.aula}</TableCell>

                        <TableCell sx={{ color: '#cbd5e1', maxWidth: 180 }}>
                          {row.disertantes || <span style={{ color: '#64748b' }}>Sin disertantes</span>}
                        </TableCell>

                        <TableCell sx={{ maxWidth: 250 }}>
                          {/* Errores */}
                          {row.errores.map((err, idx) => (
                            <Typography key={idx} variant="caption" display="block" sx={{ color: '#fca5a5', fontWeight: 600 }}>
                              • {err}
                            </Typography>
                          ))}

                          {/* Advertencias */}
                          {row.advertencias.map((adv, idx) => (
                            <Typography key={idx} variant="caption" display="block" sx={{ color: '#fdba74' }}>
                              ⚠️ {adv}
                            </Typography>
                          ))}

                          {/* Diffs de modificaciones */}
                          {row.diff &&
                            Object.entries(row.diff).map(([key, val]) => {
                              const change = val as { antes: string; ahora: string };
                              return (
                                <Typography key={key} variant="caption" display="block" sx={{ color: '#fef08a' }}>
                                  🔄 <strong>{key}:</strong> {change.antes} ➔ {change.ahora}
                                </Typography>
                              );
                            })}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </motion.div>
        )}
      </DialogContent>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />

      <DialogActions sx={{ p: 2.5, px: 3, justifyContent: 'space-between' }}>
        <Button onClick={handleClose} sx={{ color: '#94a3b8' }}>
          Cancelar
        </Button>

        {resumen && (
          <Button
            variant="contained"
            disabled={selectedRows.length === 0 || importing}
            onClick={handleConfirmImport}
            startIcon={importing ? <CircularProgress size={20} color="inherit" /> : <CheckCircle />}
            sx={{
              background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
              color: '#fff',
              fontWeight: 700,
              px: 3,
              py: 1,
              borderRadius: 2,
              boxShadow: '0 4px 14px 0 rgba(22, 163, 74, 0.39)',
              '&:hover': {
                background: 'linear-gradient(135deg, #15803d 0%, #166534 100%)'
              }
            }}
          >
            {importing
              ? 'Procesando...'
              : `Importar ${selectedRows.length} Filas Aprobadas`}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
