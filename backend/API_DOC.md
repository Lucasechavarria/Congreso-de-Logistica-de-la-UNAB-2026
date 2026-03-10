### Registrar Asistencia (Escaneo QR)

**POST** `/api/registrar-asistencia/`

Permite marcar la asistencia de un participante usando su email o ID (por ejemplo, tras escanear el QR).

#### Body (JSON)

```json
{
  "email": "juan@correo.com"
}
```

O bien:

```json
{
  "attendee_id": 1
}
```

#### Respuesta exitosa

```json
{
  "message": "Asistencia registrada",
  "attended_at": "2025-11-15T09:00:00Z"
}
```

#### Si ya estaba registrada

```json
{
  "message": "Asistencia ya registrada",
  "attended_at": "2025-11-15T09:00:00Z"
}
```

#### Errores posibles

- Asistente no encontrado:

```json
{ "error": "Asistente no encontrado" }
```

- Registro de inscripción no encontrado:

```json
{ "error": "Registro de inscripción no encontrado" }
```

- Faltan datos:

```json
{ "error": "Debe enviar email o attendee_id" }
```

# API de Inscripción Congreso UNaB

## Endpoints REST

### Inscripción Individual

**POST** `/api/inscripcion/`

#### Body (JSON)

```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@correo.com",
  "phone": "+54 11 1234 5678",
  "company_name": "Empresa S.A.",
  "position": "Estudiante",
  "participant_type": "estudiante"
}
```

#### Respuesta exitosa

```json
{
  "message": "Inscripción exitosa",
  "attendee": {
    "id": 1,
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@correo.com",
    "phone": "+54 11 1234 5678",
    "company": null,
    "company_name": "Empresa S.A.",
    "position": "Estudiante",
    "participant_type": "estudiante",
    "registered_at": "2025-08-24T12:34:56Z",
    "qr_code": "/media/qr_codes/qr_juan@correo.com.png"
  }
}
```

#### Errores posibles

- Faltan campos obligatorios:

```json
{
  "error": "Faltan campos obligatorios",
  "missing_fields": ["first_name", "participant_type"]
}
```

- Datos inválidos:

```json
{
  "error": "Datos inválidos",
  "details": { "email": ["Enter a valid email address."] }
}
```

---

### Inscripción Grupal

**POST** `/api/inscripcion-grupal/`

#### Body (JSON)

```json
{
  "company": {
    "name": "Empresa S.A.",
    "contact_email": "contacto@empresa.com",
    "contact_phone": "+54 11 9876 5432"
  },
  "attendees": [
    {
      "first_name": "Ana",
      "last_name": "García",
      "email": "ana@empresa.com",
      "phone": "+54 11 1111 2222",
      "position": "Gerente",
      "participant_type": "gerente"
    }
    // ...más asistentes
  ]
}
```

#### Respuesta exitosa

```json
{
  "message": "Inscripción grupal exitosa",
  "company": {
    "id": 1,
    "name": "Empresa S.A.",
    "contact_email": "contacto@empresa.com",
    "contact_phone": "+54 11 9876 5432"
  },
  "attendees": [
    {
      "id": 2,
      "first_name": "Ana",
      "last_name": "García",
      "email": "ana@empresa.com",
      "phone": "+54 11 1111 2222",
      "company": 1,
      "position": "Gerente",
      "participant_type": "gerente",
      "registered_at": "2025-08-24T12:34:56Z",
      "qr_code": "/media/qr_codes/qr_ana@empresa.com.png"
    }
    // ...más asistentes
  ]
}
```

#### Errores posibles

- Faltan datos de empresa:

```json
{ "error": "Faltan los datos de la empresa (company)" }
```

- Faltan campos en empresa:

```json
{
  "error": "Faltan campos obligatorios en la empresa",
  "missing_fields": ["name"]
}
```

- Faltan asistentes:

```json
{ "error": "Debe enviar una lista de asistentes (attendees)" }
```

- Faltan campos en asistente:

```json
{ "error": "Faltan campos en asistente #1", "missing_fields": ["email"] }
```

- Datos inválidos:

```json
{ "error": "Datos inválidos en la empresa", "details": { ... } }
```

---

## Notas

- Todos los campos deben enviarse en formato JSON.
- El campo `company` en inscripción individual puede ser `null` o el id de una empresa existente.
- El campo `participant_type` debe ser uno de: `estudiante`, `profesor`, `gerente`, `ponente`, `otro`.
- El campo `qr_code` en la respuesta es la URL de la credencial QR generada.
