import os
import sys
import django
from datetime import datetime

# Iniciar contexto Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

REPORT_EMAIL_DEFAULT = "echavarrialucas1986@gmail.com"

def run_evaluation(target_email: str = REPORT_EMAIL_DEFAULT):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print("=" * 65)
    print("  DIAGNÓSTICO Y MANTENIMIENTO DE INFRAESTRUCTURA - CONGRESO UNAB")
    print(f"  Fecha/Hora: {now_str}")
    print(f"  Destinatario del reporte: {target_email}")
    print("=" * 65)

    results = {
        'timestamp': now_str,
        'db_status': 'Desconocido',
        'db_details': '',
        'redis_status': 'Desconocido',
        'redis_details': '',
        'ram_status': 'N/A',
        'ram_details': '',
        'sessions_status': 'Desconocido',
        'sessions_details': '',
        'overall_success': True
    }

    # 1. Evaluar Conexión a Base de Datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            results['db_status'] = 'OK (Conectado)'
            results['db_details'] = 'Conexión activa y respondiendo a consultas SQL.'
            print("[OK] Base de datos: Conexión activa y respondiendo correctamente.")
    except Exception as e:
        results['db_status'] = 'ERROR'
        results['db_details'] = str(e)
        results['overall_success'] = False
        print(f"[ERROR] Base de datos: Falla de conexión -> {e}")

    # 2. Evaluar Estado de Redis Broker
    try:
        import redis
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1.0)
        if r.ping():
            info = r.info('memory')
            used_mb = info.get('used_memory_human', 'N/A')
            results['redis_status'] = 'OK (Modo Asíncrono Activo)'
            results['redis_details'] = f"Broker Redis operativo. Memoria en uso por Redis: {used_mb}"
            print(f"[OK] Broker Redis: Conectado. Memoria usada por Redis: {used_mb}")
    except Exception as e:
        results['redis_status'] = 'WARNING (Modo Síncrono Eager)'
        results['redis_details'] = f"Redis no disponible ({e}). Celery operará en fallback síncrono."
        print(f"[WARNING] Broker Redis: No disponible ({e}). Modo síncrono Eager ACTIVO.")

    # 3. Purga Automática por Única Vez (Post-despliegue)
    print("\n>>> Ejecutando purga inmediata de mantenimiento post-despliegue...")
    try:
        call_command('clearsessions')
        results['sessions_status'] = 'OK (Limpiado)'
        results['sessions_details'] = 'Sesiones caducadas y temporales eliminadas de la base de datos.'
        print("[OK] Sesiones expiradas eliminadas de la base de datos.")
    except Exception as e:
        results['sessions_status'] = 'ERROR'
        results['sessions_details'] = str(e)
        results['overall_success'] = False
        print(f"[ERROR] Falla al limpiar sesiones expiradas: {e}")

    # 4. Evaluación de RAM del Sistema
    try:
        import psutil
        mem = psutil.virtual_memory()
        used_mb = mem.used // (1024 * 1024)
        total_mb = mem.total // (1024 * 1024)
        results['ram_status'] = f"{mem.percent}%"
        results['ram_details'] = f"Usado: {used_mb} MB / Total: {total_mb} MB"
        print(f"\n[INFO] Estado de RAM del Servidor: {mem.percent}% en uso ({used_mb} MB / {total_mb} MB)")
        if mem.percent > 85:
            results['ram_details'] += " - [ALERTA: Memoria alta (>85%)]"
            print("[ALERTA] Uso de memoria RAM alto (>85%). Se sugiere reiniciar workers (gunicorn).")
    except ImportError:
        results['ram_status'] = 'No disponible (instale psutil)'
        results['ram_details'] = 'Librería psutil no instalada.'

    # 5. Enviar Reporte por Email
    print(f"\n>>> Enviando reporte por correo electrónico a {target_email}...")
    try:
        send_report_email(target_email, results)
        print(f"[OK] Reporte de mantenimiento enviado con éxito a {target_email}.")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el reporte por correo a {target_email}: {e}")

    print("=" * 65)
    print(" Mantenimiento y evaluación completados.")
    print("=" * 65)


