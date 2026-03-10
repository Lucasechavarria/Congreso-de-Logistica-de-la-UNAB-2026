# Integración Frontend-Backend: Congreso UNaB

## 1. Configuración de CORS

El backend ya permite peticiones desde el frontend (CORS habilitado).

## 2. Endpoints disponibles

- POST `/api/inscripcion/` — Inscripción individual
- POST `/api/inscripcion-grupal/` — Inscripción grupal

Consulta `backend/API_DOC.md` para detalles de payload y respuestas.

## 3. Ejemplo de integración en React

### Inscripción individual

```js
// src/lib/api.js
export async function inscribirIndividual(data) {
  const res = await fetch("http://127.0.0.1:8000/api/inscripcion/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return await res.json();
}
```

### Uso en el formulario

```js
import { inscribirIndividual } from "../lib/api";

async function handleSubmit(e) {
  e.preventDefault();
  const data = {
    /* ...campos del formulario... */
  };
  const resp = await inscribirIndividual(data);
  if (resp.message) {
    // éxito
  } else {
    // mostrar resp.error y/o resp.details
  }
}
```

### Inscripción grupal

```js
export async function inscribirGrupal(data) {
  const res = await fetch("http://127.0.0.1:8000/api/inscripcion-grupal/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return await res.json();
}
```

## 4. Manejo de errores

- Si falta un campo, la respuesta tendrá `error` y `missing_fields`.
- Si hay error de validación, la respuesta tendrá `error` y `details`.

## 5. Pruebas

- Puedes usar Postman/Insomnia para probar los endpoints antes de conectar el frontend.
- Desde React, asegúrate de que la URL apunte al backend correcto (localhost o producción).

## 6. Notas

- El backend responde en JSON.
- Si usas Vite, configura el proxy para evitar CORS en desarrollo.

```js
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
```

---

¿Dudas? Consulta la documentación o pide ayuda.
