import os
import sys
import time
import tempfile
import logging
import threading
from datetime import datetime, date
from contextlib import contextmanager
from django.conf import settings
from django.db import connection, transaction, close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

_scheduler_started = False
_scheduler_pid = None
_scheduler_thread = None
_scheduler_lock = threading.Lock()
_cert_batch_thread_lock = threading.Lock()
_legacy_beat_cleaned = False

# Identificador único de bloqueo consultivo en PostgreSQL (pg_try_advisory_lock)
PG_CERT_QUEUE_LOCK_ID = 20261107


def _get_web_console_priority_paths() -> list[str]:
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    primary = os.path.join(backups_dir, '.web_console_priority.ts')
    fallback = os.path.join(tempfile.gettempdir(), 'congreso_unab_web_console_priority.ts')
    return [primary, fallback]


def mark_web_console_priority(ttl_seconds: float = 25.0) -> None:
    """
    Registra una ventana de prioridad temporal para la consola web (/admin/certificate-queue/)
    de modo que durante la pausa de 2 segundos entre lotes sucesivos del navegador,
    el scheduler en segundo plano o el cron no roben el bloqueo ni interfieran con la sesión activa.
    """
    paths = _get_web_console_priority_paths()
    if ttl_seconds <= 0:
        for p in paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                try:
                    with open(p, 'w', encoding='utf-8') as f:
                        f.write('0')
                except OSError:
                    pass
        return

    expires_at = time.time() + float(ttl_seconds)
    payload = f"{expires_at:.3f}"
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    written = False
    try:
        os.makedirs(backups_dir, exist_ok=True)
        with open(paths[0], 'w', encoding='utf-8') as f:
            f.write(payload)
        try:
            os.chmod(paths[0], 0o666)
        except OSError:
            pass
        written = True
        if os.path.exists(paths[1]):
            try:
                os.remove(paths[1])
            except OSError:
                pass
    except OSError:
        written = False

    if not written:
        try:
            with open(paths[1], 'w', encoding='utf-8') as f:
                f.write(payload)
            try:
                os.chmod(paths[1], 0o666)
            except OSError:
                pass
        except OSError:
            pass


def clear_web_console_priority() -> None:
    """Limpia inmediatamente la reserva de prioridad de la consola web al concluir la tanda final."""
    mark_web_console_priority(0.0)


def is_web_console_priority_active() -> bool:
    """
    Retorna True si el administrador está transmitiendo activamente una secuencia de lotes
    desde la consola web (/admin/certificate-queue/) dentro de la ventana de TTL.
    """
    now_ts = time.time()
    for p in _get_web_console_priority_paths():
        try:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    raw = f.read().strip()
                if raw:
                    expires_at = float(raw)
                    if now_ts < expires_at:
                        return True
        except (ValueError, OSError):
            continue
    return False


def limpiar_tareas_respaldo_programadas_db() -> int:
    """
    Elimina de django_celery_beat (si existen en la base de datos PostgreSQL)
    cualquier tarea periódica residual de respaldos automáticos, garantizando
    que los respaldos sean exclusivamente manuales.
    """
    global _legacy_beat_cleaned
    try:
        from django_celery_beat.models import PeriodicTask
        from django.db.models import Q
        deleted_count, _ = PeriodicTask.objects.filter(
            Q(name__startswith='respaldo-sistema-')
            | Q(task__in=[
                'api.tasks.task_ejecutar_respaldo_programado',
                'api.tasks.task_ejecutar_backup_dual_gdrive',
            ])
        ).delete()
        _legacy_beat_cleaned = True
        return deleted_count
    except Exception:
        return 0


