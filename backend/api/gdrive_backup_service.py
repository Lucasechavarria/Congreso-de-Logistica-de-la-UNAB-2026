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


def ejecutar_backup_completo() -> dict:
    """
    Orquesta la ejecución completa del respaldo dual:
    1. Obtiene la configuración desde la base de datos (ConfiguracionBackupDrive).
    2. Genera el paquete .zip con fecha y hora.
    3. Sube el .zip al Google Drive Personal (si está configurado).
    4. Sube el .zip al Google Drive Institucional (si está configurado).
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

    # 2. Parsear credenciales de Service Account
    service_account_info = None
    if config.service_account_json and config.service_account_json.strip():
        try:
            service_account_info = json.loads(config.service_account_json.strip())
        except Exception as e:
            logger.error(f"[BACKUP GDRIVE] JSON de Service Account inválido: {e}")

    logs_resultado = []
    logs_resultado.append(f"✓ Archivo local generado: {zip_name} ({round(size_bytes / 1024, 1)} KB)")

    upload_personal_ok = False
    upload_institucional_ok = False

    if not service_account_info:
        msg_no_creds = "⚠️ Credenciales de Google Service Account no configuradas. El backup quedó resguardado en almacenamiento local."
        logs_resultado.append(msg_no_creds)
    else:
        # 3. Subir a Drive Personal
        if config.carpeta_personal_id:
            res_personal = subir_archivo_a_gdrive(zip_path, config.carpeta_personal_id, service_account_info)
            if res_personal.get('success'):
                upload_personal_ok = True
                logs_resultado.append(f"✓ Subido con éxito a Drive Personal (ID: {res_personal.get('file_id')})")
            else:
                logs_resultado.append(f"✗ Error subiendo a Drive Personal: {res_personal.get('error')}")
        else:
            logs_resultado.append("ℹ️ Carpeta de Drive Personal no configurada (omitido).")

        # 4. Subir a Drive Institucional UNaB
        if config.carpeta_institucional_id:
            res_inst = subir_archivo_a_gdrive(zip_path, config.carpeta_institucional_id, service_account_info)
            if res_inst.get('success'):
                upload_institucional_ok = True
                logs_resultado.append(f"✓ Subido con éxito a Drive Institucional UNaB (ID: {res_inst.get('file_id')})")
            else:
                logs_resultado.append(f"✗ Error subiendo a Drive Institucional: {res_inst.get('error')}")
        else:
            logs_resultado.append("ℹ️ Carpeta de Drive Institucional no configurada (omitido).")

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
        'reporte': estado_texto
    }