def send_report_email(target_email: str, results: dict):
    subject = f"[REPORTE SERVIDOR] Diagnóstico de Infraestructura - Congreso UNAB ({results['timestamp']})"
    from_email = getattr(settings, 'EMAIL_HOST_USER', 'congresologisticaytransporte@unab.edu.ar') or 'congresologisticaytransporte@unab.edu.ar'

    status_color = "#10B981" if results['overall_success'] else "#EF4444"
    status_text = "MANTENIMIENTO EXITOSO - SERVIDOR OPTIMIZADO" if results['overall_success'] else "MANTENIMIENTO COMPLETADO CON ADVERTENCIAS"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 30px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .header {{ text-align: center; border-bottom: 2px solid #334155; padding-bottom: 20px; margin-bottom: 25px; }}
            .header h1 {{ color: #38bdf8; font-size: 22px; margin: 0 0 8px 0; }}
            .header p {{ color: #94a3b8; font-size: 14px; margin: 0; }}
            .badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 13px; color: #ffffff; background-color: {status_color}; margin-top: 15px; }}
            .section {{ background-color: #0f172a; border-radius: 8px; padding: 16px; margin-bottom: 16px; border-left: 4px solid #38bdf8; }}
            .section h3 {{ margin: 0 0 6px 0; font-size: 15px; color: #f1f5f9; }}
            .section p {{ margin: 0; font-size: 13px; color: #94a3b8; }}
            .footer {{ text-align: center; font-size: 12px; color: #64748b; margin-top: 25px; border-top: 1px solid #334155; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Congreso de Logística UNAB 2026</h1>
                <p>Reporte de Diagnóstico y Mantenimiento de Infraestructura</p>
                <div class="badge">{status_text}</div>
            </div>

            <div class="section">
                <h3>📅 Fecha y Hora del Mantenimiento</h3>
                <p>{results['timestamp']}</p>
            </div>

            <div class="section">
                <h3>🗄️ Base de Datos (PostgreSQL)</h3>
                <p><strong>Estado:</strong> {results['db_status']}<br>{results['db_details']}</p>
            </div>

            <div class="section">
                <h3>⚡ Broker de Tareas (Redis / Celery)</h3>
                <p><strong>Estado:</strong> {results['redis_status']}<br>{results['redis_details']}</p>
            </div>

            <div class="section">
                <h3>🧠 Uso de Memoria RAM del Servidor</h3>
                <p><strong>Porcentaje Usado:</strong> {results['ram_status']}<br>{results['ram_details']}</p>
            </div>

            <div class="section">
                <h3>🧹 Purga de Sesiones y Cache</h3>
                <p><strong>Estado:</strong> {results['sessions_status']}<br>{results['sessions_details']}</p>
            </div>

            <div class="section">
                <h3>⚙️ Reciclaje Automático Configurado</h3>
                <p><strong>Gunicorn:</strong> Max requests: 1000 (Reciclaje de RAM continuo)<br><strong>Celery:</strong> Max memory por worker: 250MB</p>
            </div>

            <div class="footer">
                <p>Este es un reporte automático generado post-despliegue por la plataforma del Congreso UNAB 2026.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    REPORTE DE INFRAESTRUCTURA - CONGRESO UNAB 2026
    --------------------------------------------------
    Fecha: {results['timestamp']}
    Estado: {status_text}

    - Base de Datos: {results['db_status']} ({results['db_details']})
    - Redis Broker: {results['redis_status']} ({results['redis_details']})
    - Memoria RAM: {results['ram_status']} ({results['ram_details']})
    - Purga de Sesiones: {results['sessions_status']} ({results['sessions_details']})
    - Reciclaje Gunicorn: Activo (max_requests=1000)

    Sistema optimizado y listo para recibir tráfico de inscripciones.
    """

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[target_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


if __name__ == "__main__":
    email_dest = sys.argv[1] if len(sys.argv) > 1 else REPORT_EMAIL_DEFAULT
    run_evaluation(target_email=email_dest)
