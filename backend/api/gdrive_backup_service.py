import os
import io
import json
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
    3. Snapshot directo de la base de datos (PostgreSQL .sql si pg_dump está disponible, o SQLite .sqlite3).
    
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
        logger.error(f"[BACKUP] Error al generar Dump JSON con dumpdata: {e}")

    # -------------------------------------------------------------
    # 3. Snapshot de Base de Datos Cruda (PostgreSQL / SQLite)
    # -------------------------------------------------------------
    db_config = settings.DATABASES.get('default', {})
    engine = db_config.get('ENGINE', '')
    
    if 'postgresql' in engine:
        sql_path = os.path.join(temp_dir, f"{nombre_base}_postgres.sql")
        db_name = db_config.get('NAME')
        db_user = db_config.get('USER')
        db_host = db_config.get('HOST')
        db_port = str(db_config.get('PORT', 5432))
        db_password = db_config.get('PASSWORD')
        
        env_pg = os.environ.copy()
        if db_password:
            env_pg['PGPASSWORD'] = db_password
            
        cmd = ['pg_dump', '-h', db_host, '-p', db_port, '-U', db_user, '-d', db_name, '-f', sql_path]
        try:
            res = subprocess.run(cmd, env=env_pg, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and os.path.exists(sql_path):
                archivos_para_zip.append(sql_path)
                logger.info(f"[BACKUP] pg_dump SQL generado: {sql_path}")
            else:
                logger.warning(f"[BACKUP] pg_dump no disponible o falló: {res.stderr}")
        except Exception as e:
            logger.warning(f"[BACKUP] No se pudo ejecutar pg_dump directo (se usa el dump JSON como respaldo principal): {e}")
    else:
        # SQLite
        sqlite_name = db_config.get('NAME')
        if sqlite_name and os.path.exists(sqlite_name):
            db_copy_path = os.path.join(temp_dir, f"{nombre_base}.sqlite3")
            try:
                shutil.copy2(sqlite_name, db_copy_path)
                archivos_para_zip.append(db_copy_path)
                logger.info(f"[BACKUP] Snapshot SQLite copiado: {db_copy_path}")
            except Exception as e:
                logger.error(f"[BACKUP] Error copiando archivo SQLite: {e}")

    # -------------------------------------------------------------
    # 4. Empaquetar en archivo ZIP
    # -------------------------------------------------------------
    zip_filename = f"{nombre_base}.zip"
    zip_path = os.path.join(backups_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for fpath in archivos_para_zip:
            if os.path.exists(fpath):
                arcname = os.path.basename(fpath)
                zipf.write(fpath, arcname=arcname)
                
    # Limpiar directorio temporal
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass
        
    size_bytes = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    logger.info(f"[BACKUP] Paquete ZIP generado exitosamente: {zip_path} ({size_bytes} bytes)")
    
    return zip_path, zip_filename, size_bytes


def subir_archivo_a_gdrive(file_path: str, folder_id: str, service_account_info: dict) -> dict:
    """
    Sube un archivo a Google Drive dentro de una carpeta específica usando Google Drive API v3
    y una Cuenta de Servicio (Service Account).
    """
    if not folder_id:
        return {'success': False, 'error': 'ID de carpeta no proporcionado.'}
        
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        scopes = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)

        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)

        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        file_id = drive_file.get('id')
        link = drive_file.get('webViewLink', '')
        logger.info(f"[GDRIVE] Archivo {file_name} subido exitosamente a carpeta {folder_id}. ID: {file_id}")
        return {
            'success': True,
            'file_id': file_id,
            'link': link,
            'name': file_name
        }
    except Exception as e:
        error_msg = f"Error al subir a Google Drive (carpeta {folder_id}): {str(e)}"
        logger.error(f"[GDRIVE] {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


def subir_via_apps_script(zip_path: str, webhook_url: str, carpeta_personal_id: str = "", carpeta_institucional_id: str = "") -> dict:
    """
    Sube el archivo ZIP directamente a la carpeta de Google Drive Personal utilizando una aplicación web
    de Google Apps Script (Webhook). Esto no requiere Cuenta de Servicio de Google Cloud ni claves JSON.
    """
    import base64
    import requests

    file_name = os.path.basename(zip_path)
    try:
        with open(zip_path, 'rb') as f:
            b64_content = base64.b64encode(f.read()).decode('utf-8')

        # Limpieza defensiva de ID de carpeta si viene con URL completa
        folder_clean = (carpeta_personal_id or '').strip()
        if "/folders/" in folder_clean:
            parts = folder_clean.split("/folders/")
            if len(parts) > 1:
                folder_clean = parts[1].split("?")[0].split("/")[0].strip()

        payload = {
            'filename': file_name,
            'base64': b64_content,
            'carpeta_personal_id': folder_clean,
        }

        logger.info(f"[APPS SCRIPT] Enviando {file_name} a webhook: {webhook_url[:45]}...")
        resp = requests.post(webhook_url, json=payload, timeout=90, allow_redirects=True)

        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('status') == 'ok':
                    return {
                        'success': True,
                        'message': data.get('mensaje', 'Subido correctamente a Google Drive Personal vía Apps Script.')
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('mensaje', f"Respuesta de Apps Script: {resp.text[:200]}")
                    }
            except Exception:
                return {
                    'success': True,
                    'message': f"Webhook ejecutado con éxito: {resp.text[:200]}"
                }
        else:
            return {
                'success': False,
                'error': f"Error HTTP {resp.status_code} desde Apps Script: {resp.text[:200]}"
            }
    except Exception as exc:
        return {
            'success': False,
            'error': f"Excepción conectando con Apps Script: {str(exc)}"
        }



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

    asunto = f"📁 [RESPALDO AUTOMÁTICO] Base de Datos y Planillas - {zip_name}"
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
        <h2 style="color: #4f46e5; margin-top: 0;">📁 Respaldo Automático del Congreso</h2>
        <p>Adjunto encontrarás el paquete completo de respaldo correspondiente al corte programado:</p>
        <ul style="background: #f8fafc; padding: 15px 30px; border-radius: 6px; color: #334155;">
            <li><strong>Archivo:</strong> <code>{zip_name}</code></li>
            <li><strong>Contenido:</strong> Excel (.xlsx) con todas las tablas + Dump JSON + Snapshot SQL</li>
            <li><strong>Destinos:</strong> {', '.join(emails)}</li>
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


def ejecutar_backup_completo() -> dict:
    """
    Orquesta la ejecución completa del respaldo dual:
    1. Obtiene la configuración desde la base de datos (ConfiguracionBackupDrive).
    2. Genera el paquete .zip con fecha y hora.
    3. Sube el .zip a Google Drive (vía Apps Script Webhook o Service Account API).
    4. Envía copia por email a las casillas personal e institucional si está habilitado.
    5. Actualiza la auditoría en la base de datos.
    """
    from .models import ConfiguracionBackupDrive

    config = ConfiguracionBackupDrive.get_solo()
    if not config.activo:
        logger.info("[BACKUP GDRIVE] Respaldo automático desactivado en la configuración.")
        return {'status': 'inactive', 'message': 'Respaldo automático desactivado.'}

    # 1. Generar paquete ZIP local
    try:
        zip_path, zip_name, size_bytes = generar_paquete_backup()
    except Exception as e:
        error_local = f"Fallo crítico al generar paquete de respaldo local: {str(e)}"
        logger.error(f"[BACKUP GDRIVE] {error_local}")
        config.ultimo_respaldo_fecha = timezone.now()
        config.ultimo_respaldo_estado = f"ERROR LOCAL: {error_local}"
        config.save()
        return {'status': 'error', 'message': error_local}

    logs_resultado = []
    logs_resultado.append(f"✓ Archivo local generado: {zip_name} ({round(size_bytes / 1024, 1)} KB)")

    upload_personal_ok = False
    upload_institucional_ok = False

    # 2. Vía 1: Google Apps Script Webhook (Personal)
    if config.apps_script_url and config.apps_script_url.strip():
        logger.info("[BACKUP GDRIVE] Ejecutando subida mediante Google Apps Script...")
        res_apps = subir_via_apps_script(
            zip_path,
            config.apps_script_url.strip(),
            config.carpeta_personal_id
        )
        if res_apps.get('success'):
            upload_personal_ok = True
            logs_resultado.append(f"✓ Google Apps Script: {res_apps.get('message')}")
        else:
            logs_resultado.append(f"✗ Error Google Apps Script: {res_apps.get('error')}")

    # 3. Vía 2: Google Service Account API (si no hay Apps Script configurado)
    elif config.service_account_json and config.service_account_json.strip():
        try:
            service_account_info = json.loads(config.service_account_json.strip())
        except Exception as e:
            service_account_info = None
            logs_resultado.append(f"✗ JSON de Service Account inválido: {e}")

        if service_account_info:
            if config.carpeta_personal_id:
                res_personal = subir_archivo_a_gdrive(zip_path, config.carpeta_personal_id, service_account_info)
                if res_personal.get('success'):
                    upload_personal_ok = True
                    logs_resultado.append(f"✓ Subido con éxito a Drive Personal (ID: {res_personal.get('file_id')})")
                else:
                    logs_resultado.append(f"✗ Error subiendo a Drive Personal: {res_personal.get('error')}")
            else:
                logs_resultado.append("ℹ️ Carpeta de Drive Personal no configurada (omitido).")

            if config.carpeta_institucional_id:
                res_inst = subir_archivo_a_gdrive(zip_path, config.carpeta_institucional_id, service_account_info)
                if res_inst.get('success'):
                    upload_institucional_ok = True
                    logs_resultado.append(f"✓ Subido con éxito a Drive Institucional (ID: {res_inst.get('file_id')})")
                else:
                    logs_resultado.append(f"✗ Error subiendo a Drive Institucional: {res_inst.get('error')}")
    else:
        logs_resultado.append("ℹ️ Subida directa a Drive pendiente (configurá la URL de Apps Script o el JSON de Service Account).")

    # 4. Vía 3: Envío por correo electrónico con el ZIP adjunto (Personal)
    email_destinos = []
    if config.enviar_por_email:
        if config.email_personal and config.email_personal.strip():
            email_destinos.append(config.email_personal.strip())
        if config.email_institucional and config.email_institucional.strip():
            email_destinos.append(config.email_institucional.strip())

        if email_destinos:
            logs_email = enviar_backup_por_email(zip_path, zip_name, email_destinos)
            logs_resultado.extend(logs_email)

    # 5. Actualizar registro en base de datos
    estado_texto = "\n".join(logs_resultado)
    config.ultimo_respaldo_fecha = timezone.now()
    config.ultimo_respaldo_archivo = zip_name
    config.ultimo_respaldo_estado = estado_texto
    config.save()

    return {
        'status': 'ok',
        'archivo': zip_name,
        'size_bytes': size_bytes,
        'drive_personal': upload_personal_ok,
        'drive_institucional': upload_institucional_ok,
        'emails_enviados': email_destinos if config.enviar_por_email else [],
        'reporte': estado_texto
    }