def es_horario_habilitado_certificados(ahora_local=None) -> bool:
    """
    Determina si ya se cumplió el horario de cierre para habilitar la emisión de certificados:
    - En días posteriores al 7 de noviembre del año del evento (ej. 8 de noviembre a las 00:05 hs o 10:00 hs),
      el cierre del Congreso ya ocurrió y la cola está habilitada las 24 hs.
    - En el día del evento (7 de noviembre) o días previos, requiere hora local >= 18:00 hs.
    """
    if ahora_local is None:
        ahora_local = timezone.localtime(timezone.now())
    if ahora_local.date() > date(ahora_local.year, 11, 7):
        return True
    return ahora_local.hour >= 18


@contextmanager
def _acquire_file_lock(min_interval_seconds: float = 0.0, lock_filename: str = '.scheduler.lock'):
    """
    Adquiere un bloqueo de archivo no bloqueante entre procesos (compatible con Linux/Gunicorn y Windows)
    para garantizar que solo un worker de Gunicorn ejecute el ciclo automático a la vez.
    Si el directorio backups no tiene permisos de escritura, utiliza el directorio temporal del sistema.
    """
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    lock_path = os.path.join(backups_dir, lock_filename)

    fd = None
    try:
        os.makedirs(backups_dir, exist_ok=True)
        fd = open(lock_path, 'a+b')
        try:
            os.chmod(lock_path, 0o666)
        except OSError:
            pass
    except OSError:
        safe_name = lock_filename.lstrip('.').replace('.', '_')
        fallback_path = os.path.join(tempfile.gettempdir(), f'congreso_unab_{safe_name}.lock')
        try:
            fd = open(fallback_path, 'a+b')
            lock_path = fallback_path
            try:
                os.chmod(lock_path, 0o666)
            except OSError:
                pass
        except OSError as open_err:
            logger.warning(f"[AUTO-SCHEDULER] No se pudo abrir archivo de lock ({open_err}).")
            yield False
            return

    locked = False
    try:
        try:
            if os.name == 'nt':
                import msvcrt
                fd.seek(0)
                msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
            else:
                import fcntl
                fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
        except (BlockingIOError, IOError, OSError):
            yield False
            return

        if min_interval_seconds > 0:
            ts_path = lock_path + '.ts'
            now_ts = time.time()
            try:
                if os.path.exists(ts_path):
                    with open(ts_path, 'r', encoding='utf-8') as tf:
                        last_ts = float(tf.read().strip() or '0')
                    if (now_ts - last_ts) < min_interval_seconds:
                        yield False
                        return
                with open(ts_path, 'w', encoding='utf-8') as tf:
                    tf.write(f"{now_ts:.3f}")
                try:
                    os.chmod(ts_path, 0o666)
                except OSError:
                    pass
            except (ValueError, OSError):
                pass

        yield True
    finally:
        if fd is not None:
            if locked:
                try:
                    if os.name == 'nt':
                        import msvcrt
                        fd.seek(0)
                        msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
            try:
                fd.close()
            except Exception:
                pass


