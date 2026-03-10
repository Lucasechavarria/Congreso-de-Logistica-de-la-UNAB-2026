# Manual de Carga Masiva de Asistentes

## 📋 Resumen de Funcionalidades Implementadas

### ✅ Nuevos Tipos de Perfil Agregados:
- **GRADUADO**: Para graduados universitarios
- **OTRO**: Para perfiles que no encajan en las otras categorías

### ✅ Funcionalidades de Carga Masiva:
1. **DNIs Nulos Permitidos**: Los asistentes pueden ser registrados sin DNI
2. **Tipo de Perfil por Defecto**: Si el campo está vacío se asigna automáticamente 'OTRO'  
3. **Rol Específico**: Campo adicional para información como "Colaborador/a Estudiante", "Colaborador/a Docente", etc.
4. **Validación de Emails**: Evita duplicados y valida formato correcto
5. **Envío de Emails Automático**: Opción de enviar emails de confirmación

## 📊 Estructura del Archivo Excel/CSV Esperado

El archivo debe tener las siguientes columnas (nombres exactos):

| Columna | Descripción | Obligatorio | Ejemplo |
|---------|-------------|-------------|---------|
| `NOMBRE` | Nombre del asistente | ✅ Sí | Juan Carlos |
| `Apellido` | Apellido del asistente | ✅ Sí | Pérez |
| `CORREO ELECTRONICO` | Email del asistente | ✅ Sí | juan.perez@example.com |
| `NUMERO DE CELULAR (con codigo de area)` | Teléfono con código de área | ❌ No | +54911123456789 |
| `DNI` | Documento Nacional de Identidad | ❌ No | 12345678 |
| `TIPO DE PERFIL` | Tipo de perfil del asistente | ❌ No* | Visitante |
| `Columna1` | Rol específico adicional | ❌ No | Colaborador/a Estudiante |

*Si está vacío se asigna automáticamente 'OTRO'

### 🔄 Mapeo de Tipos de Perfil

Los valores en la columna `TIPO DE PERFIL` se mapean automáticamente:

| Valor en Excel | Se convierte a | Descripción |
|----------------|----------------|-------------|
| `Visitante` | `VISITOR` | Visitante general |
| `Estudiante` | `STUDENT` | Estudiante universitario |
| `Docente` | `TEACHER` | Docente/Profesor |
| `Profesional` | `PROFESSIONAL` | Profesional del sector |
| `Representante de Grupo` | `GROUP_REPRESENTATIVE` | Representante de grupo |
| `Graduado` | `GRADUADO` | Graduado universitario |
| `Otro` | `OTRO` | Otros perfiles |
| *(vacío)* | `OTRO` | Se asigna automáticamente |

## 🚀 Cómo Usar la Carga Masiva

### 1. Preparar el Archivo Excel
Crea un archivo Excel (.xlsx) o CSV con la estructura indicada arriba.

### 2. Verificar el Endpoint
```bash
# Para ver información del endpoint
GET /api/carga-masiva/

# Respuesta esperada:
{
    "status": "info",
    "message": "Endpoint para carga masiva de asistentes",
    "metodo": "POST",
    "parametros": {
        "archivo": "Archivo Excel (.xlsx, .xls) o CSV (.csv) - REQUERIDO",
        "enviar_emails": "true/false - OPCIONAL (default: true)"
    },
    "estructura_archivo": {
        "columnas_requeridas": ["NOMBRE", "Apellido", "CORREO ELECTRONICO"],
        "columnas_opcionales": [
            "NUMERO DE CELULAR (con codigo de area)",
            "DNI", 
            "TIPO DE PERFIL",
            "Columna1"
        ]
    }
}
```

### 3. Usar la API
```bash
# Endpoint para carga masiva
POST /api/carga-masiva/

# Parámetros:
# - archivo: Archivo Excel/CSV (requerido)
# - enviar_emails: true/false (opcional, default: true)
```

