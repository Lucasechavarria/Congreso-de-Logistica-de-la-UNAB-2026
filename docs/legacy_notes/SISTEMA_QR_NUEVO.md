# Sistema de QR Codes - Congreso UNAB

## Nueva Funcionalidad Implementada

Se ha modificado completamente la lógica del sistema según los requerimientos del cliente:

### Cambios Principales

1. **Eliminación de QRs individuales**: Ya no se generan QRs únicos para cada registro
2. **Implementación de QRs estáticos**: Dos QRs fijos para todo el evento
3. **Eliminación de envío de emails en el registro**: No se envían QRs por email
4. **Nueva lógica de confirmación**: La asistencia se confirma mediante verificación de DNI

### QRs Estáticos del Sistema

#### 1. QR Azul - Confirmar Asistencia (para personas ya registradas)

- **URL**: `http://localhost:5173/verificar-dni`
- **Propósito**: Verificar DNI y confirmar asistencia
- **Proceso**:
  1. El asistente escanea el QR azul
  2. Ingresa su DNI en la página
  3. El sistema verifica si está registrado
  4. Se confirma la asistencia y se envía el certificado por email

#### 2. QR Verde - Registro in-situ (para personas no registradas)

- **URL**: `http://localhost:5173/registro-rapido`
- **Propósito**: Registro rápido en el momento del evento
- **Proceso**:
  1. El asistente escanea el QR verde
  2. Completa el formulario de registro
  3. Se registra automáticamente y confirma asistencia
  4. Recibe certificado por email inmediatamente

### Páginas Implementadas

1. **`/verificar-dni`** - Página para confirmar asistencia con DNI
2. **`/registro-rapido`** - Página para registro in-situ
3. **`/generar-qrs`** - Página administrativa para generar e imprimir los QRs estáticos

### Funcionalidades del Backend

- **`/api/verificar-dni/`** - Endpoint para verificar DNI y confirmar asistencia
- **`/api/registro-rapido/`** - Endpoint para registro rápido con confirmación automática
- **`/api/generar-qrs/`** - Endpoint para generar QRs estáticos

### Base de Datos

Los modelos fueron actualizados:

- **Asistente**: Agregados campos `asistencia_confirmada` y `fecha_confirmacion`
- **CodigoQR**: Modelo eliminado (ya no se necesita)
- **Migración**: Se requiere recrear la base de datos

### Instrucciones de Uso

#### Para Organizers del Evento:

1. **Generar QRs**: Ir a `/generar-qrs` para obtener los dos QRs estáticos
2. **Imprimir QRs**: Descargar e imprimir en tamaño grande
3. **Colocar en el evento**:
   - QR Azul: "Confirmar Asistencia" - para registrados
   - QR Verde: "Registro in-situ" - para no registrados

#### Para Asistentes:

1. **Si ya estás registrado**: Escanea QR azul → Ingresa DNI → Recibe certificado
2. **Si no estás registrado**: Escanea QR verde → Completa registro → Recibe certificado

### Panel de Administración

El admin de Django fue actualizado con nuevas funciones:

- Confirmar asistencia masiva
- Enviar certificados
- Ver estado de confirmación de asistentes

### Pasos para Recrear la Base de Datos

```bash
cd backend
rm -f db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### URLs del Sistema

- **Frontend**: `http://localhost:5173`
- **Backend**: `http://127.0.0.1:8000`
- **Admin**: `http://127.0.0.1:8000/admin`

### Certificados

Los certificados se envían automáticamente por email cuando:

- Se confirma asistencia mediante verificación de DNI
- Se completa un registro rápido in-situ

La nueva lógica está completamente implementada y lista para usar.