@contextmanager
def acquire_certificate_queue_lock(lock_id: int = PG_CERT_QUEUE_LOCK_ID):
    """
    Coordina en PostgreSQL (mediante pg_try_advisory_lock / pg_advisory_unlock) y entre
    hilos/procesos locales el procesamiento por lotes de la cola de certificados.
    Garantiza que el scheduler en segundo plano y la consola web jamás seleccionen ni
    envíen el mismo certificado simultáneamente.
    """
    thread_acquired = _cert_batch_thread_lock.acquire(blocking=False)
    if not thread_acquired:
        yield False
        return

    try:
        with _acquire_file_lock(min_interval_seconds=0.0, lock_filename='.cert_batch.lock') as file_acquired:
            if not file_acquired:
                yield False
                return

            close_old_connections()
            pg_acquired = False
            if connection.vendor == 'postgresql':
                try:
                    with connection.cursor() as cursor:
                        try:
                            cursor.execute("SELECT pg_advisory_unlock_all()")
                        except Exception:
                            pass
                        try:
                            cursor.execute(
                                "SELECT pg_terminate_backend(l.pid) "
                                "FROM pg_locks l "
                                "JOIN pg_stat_activity a ON a.pid = l.pid "
                                "WHERE l.locktype = 'advisory' "
                                "AND l.objid = %s "
                                "AND l.pid <> pg_backend_pid() "
                                "AND a.state = 'idle' "
                                "AND a.state_change < (now() - interval '35 seconds')",
                                [lock_id]
                            )
                            terminated_rows = cursor.fetchall()
                            if terminated_rows and any(r[0] for r in terminated_rows):
                                time.sleep(0.1)
                        except Exception:
                            pass
                        cursor.execute("SELECT pg_try_advisory_lock(%s)", [lock_id])
                        row = cursor.fetchone()
                        pg_acquired = bool(row and row[0])
                        if not pg_acquired:
                            yield False
                            return
                except Exception as pg_err:
                    logger.warning(f"[PG-LOCK] Error consultando pg_try_advisory_lock: {pg_err}")
                    yield False
                    return

            try:
                yield True
            finally:
                if pg_acquired and connection.vendor == 'postgresql':
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SELECT pg_advisory_unlock(%s)", [lock_id])
                    except Exception as unlock_err:
                        logger.warning(f"[PG-LOCK] Error liberando pg_advisory_unlock: {unlock_err}")
                        try:
                            connection.close()
                        except Exception:
                            pass
    finally:
        _cert_batch_thread_lock.release()


def is_certificate_queue_locked(lock_id: int = PG_CERT_QUEUE_LOCK_ID) -> bool:
    """
    Consulta de forma no bloqueante si el lock de procesamiento de certificados está activo
    actualmente (en memoria, en pg_locks de PostgreSQL o en el lock de archivo entre procesos).
    """
    if _cert_batch_thread_lock.locked():
        return True
    if connection.vendor == 'postgresql':
        try:
            close_old_connections()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM pg_locks l "
                    "JOIN pg_stat_activity a ON a.pid = l.pid "
                    "WHERE l.locktype = 'advisory' "
                    "AND l.objid = %s "
                    "AND l.granted = true "
                    "AND (a.state <> 'idle' OR a.state_change > (now() - interval '35 seconds'))"
                    ")",
                    [lock_id]
                )
                row = cursor.fetchone()
                return bool(row and row[0])
        except Exception:
            pass
        return False
    with _acquire_file_lock(min_interval_seconds=0.0, lock_filename='.cert_batch.lock') as file_free:
        if not file_free:
            return True
    return False


def reclamar_lote_certificados(batch_size: int = 5, reintentar_fallidos: bool = False, after_id: int = 0, max_intentos_auto: int | None = None):
    """
    Selecciona el lote de certificados pendientes utilizando select_for_update(skip_locked=True)
    en PostgreSQL dentro de una transacción corta para evitar cualquier colisión a nivel de fila.
    """
    from .models import Certificado

    with transaction.atomic():
        qs_base = Certificado.objects.filter(email_enviado=False)
        if getattr(connection.features, 'has_select_for_update_skip_locked', False):
            qs_base = qs_base.select_for_update(skip_locked=True)

        if reintentar_fallidos:
            qs_filtered = qs_base
            if max_intentos_auto is not None:
                qs_filtered = qs_filtered.filter(intentos__lt=max_intentos_auto)
            if after_id > 0:
                qs_filtered = qs_filtered.filter(id__gt=after_id)
            ids = list(qs_filtered.order_by('id').values_list('id', flat=True)[:batch_size])
        else:
            ids = list(qs_base.filter(intentos=0).order_by('id').values_list('id', flat=True)[:batch_size])

    if not ids:
        return []

    return list(
        Certificado.objects.filter(id__in=ids)
        .select_related('asistente', 'asistente__empresa_vinculada', 'asistente__disertante_vinculado')
        .order_by('id')
    )