### 4. Ejemplo con curl:
```bash
curl -X POST \
  http://localhost:8000/api/carga-masiva/ \
  -F "archivo=@/ruta/al/archivo.xlsx" \
  -F "enviar_emails=false"
```

### 4. Respuesta Esperada:
```json
{
    "status": "success",
    "message": "Carga masiva completada. 150 registros exitosos, 2 errores.",
    "resultados": {
        "total_procesados": 152,
        "exitosos": 150,
        "errores": 2,
        "emails_enviados": 148,
        "emails_fallidos": 2,
        "detalles": [
            {
                "fila": 2,
                "mensaje": "Asistente creado exitosamente: Juan Carlos Pérez",
                "id": 123
            },
            {
                "fila": 5,
                "error": "Ya existe un asistente con el email: existing@example.com"
            }
        ]
    }
}
```

## 📧 Sistema de Emails de Confirmación

### ¿Se Envían Emails Automáticamente?
**Sí**, por defecto se envían emails de confirmación a todos los asistentes cargados masivamente, pero esto se puede controlar con el parámetro `enviar_emails`.

### Diferencias con la Inscripción Web:
- **Inscripción Web**: Email de confirmación inmediato con todos los datos
- **Carga Masiva**: Email específico para carga masiva que puede solicitar información faltante (como DNI)

### Control de Envío:
```bash
# Con envío de emails (por defecto)
-F "enviar_emails=true"

# Sin envío de emails
-F "enviar_emails=false"
```

## 🛠️ Manejo de la "Columna1"

### Recomendación de Uso:
La **"Columna1"** se ha implementado como campo `rol_especifico` para almacenar información adicional como:
- "Colaborador/a Estudiante"
- "Colaborador/a Docente" 
- "Colaborador/a Graduado"
- Cualquier rol específico adicional

### Ventajas:
1. **Flexibilidad**: Permite agregar contexto adicional al tipo de perfil
2. **Histórico**: Mantiene la información original del Excel
3. **Filtrado**: Puede usarse para filtros y reportes específicos
4. **Opcional**: No es obligatorio, puede estar vacío

## 🔍 Validaciones Implementadas

### ✅ Validaciones que se Realizan:
1. **Email único**: No se permiten emails duplicados
2. **Formato de email**: Validación de formato correcto
3. **Campos obligatorios**: Nombre, apellido y email son requeridos
4. **Tipo de perfil válido**: Se mapea automáticamente a valores válidos
5. **DNI único**: Si se proporciona, debe ser único (pero puede ser nulo)

### ❌ Errores Comunes y Soluciones:
| Error | Solución |
|-------|----------|
| "Ya existe un asistente con el email: ..." | Verificar duplicados en el Excel |
| "Formato de email inválido: ..." | Corregir formato del email |
| "Nombre, apellido y email son obligatorios" | Completar campos vacíos |
| "Columnas faltantes en el archivo: ..." | Verificar nombres exactos de columnas |

## 🎯 Estado Posterior a la Carga

### Campos que se Asignan Automáticamente:
- **Tipo de perfil**: 'OTRO' si está vacío
- **DNI**: Se permite `null` si no se proporciona
- **Asistencia confirmada**: `false` (requiere confirmación posterior)

### Próximos Pasos Recomendados:
1. **Revisión**: Verificar los asistentes cargados en el panel de administración
2. **Confirmaciones**: Los asistentes con DNI nulo recibirán emails para completar datos
3. **Seguimiento**: Monitorear respuestas de confirmación de emails

## 🚨 Notas Importantes

### ⚠️ Antes de la Carga:
- Hacer backup de la base de datos
- Verificar que el archivo tenga la estructura correcta
- Revisar emails duplicados en el Excel

### 📈 Después de la Carga:
- Revisar el reporte de resultados
- Verificar asistentes con errores
- Confirmar que los emails se enviaron correctamente

### 🔧 En Caso de Errores:
- Los errores no detienen la carga completa
- Se procesan todas las filas posibles
- El reporte detalla errores específicos por fila

---

**¡La funcionalidad de carga masiva está lista para usar!** 🎉