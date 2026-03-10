# Congreso UNAB 2026

## Descripción
Plataforma integral para la gestión, difusión y administración del **Congreso de Logística UNAB**.  
Este sistema permite la gestión de disertantes, asistentes, empresas y la generación automatizada de certificados y acreditaciones QR.

## Tecnologías
- **Frontend**: React + Vite + TailwindCSS + Framer Motion.
- **Backend**: Django REST Framework + SQLite 3 (Producción recomendada: PostgreSQL).
- **Herramientas**: Supabase (Storage), SMTP (Email).

## Estructura del repositorio
- `client/`: Aplicación frontend.
- `backend/`: API y lógica de negocio.
- `shared/`: Recursos compartidos.
- `docs/`: Documentación, guías y notas históricas.

## Instalación y Ejecución

### 1. Requisitos previos
- Node.js >= 18.
- Python >= 3.10.

### 2. Configuración del Backend
```bash
cd backend
python -m venv venv
# Activar venv (Windows: .\venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python manage.py runserver
```

### 3. Configuración del Frontend
```bash
# En el root del proyecto
pnpm install # o npm install
pnpm run dev
```

---
*Desarrollado de forma individual como plataforma de gestión para el Congreso UNAB.*