def obtener_estado_cola_certificados(since_log_id: int = 0, limit: int = 40) -> dict:
    """
    Devuelve los contadores en vivo desde PostgreSQL y los últimos registros reales
    de transmisión de certificados desde LogEnvioEmail para renderizar en la consola
    de /admin/certificate-queue/ tanto en modo automático como manual.
    """
    from django.db.models import Count, Q
    from .models import Certificado, LogEnvioEmail

    agg = Certificado.objects.aggregate(
        remaining=Count('id', filter=Q(email_enviado=False)),
        remaining_unattempted=Count('id', filter=Q(email_enviado=False, intentos=0)),
        failed_count=Count('id', filter=Q(email_enviado=False, intentos__gt=0)),
        sent_total=Count('id', filter=Q(email_enviado=True)),
        pendientes_asistencia=Count('id', filter=Q(email_enviado=False, tipo_certificado='ASISTENCIA')),
        pendientes_disertante=Count('id', filter=Q(email_enviado=False, tipo_certificado='DISERTANTE')),
        pendientes_empresa=Count('id', filter=Q(email_enviado=False, tipo_certificado='EMPRESA')),
    )

    remaining = agg['remaining'] or 0
    remaining_unattempted = agg['remaining_unattempted'] or 0
    failed_count = agg['failed_count'] or 0
    sent_total = agg['sent_total'] or 0
    pendientes_asistencia = agg['pendientes_asistencia'] or 0
    pendientes_disertante = agg['pendientes_disertante'] or 0
    pendientes_empresa = agg['pendientes_empresa'] or 0

    qs_logs = LogEnvioEmail.objects.filter(tipo_email__startswith='certificado')
    max_log_id_db = qs_logs.order_by('-id').values_list('id', flat=True).first() or 0

    if since_log_id > 0:
        logs_rows = list(qs_logs.filter(id__gt=since_log_id).order_by('id')[:limit])
    else:
        logs_rows = list(qs_logs.order_by('-id')[:limit])[::-1]

    recent_logs = []
    for log in logs_rows:
        tipo_raw = (log.tipo_email or '').lower()
        if 'disertante' in tipo_raw:
            tipo_label = 'Disertante'
        elif 'empresa' in tipo_raw:
            tipo_label = 'Empresa'
        else:
            tipo_label = 'Asistencia'

        fecha_local = timezone.localtime(log.fecha_envio) if log.fecha_envio else timezone.localtime(timezone.now())
        ts_str = fecha_local.strftime('%H:%M:%S')

        if log.exitoso:
            msg = f"✓ Enviado con éxito a {log.destinatario} ({tipo_label})"
            level = 'success'
        else:
            motivo = (log.error or 'Error SMTP').strip().splitlines()[0][:140]
            msg = f"✗ Falló el envío a {log.destinatario}: {motivo}"
            level = 'error'

        recent_logs.append({
            'id': log.id,
            'timestamp': ts_str,
            'destinatario': log.destinatario,
            'exitoso': bool(log.exitoso),
            'level': level,
            'message': msg,
        })

    ahora_local = timezone.localtime(timezone.now())
    last_log_id = recent_logs[-1]['id'] if recent_logs else max(since_log_id, max_log_id_db)
    failed_certificates = obtener_lista_certificados_fallidos(limit=50)

    return {
        'remaining': remaining,
        'remaining_unattempted': remaining_unattempted,
        'failed_count': failed_count,
        'sent_total': sent_total,
        'pendientes_asistencia': pendientes_asistencia,
        'pendientes_disertante': pendientes_disertante,
        'pendientes_empresa': pendientes_empresa,
        'recent_logs': recent_logs,
        'last_log_id': last_log_id,
        'lock_busy': is_certificate_queue_locked(),
        'hora_valida': es_horario_habilitado_certificados(ahora_local),
        'hora_actual_str': ahora_local.strftime('%H:%M:%S'),
        'failed_certificates': failed_certificates,
    }


