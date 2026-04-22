# 💎 Catálogo de Skills: Congreso UNAB 2026

He "instalado" un conjunto de habilidades técnicas directamente en la base de código para que podamos construir con estándares de alta calidad desde el primer momento.

## 🎨 Frontend & UI/UX

### 1. Animaciones Premium (`use-premium-animation.ts`)
**Ubicación:** `client/hooks/use-premium-animation.ts`
*   **Skill:** Permite implementar scroll dinámico y entradas escalonadas con `Framer Motion`.
*   **Uso:**
    ```tsx
    const { scale, opacity } = usePremiumScroll();
    return <motion.div style={{ scale, opacity }}>...</motion.div>
    ```

### 2. Manejador de API Seguro (`api-handler.ts`)
**Ubicación:** `client/lib/api-handler.ts`
*   **Skill:** Centraliza las peticiones al backend de Django con validación de tipos mediante **Zod**.
*   **Uso:**
    ```tsx
    const { data, error } = await safeApiRequest(fetch('/api/v1/data'), MySchema);
    ```

---

## ⚙️ Backend & DB

### 3. Base de API Premium (`skills.py`)
**Ubicación:** `backend/core/skills.py`
*   **Skill:** Una clase `PremiumAPIView` para Django que estandariza las respuestas (JSON uniforme) y el logging de errores.
*   **Uso:**
    ```python
    class MyView(PremiumAPIView):
        def get(self, request):
            return self.success_response(data={"key": "value"})
    ```

### 4. Optimización PostgreSQL
*   **Skill:** Configuración de índices y transacciones atómicas habilitada en el core.

---

## 🏗️ Arquitectura y Estándares de Ingeniería

Para este proyecto, aplicamos una arquitectura de **Separación de Responsabilidades** (SoC) y **Clean Code**.

### 1. TypeScript & React (Frontend)
*   **🚫 Cero `any`:** El uso de `any` está prohibido. En su lugar, se utilizan Genéricos (`<T>`), Interfaces, Tipos de Unión o `unknown` con guardias de tipo.
*   **Custom Hooks:** La lógica de negocio se extrae a hooks para mantener los componentes puramente visuales.
*   **Inmutabilidad:** Uso estricto de spreads y métodos inmutables para el manejo de estado.
*   **Atomic Design:** Organización de componentes en átomos, moléculas y organismos para máxima reutilización.

### 2. Django & PostgreSQL (Backend)
*   **Normalización 3NF:** Todas las tablas de la base de datos deben cumplir al menos con la **Tercera Forma Normal (3NF)** para evitar redundancias y anomalías.
*   **Modelos "Gordos", Vistas "Flacas":** La lógica de negocio reside en los modelos de Django o en *Services*, no en las vistas.
*   **Type Hinting:** Uso de anotaciones de tipo en Python para mejorar la legibilidad y detectar errores con `mypy`.
*   **Serialización Robusta:** Validación estricta en DRF para asegurar que solo datos limpios lleguen a PostgreSQL.

### 3. Combinación Estratégica (The Bridge)
*   **Contrato de Datos:** El esquema de **Zod** en el frontend debe ser un espejo del **Serializer** en el backend.
*   **Manejo de Errores Unificado:** Todas las excepciones del backend se mapean a un formato JSON estándar que el `api-handler` del frontend entiende y muestra vía Toasts.
*   **CORS & Security:** Configuración estricta de dominios permitidos y protección CSRF/JWT en cada transacción.

---

## 🚀 ¿Cómo seguir?
Estas herramientas están listas para ser usadas. Si quieres que implemente una nueva página o feature, usaré estas **skills** automáticamente para asegurar que el resultado sea **Premium**.

> [!TIP]
> Si encuentras un `any` en el código existente, es una oportunidad de refactorización inmediata para elevar la deuda técnica.
