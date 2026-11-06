import os
import shutil
import zipfile
import logging
import subprocess
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.apps import apps
from django.core.management import call_command
import pandas as pd

logger = logging.getLogger(__name__)


def generar_paquete_backup() -> tuple[str, str, int]:
    """
    Genera un paquete de respaldo comprimido (.zip) con fecha y hora que incluye:
    1. Libro Excel consolidado (.xlsx) con todas las tablas del congreso vía ORM.
    2. Dump estructurado portable en JSON (.json) vía dumpdata de Django.
    3. Snapshot de la base de datos (PostgreSQL .sql si pg_dump está disponible, o SQLite .sqlite3).
    
    Retorna una tupla: (ruta_absoluta_zip, nombre_archivo_zip, tamaño_en_bytes).
    """
    ahora_local = timezone.localtime(timezone.now())
    timestamp = ahora_local.strftime('%Y%m%d_%H%M%S')
    nombre_base = f"backup_congreso_{timestamp}"
    
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    temp_dir = os.path.join(backups_dir, f"temp_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)
    
    archivos_para_zip = []
    
    # -------------------------------------------------------------
    # 1. Generar Excel consolidado multi-hoja (.xlsx)
    # -------------------------------------------------------------
    excel_path = os.path.join(temp_dir, f"{nombre_base}.xlsx")
    try:
        custom_apps = ['api', 'bolsa_trabajo']
        models_to_export = []
        for app_config in apps.get_app_configs():
            if app_config.label in custom_apps:
                for model in app_config.get_models():
                    if model._meta.managed:
                        models_to_export.append(model)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:  # type: ignore
            for model in models_to_export:
                fields = [f.name for f in model._meta.fields]
                queryset = model.objects.all()
                data = list(queryset.values(*fields))
                df = pd.DataFrame(data, columns=fields)
                
                for col in df.columns:
                    if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                        df[col] = df[col].dt.tz_localize(None)
                    elif df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: x.replace(tzinfo=None) if hasattr(x, 'tzinfo') and x is not None else x)
                
                sheet_name = model._meta.object_name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        archivos_para_zip.append(excel_path)
        logger.info(f"[BACKUP] Excel consolidado generado: {excel_path}")
    except Exception as e:
        logger.error(f"[BACKUP] Error al generar Excel consolidado: {e}")

    # -------------------------------------------------------------
    # 2. Generar Dump estructurado portable JSON (Django dumpdata)
    # -------------------------------------------------------------
    json_path = os.path.join(temp_dir, f"{nombre_base}_data.json")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                'api',
                'bolsa_trabajo',
                exclude=['api.Dashboard'],
                natural_foreign=True,
                natural_primary=True,
                indent=2,
                stdout=f
            )
        archivos_para_zip.append(json_path)
        logger.info(f"[BACKUP] Dump JSON generado: {json_path}")
    except Exception as e:
        logger.error(f"[BACKUP] Error al generar dump JSON: {e}")

    # -------------------------------------------------------------
    # 3. Snapshot de Base de Datos (PostgreSQL pg_dump o copia SQLite)
    # -------------------------------------------------------------
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'postgresql' in db_engine:
        sql_path = os.path.join(temp_dir, f"{nombre_base}_postgres.sql")
        try:
            db_conf = settings.DATABASES['default']
            cmd = ['pg_dump']
            if db_conf.get('HOST'):
                cmd.extend(['-h', db_conf['HOST']])
            if db_conf.get('PORT'):
                cmd.extend(['-p', str(db_conf['PORT'])])
            if db_conf.get('USER'):
                cmd.extend(['-U', db_conf['USER']])
            cmd.extend(['-f', sql_path, db_conf['NAME']])
            
            env = os.environ.copy()
            if db_conf.get('PASSWORD'):
                env['PGPASSWORD'] = db_conf['PASSWORD']
                
            res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and os.path.exists(sql_path):
                archivos_para_zip.append(sql_path)
                logger.info(f"[BACKUP] pg_dump SQL generado: {sql_path}")
            else:
                logger.warning(f"[BACKUP] pg_dump finalizó con advertencia/error ({res.stderr[:200]}). Continuando con Excel y JSON.")
        except Exception as e:
            logger.warning(f"[BACKUP] No se pudo ejecutar pg_dump directo ({e}). Continuando con dumpdata y Excel.")
    elif 'sqlite3' in db_engine:
        sqlite_file = settings.DATABASES['default']['NAME']
        if os.path.exists(sqlite_file):
            sqlite_copy = os.path.join(temp_dir, f"{nombre_base}.sqlite3")
            try:
                shutil.copy2(sqlite_file, sqlite_copy)
                archivos_para_zip.append(sqlite_copy)
                logger.info(f"[BACKUP] Copia SQLite generada: {sqlite_copy}")
            except Exception as e:
                logger.error(f"[BACKUP] Error al copiar SQLite: {e}")

    # -------------------------------------------------------------
    # 4. Empaquetar todo en el archivo ZIP final
    # -------------------------------------------------------------
    zip_filename = f"{nombre_base}.zip"
    zip_path = os.path.join(backups_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_to_add in archivos_para_zip:
            if os.path.exists(file_to_add):
                arcname = os.path.basename(file_to_add)
                zipf.write(file_to_add, arcname)

    # Limpieza del directorio temporal
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    size_bytes = os.path.getsize(zip_path)
    logger.info(f"[BACKUP] Paquete ZIP generado con éxito: {zip_path} ({round(size_bytes / 1024, 1)} KB)")
    
    return zip_path, zip_filename, size_bytes


def enviar_backup_por_email(zip_path: str, zip_name: str, emails: list[str]) -> list[str]:
    """
    Envía el paquete comprimido (.zip) adjunto por correo electrónico a las casillas configuradas.
    Permite a los administradores resguardar el archivo y guardarlo en Google Drive con un clic en Gmail.
    """
    from django.core.mail import EmailMultiAlternatives
    from .email import CONGRESO_EMAIL

    logs = []
    if not emails:
        return logs

    asunto = f"📦 [RESPALDO AUTOMÁTICO] Base de Datos y Planillas - {zip_name}"
    cuerpo_texto = (
        f"Se adjunta el paquete de respaldo automático generado para el 2º Congreso de Logística UNAB 2026.\n\n"
        f"Archivo: {zip_name}\n"
        f"Contenido del ZIP:\n"
        f" - Libro Excel consolidado multi-hoja (.xlsx) con todas las tablas del congreso\n"
        f" - Volcado estructural portable en JSON (.json)\n"
        f" - Snapshot crudo de la base de datos (.sql / .sqlite3)\n\n"
        f"Podés guardar este archivo directamente en tu Google Drive haciendo clic en el icono 'Guardar en Drive' dentro de Gmail/Workspace."
    )

    cuerpo_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #4f46e5; margin-top: 0;">📦 Respaldo Automático del Congreso UNAB 2026</h2>
        <p>Adjunto encontrarás el paquete completo de respaldo correspondiente al corte programado:</p>
        <ul style="background: #f8fafc; padding: 15px 30px; border-radius: 6px; color: #334155; line-height: 1.6;">
            <li><strong>Archivo:</strong> <code>{zip_name}</code></li>
            <li><strong>Contenido:</strong> Excel (.xlsx) con todas las tablas + Dump JSON portable + Snapshot SQL</li>
            <li><strong>Destinatarios:</strong> {', '.join(emails)}</li>
        </ul>
        <p style="color: #64748b; font-size: 13px;">
            💡 <strong>Tip Google Workspace / Gmail:</strong> Al pasar el cursor sobre el archivo adjunto, hacé clic en el botón <strong>"Guardar en Drive"</strong> 📁 para guardarlo instantáneamente en tu cuenta.
        </p>
    </div>
    """

    for email_dest in emails:
        email_clean = (email_dest or '').strip()
        if not email_clean or '@' not in email_clean:
            continue
        try:
            msg = EmailMultiAlternatives(
                subject=asunto,
                body=cuerpo_texto,
                from_email=f"Congreso de Logística UNAB <{CONGRESO_EMAIL}>",
                to=[email_clean]
            )
            msg.attach_alternative(cuerpo_html, "text/html")

            with open(zip_path, 'rb') as f:
                msg.attach(zip_name, f.read(), 'application/zip')

            msg.send(fail_silently=False)
            logs.append(f"✓ Respaldo enviado por email adjunto a {email_clean}")
            logger.info(f"[BACKUP EMAIL] Archivo {zip_name} enviado a {email_clean}")
        except Exception as exc:
            err = f"✗ Falló envío de email de respaldo a {email_clean}: {exc}"
            logs.append(err)
            logger.error(f"[BACKUP EMAIL] {err}")

    return logs


def ejecutar_respaldo_programado(destinos_forzados: list[str] | None = None) -> dict:
    """
    Orquesta la ejecución completa del respaldo del sistema:
    1. Obtiene la configuración desde la base de datos (ConfiguracionRespaldo).
    2. Genera el paquete .zip con fecha y hora (Excel + JSON + SQL).
    3. Envía copia por email con el .zip adjunto a las casillas personal e institucional.
    4. Actualiza la auditoría en la base de datos.
    """
    from .models import ConfiguracionRespaldo

    config = ConfiguracionRespaldo.get_solo()
    if not config.activo and destinos_forzados is None:
        logger.info("[BACKUP] Respaldo automático desactivado en la configuración.")
        return {'status': 'inactive', 'message': 'Respaldo automático desactivado.'}

    # 1. Generar paquete ZIP local
    try:
        zip_path, zip_name, size_bytes = generar_paquete_backup()
    except Exception as e:
        error_local = f"Fallo crítico al generar paquete de respaldo local: {str(e)}"
        logger.error(f"[BACKUP] {error_local}")
        config.ultimo_respaldo_fecha = timezone.now()
        config.ultimo_respaldo_estado = f"ERROR LOCAL: {error_local}"
        config.save()
        return {'status': 'error', 'ok': False, 'message': error_local, 'error': error_local, 'logs': [error_local]}

    logs_resultado = []
    logs_resultado.append(f"✓ Archivo local generado: {zip_name} ({round(size_bytes / 1024, 1)} KB)")

    # 2. Determinar destinatarios
    if destinos_forzados is not None:
        email_destinos = destinos_forzados
    elif config.enviar_por_email:
        email_destinos = []
        if config.email_personal and config.email_personal.strip():
            email_destinos.append(config.email_personal.strip())
        if config.email_institucional and config.email_institucional.strip():
            email_destinos.append(config.email_institucional.strip())
    else:
        email_destinos = []

    # 3. Enviar por correo electrónico
    if email_destinos:
        logs_email = enviar_backup_por_email(zip_path, zip_name, email_destinos)
        logs_resultado.extend(logs_email)
    else:
        logs_resultado.append("ℹ️ Envío por email desactivado. El archivo quedó guardado en el servidor local.")

    # 4. Actualizar auditoría en base de datos
    estado_texto = "\n".join(logs_resultado)
    config.ultimo_respaldo_fecha = timezone.now()
    config.ultimo_respaldo_archivo = zip_name
    config.ultimo_respaldo_estado = estado_texto
    config.save()

    return {
        'status': 'ok',
        'ok': True,
        'archivo': zip_name,
        'zip_path': zip_path,
        'size_bytes': size_bytes,
        'emails_enviados': email_destinos,
        'reporte': estado_texto,
        'logs': logs_resultado
    }