def obtener_lista_certificados_fallidos(limit: int = 100) -> list[dict]:
    """
    Retorna la lista de certificados con envíos fallidos (email_enviado=False, intentos > 0),
    incluyendo datos del participante, DNI, email registrado, tipo, intentos y el motivo exacto
    del fallo (evaluando validación de sintaxis/typos y registros reales en LogEnvioEmail).
    """
    from .models import Certificado, LogEnvioEmail
    from .email import validar_email_destinatario

    qs = (
        Certificado.objects.filter(email_enviado=False, intentos__gt=0)
        .select_related('asistente', 'asistente__empresa_vinculada', 'asistente__disertante_vinculado', 'edicion')
        .order_by('-intentos', '-id')[:limit]
    )

    fallidos = []
    emails_fallidos = [
        c.asistente.email.strip().lower()
        for c in qs
        if c.asistente and getattr(c.asistente, 'email', None) and c.asistente.email.strip()
    ]
    logs_dict = {}
    if emails_fallidos:
        logs_qs = (
            LogEnvioEmail.objects.filter(
                destinatario__in=emails_fallidos,
                tipo_email__startswith='certificado',
                exitoso=False
            )
            .order_by('-id')
        )
        for log in logs_qs:
            dest_lower = (log.destinatario or '').strip().lower()
            if dest_lower not in logs_dict and log.error:
                logs_dict[dest_lower] = log.error.strip().splitlines()[0][:200]

    for cert in qs:
        asist = cert.asistente
        email_dest = getattr(asist, 'email', '') or ''

        # Nombre display según tipo
        if cert.tipo_certificado == 'EMPRESA' and getattr(asist, 'empresa_vinculada', None) and asist.empresa_vinculada.nombre_empresa:
            nombre = asist.empresa_vinculada.nombre_empresa.strip()
        elif cert.tipo_certificado == 'DISERTANTE' and getattr(asist, 'disertante_vinculado', None) and asist.disertante_vinculado.nombre:
            nombre = asist.disertante_vinculado.nombre.strip()
        else:
            nombre = f"{getattr(asist, 'first_name', '')} {getattr(asist, 'last_name', '')}".strip() or f"Asistente #{cert.asistente_id}"

        dni = getattr(asist, 'dni', '') or ''
        telefono = getattr(asist, 'telefono', '') or ''

        # Determinar el motivo exacto del fallo
        if not email_dest or email_dest.strip() == '' or email_dest.startswith('sin-email-'):
            error_motivo = "Sin correo registrado (casilla vacía o temporal sin-email)"
        else:
            es_valido, motivo_val = validar_email_destinatario(email_dest)
            if not es_valido:
                error_motivo = motivo_val
            elif email_dest.lower() in logs_dict:
                error_motivo = logs_dict[email_dest.lower()]
            else:
                error_motivo = "Rechazo de transporte SMTP o tiempo de espera agotado"

        fecha_gen_str = ""
        if cert.fecha_generacion:
            fecha_gen_str = timezone.localtime(cert.fecha_generacion).strftime('%d/%m/%Y %H:%M')

        fallidos.append({
            'id': cert.id,
            'asistente_id': asist.id if asist else None,
            'nombre': nombre,
            'dni': dni,
            'telefono': telefono,
            'email': email_dest,
            'tipo': cert.tipo_certificado,
            'tipo_display': cert.get_tipo_certificado_display(),
            'intentos': cert.intentos,
            'error': error_motivo,
            'fecha_generacion': fecha_gen_str,
        })

    return fallidos


def verificar_y_procesar_cola_certificados(ahora_local=None, batch_size=5, delay_seconds=1) -> dict:
    """
    Si ya se cumplió el horario de cierre (18:00 hs del 7 de noviembre o fecha posterior),
    sincroniza las inscripciones con asistencia confirmada y procesa un lote controlado
    de certificados pendientes (intentos=0) coordinado en PostgreSQL.
    """
    from .models import Certificado
    from .services import sincronizar_certificados_asistencia
    from .tasks import task_procesar_cola_certificados_lote

    if ahora_local is None:
        ahora_local = timezone.localtime(timezone.now())

    if not es_horario_habilitado_certificados(ahora_local):
        return {'executed': False, 'reason': 'before_18hs'}

    if is_web_console_priority_active():
        return {'executed': False, 'reason': 'web_console_priority'}

    try:
        sincronizar_certificados_asistencia()
    except Exception as sync_err:
        logger.warning(f"[AUTO-SCHEDULER] Error sincronizando certificados de asistencia: {sync_err}")

    pendientes_sin_intentar = Certificado.objects.filter(email_enviado=False, intentos=0).count()
    if pendientes_sin_intentar == 0:
        return {'executed': False, 'reason': 'no_pending_certificates', 'remaining_unattempted': 0}

    logger.info(
        f"[AUTO-SCHEDULER] Procesando lote automático de certificados ({pendientes_sin_intentar} pendientes sin intentar)..."
    )
    resultado = task_procesar_cola_certificados_lote(
        batch_size=batch_size,
        forzar=True,
        delay_seconds=delay_seconds,
        reintentar_fallidos=False,
    )
    if resultado.get('status') == 'busy_web_or_worker':
        return {
            'executed': False,
            'reason': 'busy_web_or_worker',
            'result': resultado,
            'remaining_unattempted': resultado.get('remaining_unattempted', pendientes_sin_intentar),
        }
    return {
        'executed': True,
        'result': resultado,
        'remaining_unattempted': resultado.get('remaining_unattempted', 0),
    }


def ejecutar_ciclo_scheduler(ahora_local=None, batch_size=5, delay_seconds=1, min_interval_seconds: float = 0.0) -> dict:
    """
    Ejecuta un ciclo del planificador autónomo para la cola de certificados bajo bloqueo multi-proceso.
    Los respaldos del sistema son exclusivamente manuales y no se ejecutan automáticamente aquí.
    """
    with _acquire_file_lock(min_interval_seconds=min_interval_seconds, lock_filename='.scheduler.lock') as acquired:
        if not acquired:
            return {'status': 'skipped_locked'}

        try:
            close_old_connections()
            if not _legacy_beat_cleaned:
                limpiar_tareas_respaldo_programadas_db()
            res_certs = verificar_y_procesar_cola_certificados(
                ahora_local=ahora_local,
                batch_size=batch_size,
                delay_seconds=delay_seconds,
            )
            return {
                'status': 'ok',
                'backup': {'executed': False, 'reason': 'manual_only'},
                'certificates': res_certs,
            }
        except Exception as exc:
            logger.error(f"[AUTO-SCHEDULER] Error en ciclo automático: {exc}")
            return {'status': 'error', 'error': str(exc)}
        finally:
            close_old_connections()


def ejecutar_ventana_cron_scheduler(
    max_seconds: float = 210.0,
    batch_size: int = 5,
    delay_seconds: float = 1.0,
    pause_between_batches: float = 3.0,
) -> dict:
    """
    Ejecuta múltiples lotes controlados dentro de una ventana de cron (ej. cada 5 minutos)
    mientras existan certificados pendientes sin intentar, cediendo prioridad inmediata
    si el administrador está transmitiendo desde la consola web.
    """
    window_start = time.monotonic()
    batches_run = 0
    total_processed = 0
    total_errors = 0
    last_result = None

    while (time.monotonic() - window_start) < max_seconds:
        if is_web_console_priority_active():
            return {
                'status': 'yielded_to_web_console',
                'reason': 'web_console_priority',
                'batches_run': batches_run,
                'total_processed': total_processed,
                'total_errors': total_errors,
                'last_result': last_result,
            }

        res = ejecutar_ciclo_scheduler(
            batch_size=batch_size,
            delay_seconds=delay_seconds,
            min_interval_seconds=0.0,
        )
        last_result = res
        if res.get('status') != 'ok':
            break

        certs_info = res.get('certificates') or {}
        if not certs_info.get('executed'):
            break

        batches_run += 1
        inner = certs_info.get('result') or {}
        total_processed += int(inner.get('processed', 0) or 0)
        total_errors += int(inner.get('errors', 0) or 0)

        remaining_unattempted = int(certs_info.get('remaining_unattempted', 0) or 0)
        if remaining_unattempted <= 0:
            break

        if pause_between_batches > 0:
            if (time.monotonic() - window_start + pause_between_batches) >= max_seconds:
                break
            time.sleep(pause_between_batches)

    return {
        'status': 'ok',
        'batches_run': batches_run,
        'total_processed': total_processed,
        'total_errors': total_errors,
        'last_result': last_result,
    }


def _debe_iniciar_scheduler() -> bool:
    """
    Determina si el proceso actual corresponde al servidor web activo (Gunicorn / runserver)
    y NO a comandos transitorios como test, migrate, collectstatic, etc.
    """
    if os.environ.get('DISABLE_INTERNAL_SCHEDULER') == '1':
        return False

    argv_lower = [str(arg).lower() for arg in sys.argv]
    comandos_excluidos = {
        'test', 'migrate', 'makemigrations', 'collectstatic', 'dumpdata',
        'loaddata', 'shell', 'dbshell', 'check', 'compileall',
        'sync_pg_sequences', 'procesar_cola_certificados', 'generar_respaldo',
        'createsuperuser', 'inspectdb', 'flush', 'showmigrations'
    }
    if any(cmd in argv_lower for cmd in comandos_excluidos):
        return False

    # Iniciar si corre bajo Gunicorn/uWSGI o runserver principal
    es_servidor_wsgi = any('gunicorn' in arg or 'uwsgi' in arg or 'daphne' in arg or 'uvicorn' in arg for arg in argv_lower)
    es_runserver = 'runserver' in argv_lower and (os.environ.get('RUN_MAIN') == 'true' or '--noreload' in argv_lower)

    return es_servidor_wsgi or es_runserver


def iniciar_scheduler_en_segundo_plano():
    """
    Inicia un hilo daemon liviano en el proceso del servidor para garantizar que
    el despacho por lotes de certificados después de las 18:00 hs se cumpla puntualmente
    coordinado en PostgreSQL, cediendo prioridad inmediata si el administrador inicia el envío desde la consola web.
    Soporta Gunicorn con --preload detectando cambios de PID tras fork().
    """
    global _scheduler_started, _scheduler_pid, _scheduler_thread
    if not _debe_iniciar_scheduler():
        return False

    current_pid = os.getpid()
    with _scheduler_lock:
        if (
            _scheduler_started
            and _scheduler_pid == current_pid
            and _scheduler_thread is not None
            and _scheduler_thread.is_alive()
        ):
            return False
        _scheduler_started = True
        _scheduler_pid = current_pid

    def _loop():
        time.sleep(8)
        logger.info("[AUTO-SCHEDULER] Hilo de automatización de cola de certificados iniciado (PostgreSQL coordinado).")
        while True:
            try:
                res = ejecutar_ciclo_scheduler(batch_size=5, delay_seconds=1, min_interval_seconds=10.0)
                certs_info = res.get('certificates') or {}
                if certs_info.get('executed') and certs_info.get('remaining_unattempted', 0) > 0:
                    # Si hay certificados pendientes en cola, procesar el siguiente lote tras una pausa breve
                    time.sleep(12)
                else:
                    time.sleep(45)
            except Exception as err:
                logger.error(f"[AUTO-SCHEDULER] Excepción no controlada en hilo: {err}")
                time.sleep(60)

    thread = threading.Thread(target=_loop, name='congreso-auto-scheduler', daemon=True)
    with _scheduler_lock:
        _scheduler_thread = thread
    thread.start()
    return True
