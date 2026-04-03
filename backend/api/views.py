from rest_framework import viewsets, mixins, status, views, serializers, permissions
from typing import Any
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import Disertante, Inscripcion, Programa, Certificado, Asistente, Empresa, MiembroGrupo, PostulacionDisertante, Edicion, InscripcionPrensa
from .serializers import (
    EdicionSerializer, DisertanteSerializer, EmpresaSerializer, 
    ProgramaSerializer, AsistenteSerializer, InscripcionSerializer,
    PostulacionDisertanteSerializer, InscripcionPrensaSerializer,
    EmpresaLogoSerializer, MiembroGrupoSerializer
)
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from .email import (
    send_confirmation_email, send_bulk_confirmation_email, 
    send_certificate_email, send_admin_postulation_alert
)
import pandas as pd
import re


class GetCSRFTokenView(views.APIView):
    """
    Vista simple para obtener un token CSRF.
    Esto es útil para aplicaciones frontend que necesitan obtener
    el token antes de hacer peticiones POST.
    
    IMPORTANTE: No usar @ensure_csrf_cookie ya que fuerza HTTPOnly=True
    En su lugar, llamamos manualmente get_token() que respeta CSRF_COOKIE_HTTPONLY=False
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Forzar la creación del token CSRF
        csrf_token = get_token(request)
        return Response({
            'detail': 'CSRF cookie set',
            'csrfToken': csrf_token  # También lo devolvemos en la respuesta por si acaso
        }, status=status.HTTP_200_OK)

class EdicionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar las ediciones disponibles del congreso.
    """
    queryset = Edicion.objects.all().order_by('-anio')
    serializer_class = EdicionSerializer
    permission_classes = [AllowAny]

class DisertanteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Un ViewSet para ver la lista de disertantes y los detalles de uno específico.
    Filtra por edición activa y estado APROBADO.
    """
    serializer_class = DisertanteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        edicion_id = self.request.query_params.get('edicion_id')
        queryset = Disertante.objects.filter(estado='APROBADO')
        if edicion_id:
            queryset = queryset.filter(edicion_id=edicion_id)
        else:
            queryset = queryset.filter(edicion__activa=True)
        return queryset

class ProgramaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Un ViewSet para ver el programa del congreso, ordenado por día y hora.
    Soporta filtrado por edición.
    """
    serializer_class = ProgramaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        edicion_id = self.request.query_params.get('edicion_id')
        queryset = Programa.objects.all().order_by('dia', 'hora_inicio')
        if edicion_id:
            queryset = queryset.filter(edicion_id=edicion_id)
        else:
            queryset = queryset.filter(edicion__activa=True)
        return queryset

class RegistroEmpresasView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Vista para el registro de empresas.
    """
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        from django.db import transaction
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                empresa = serializer.save()
                
                # Enviar email de confirmación al contacto de la empresa
                from .email import send_empresa_confirmation_email
                email_success = False
                try:
                    email_success = send_empresa_confirmation_email(empresa)
                except Exception as e:
                    print(f"[ERROR] No se pudo enviar el email de confirmación a la empresa: {e}")
                
                msg = 'Registro de empresa realizado correctamente.'
                if email_success:
                    msg += ' Se ha enviado un email de confirmación.'
                else:
                    msg += ' Registro guardado, pero ocurrió un problema al enviar el correo.'

                return Response({'status': 'success', 'message': msg, 'id': empresa.id}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"[ERROR] Error inesperado en RegistroEmpresasView: {str(e)}")
            return Response({'status': 'error', 'message': f'Ha ocurrido un error inesperado al procesar el registro de la empresa. Por favor intente más tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegistroDisertanteView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Vista para procesar las postulaciones del Call for Papers a Disertantes.
    """
    queryset = PostulacionDisertante.objects.all()
    serializer_class = PostulacionDisertanteSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        from django.db import transaction
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                postulacion = serializer.save()
                
                # Enviar email de confirmación de postulación
                from .email import send_postulacion_disertante_email
                email_success = False
                try:
                    email_success = send_postulacion_disertante_email(postulacion)
                except Exception as e:
                    print(f"[ERROR] Fallo crítico al enviar email de disertante: {e}")
                
                msg = 'Postulación recibida correctamente.'
                if email_success:
                    msg += ' Se ha enviado un email de confirmación.'
                else:
                    msg += ' Postulación guardada, pero ocurrió un problema al enviar el correo.'
                    
                return Response({'status': 'success', 'message': msg, 'id': postulacion.id}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            error_messages: dict[str, Any] = {}
            if isinstance(e.detail, dict):
                for field, errors in e.detail.items():
                    if isinstance(errors, list):
                        error_messages[field] = [str(err) for err in errors]
                    else:
                        error_messages[field] = str(errors)
            else:
                error_messages = {'detail': str(e.detail)}
            return Response({'status': 'error', 'message': error_messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"[ERROR] Error inesperado en RegistroDisertanteView: {str(e)}")
            return Response({'status': 'error', 'message': f'Ha ocurrido un error inesperado al procesar su postulación. Por favor intente nuevamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AsistenteCRMView(views.APIView):
    """
    Endpoint para buscar un Asistente por su DNI.
    Devuelve sus datos básicos (CRM) para que el frontend auto-complete y realice un Upsert.
    """
    permission_classes = [AllowAny]

    def get(self, request, dni, *args, **kwargs):
        try:
            asistente = Asistente.objects.get(dni=dni)
            serializer = AsistenteSerializer(asistente)
            return Response({
                'status': 'success',
                'asistente': serializer.data
            }, status=status.HTTP_200_OK)
        except Asistente.DoesNotExist:
            return Response({
                'status': 'not_found',
                'message': 'Asistente no encontrado en CRM histórico.'
            }, status=status.HTTP_404_NOT_FOUND)

class EmpresaCRMView(views.APIView):
    """
    Endpoint para buscar una Empresa por su Email de contacto (CRM).
    Devuelve sus datos básicos para que el frontend auto-complete y realice un Upsert.
    """
    permission_classes = [AllowAny]

    def get(self, request, email, *args, **kwargs):
        try:
            empresa = Empresa.objects.get(email_empresa=email)
            serializer = EmpresaSerializer(empresa)
            return Response({
                'status': 'success',
                'empresa': serializer.data
            }, status=status.HTTP_200_OK)
        except Empresa.DoesNotExist:
            return Response({
                'status': 'not_found',
                'message': 'Empresa no encontrada en CRM histórico.'
            }, status=status.HTTP_404_NOT_FOUND)

class DisertanteCRMView(views.APIView):
    """
    Endpoint para buscar una Postulación Disertante por su DNI (CRM).
    Devuelve sus datos básicos para auto-completar.
    """
    permission_classes = [AllowAny]

    def get(self, request, dni, *args, **kwargs):
        try:
            postulacion = PostulacionDisertante.objects.get(dni=dni)
            serializer = PostulacionDisertanteSerializer(postulacion)
            return Response({
                'status': 'success',
                'disertante': serializer.data
            }, status=status.HTTP_200_OK)
        except PostulacionDisertante.DoesNotExist:
            return Response({
                'status': 'not_found',
                'message': 'Postulante no encontrado en CRM histórico.'
            }, status=status.HTTP_404_NOT_FOUND)


class RegistroViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Un ViewSet único y transaccional para la creación de nuevas inscripciones.
    Maneja inscripciones individuales y grupales (Upsert en Asistente + nueva Inscripción).
    """
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                inscripcion = serializer.save()
                
                # Email de confirmación se maneja dentro de AsistenteSerializer
                asistente = inscripcion.asistente
                email_success = getattr(asistente, '_email_enviado', False)
                
                msg = 'Registro de participante realizado correctamente.'
                if email_success:
                    msg += ' Se ha enviado un email de confirmación.'
                else:
                    msg += ' Registro guardado, pero ocurrió un problema al enviar el correo.'
                
                headers = self.get_success_headers(serializer.data)
                return Response({'status': 'success', 'message': msg, 'id': inscripcion.id}, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            error_messages: dict[str, Any] = {}
            if isinstance(e.detail, dict):
                for field, errors in e.detail.items():
                    if isinstance(errors, list):
                        error_messages[field] = [str(err) for err in errors]
                    else:
                        error_messages[field] = str(errors)
            else:
                error_messages = {'detail': str(e.detail)}
            return Response({'status': 'error', 'message': error_messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"[ERROR] Error inesperado en RegistroViewSet: {str(e)}")
            return Response({'status': 'error', 'message': f'Ha ocurrido un error inesperado al procesar su inscripción. Por favor intente nuevamente.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerificarDNIView(views.APIView):
    """
    Vista para verificar si un DNI está registrado y confirmar asistencia.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        dni = request.data.get('dni')
        if not dni:
            return Response({'status': 'error', 'message': 'No se proporcionó DNI.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener la edición activa
            edicion_activa = Edicion.objects.filter(activa=True).first()
            if not edicion_activa:
                return Response({'status': 'error', 'message': 'No hay una edición activa configurada.'}, status=400)

            # Buscar al asistente e inscripción para la edición activa
            asistente = Asistente.objects.get(dni=dni)
            inscripcion = asistente.inscripciones.filter(edicion=edicion_activa).first()
            
            if not inscripcion:
                return Response({
                    'status': 'error', 
                    'message': f'El asistente está registrado en el sistema pero no tiene inscripción para la edición activa ({edicion_activa.nombre}).'
                }, status=403)
                
            if inscripcion.asistencia_confirmada:
                fecha_confirmacion_str = inscripcion.fecha_confirmacion.strftime("%d/%m/%Y a las %H:%M:%S") if inscripcion.fecha_confirmacion else "fecha desconocida"
                return Response({
                    'status': 'error',
                    'message': f'La asistencia ya fue confirmada el {fecha_confirmacion_str}.',
                }, status=status.HTTP_409_CONFLICT)

        except Asistente.DoesNotExist:
            return Response({'status': 'error', 'message': 'DNI no encontrado en el listado de registrados.'}, status=status.HTTP_404_NOT_FOUND)

        # Confirmar asistencia en la inscripción
        inscripcion.asistencia_confirmada = True
        inscripcion.fecha_confirmacion = timezone.now()
        inscripcion.save()

        # Crear certificado de asistencia
        certificado, created = Certificado.objects.get_or_create(
            asistente=asistente,
            tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
        )
        
        # Enviar el certificado por email
        email_success = send_certificate_email(certificado)

        # --- Determinar tipo de pantalla para los 7 casos QR ---
        perfil   = asistente.profile_type
        nombre   = f"{asistente.first_name} {asistente.last_name}"
        pantalla = 'GENERAL'
        subtitulo = ''
        nombre_vinculado = ''

        if perfil == 'GROUP_REPRESENTATIVE':
            pantalla = 'REPRESENTANTE_GRUPO'
            try:
                dg = asistente.detalle_grupo
                nombre_vinculado = dg.group_name or ''
            except Exception:
                nombre_vinculado = ''
            subtitulo = f'Representante de Grupo: {nombre_vinculado}' if nombre_vinculado else 'Representante de Grupo'

        elif asistente.representante_grupo_id:
            pantalla = 'MIEMBRO_GRUPO'
            try:
                rep = asistente.representante_grupo
                dg = rep.detalle_grupo
                nombre_vinculado = dg.group_name or ''
            except Exception:
                nombre_vinculado = ''
            subtitulo = f'Miembro de {nombre_vinculado}' if nombre_vinculado else 'Miembro de Grupo'

        elif asistente.empresa_vinculada_id:
            pantalla = 'REPRESENTANTE_EMPRESA'
            nombre_vinculado = asistente.empresa_vinculada.nombre_empresa if asistente.empresa_vinculada else ''
            subtitulo = f'Representante de {nombre_vinculado}' if nombre_vinculado else 'Representante de Empresa'

        elif asistente.disertante_vinculado_id:
            pantalla = 'DISERTANTE'
            subtitulo = 'Disertante del Congreso'

        elif asistente.prensa_vinculada_id or perfil == 'PRESS':
            pantalla = 'PRENSA'
            subtitulo = 'Prensa Acreditada'

        asistente_data = {
            'nombre_completo': nombre,
            'email': asistente.email,
            'dni': asistente.dni,
            'profile_type': perfil,
        }

        msg = 'Asistencia confirmada con exito.' if email_success else 'Asistencia confirmada con exito (email no configurado).'

        return Response({
            'status': 'success',
            'message': msg,
            'asistente': asistente_data,
            'pantalla': {
                'tipo': pantalla,
                'subtitulo': subtitulo,
                'nombre_vinculado': nombre_vinculado,
            }
        }, status=status.HTTP_200_OK)

class RegistroRapidoView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Vista para registro rápido in-situ en el evento.
    """
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            inscripcion = serializer.save()
            
            # Confirmar asistencia inmediatamente para registro in-situ
            inscripcion.asistencia_confirmada = True
            inscripcion.fecha_confirmacion = timezone.now()
            inscripcion.save()
            
            # Crear certificado de asistencia
            certificado, created = Certificado.objects.get_or_create(
                asistente=asistente,
                tipo_certificado=Certificado.TipoCertificado.ASISTENCIA
            )
            
            # Enviar el certificado por email
            email_success = send_certificate_email(certificado)
            
            headers = self.get_success_headers(serializer.data)
            msg = 'Registro completado. Asistencia confirmada y certificado enviado por email.' if email_success else 'Registro completado y asistencia confirmada, pero no se pudo enviar el certificado por email (sistema de correos no configurado).'
            return Response({
                'status': 'success', 
                'message': msg
            }, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'status': 'error', 'message': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': f'Ha ocurrido un error inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmpresaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver la lista de empresas participantes.
    Solo permite lectura (GET) para mostrar logos en carrusel/slider.
    """
    serializer_class = EmpresaLogoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        edicion_id = self.request.query_params.get('edicion_id')
        queryset = Empresa.objects.filter(
            estado='APROBADO', 
            logo__isnull=False
        ).exclude(logo='')
        
        if edicion_id:
            queryset = queryset.filter(edicion_id=edicion_id)
        else:
            queryset = queryset.filter(edicion__activa=True)
            
        return queryset.order_by('nombre_empresa')


class EnvioMasivoEmailsView(views.APIView):
    """
    Vista para envío masivo de emails a todos los asistentes registrados.
    Envía emails de confirmación con la fecha correcta del evento: 7 de noviembre de 2026.
    """
    permission_classes = [AllowAny]  # En producción, cambiar por permisos de administrador

    def get(self, request, *args, **kwargs):
        """Método GET para mostrar estadísticas de emails"""
        total_asistentes = Asistente.objects.count()
        sin_dni = Asistente.objects.filter(dni__isnull=True).count()
        con_dni = Asistente.objects.filter(dni__isnull=False).count()
        
        return Response({
            'status': 'info',
            'message': 'Endpoint para envío masivo de emails',
            'estadisticas': {
                'total_asistentes': total_asistentes,
                'con_dni': con_dni,
                'sin_dni': sin_dni,
                'fecha_evento': '7 de noviembre de 2026'
            },
            'parametros_post': {
                'tipo_email': 'confirmacion/recordatorio - OPCIONAL (default: confirmacion)',
                'solo_sin_dni': 'true/false - OPCIONAL (default: false)',
                'fecha_evento_override': 'YYYY-MM-DD - OPCIONAL (default: 2026-11-07)'
            }
        })

    def post(self, request, *args, **kwargs):
        """Envío masivo de emails a los asistentes usando hilos para evitar timeouts"""
        import threading
        import logging
        
        logger = logging.getLogger(__name__)
        
        tipo_email = request.data.get('tipo_email', 'confirmacion')
        solo_sin_dni = request.data.get('solo_sin_dni', 'false').lower() == 'true'
        fecha_evento = request.data.get('fecha_evento_override', '2026-11-07')
        
        # Filtrar asistentes según parámetros
        if solo_sin_dni:
            asistentes = list(Asistente.objects.filter(dni__isnull=True))
            descripcion = "asistentes sin DNI"
        else:
            asistentes = list(Asistente.objects.all())
            descripcion = "todos los asistentes"
        
        total_asistentes = len(asistentes)
        
        if total_asistentes == 0:
            return Response({
                'status': 'warning',
                'message': f'No hay {descripcion} para enviar emails.'
            }, status=status.HTTP_200_OK)

        def run_bulk_email_task(asistentes_list, t_email, f_evento):
            total = len(asistentes_list)
            enviados = 0
            fallidos = 0
            logger.info(f"Iniciando tarea de fondo: {total} emails de tipo {t_email} para la fecha {f_evento}")
            
            for asistente in asistentes_list:
                try:
                    if t_email == 'recordatorio':
                        email_enviado = send_bulk_confirmation_email(
                            asistente, 
                            es_recordatorio=True,
                            fecha_evento=f_evento
                        )
                    else:
                        email_enviado = send_bulk_confirmation_email(
                            asistente, 
                            es_carga_masiva=True,
                            fecha_evento=f_evento
                        )
                    
                    if email_enviado:
                        enviados += 1
                    else:
                        fallidos += 1
                except Exception as e:
                    fallidos += 1
                    logger.error(f"Error en tarea de fondo enviando a {asistente.email}: {e}")
            
            logger.info(f"Tarea de fondo completada. Enviados: {enviados}, Fallidos: {fallidos}")

        # Iniciar el hilo de fondo
        thread = threading.Thread(target=run_bulk_email_task, args=(asistentes, tipo_email, fecha_evento))
        thread.daemon = True
        thread.start()
        
        return Response({
            'status': 'success',
            'message': f"Se ha iniciado el envío masivo en segundo plano para {total_asistentes} registros ({descripcion}).",
            'info': {
                'tipo_email': tipo_email,
                'fecha_evento': fecha_evento,
                'total_a_procesar': total_asistentes
            }
        }, status=status.HTTP_202_ACCEPTED)


class CargaMasivaAsistentesCompletaView(views.APIView):
    """
    Vista para carga masiva de asistentes desde archivo Excel/CSV.
    Maneja DNIs nulos y asigna perfil 'OTRO' por defecto cuando el tipo de perfil está vacío.
    """
    permission_classes = [AllowAny]  # En producción, cambiar por permisos de administrador

    def get(self, request, *args, **kwargs):
        """Método GET para mostrar información sobre el endpoint"""
        return Response({
            'status': 'info',
            'message': 'Endpoint para carga masiva de asistentes',
            'metodo': 'POST',
            'parametros': {
                'archivo': 'Archivo Excel (.xlsx, .xls) o CSV (.csv) - REQUERIDO',
                'enviar_emails': 'true/false - OPCIONAL (default: true)'
            },
            'estructura_archivo': {
                'columnas_requeridas': ['NOMBRE', 'Apellido', 'CORREO ELECTRONICO'],
                'columnas_opcionales': [
                    'NUMERO DE CELULAR (con codigo de area)',
                    'DNI',
                    'TIPO DE PERFIL',
                    'Columna1'
                ]
            },
            'tipos_perfil_validos': [
                'VISITOR (Visitante)',
                'STUDENT (Estudiante)', 
                'TEACHER (Docente)',
                'PROFESSIONAL (Profesional)',
                'GROUP_REPRESENTATIVE (Representante de Grupo)',
                'GRADUADO',
                'OTRO (Por defecto)'
            ]
        })

    def post(self, request, *args, **kwargs):
        if 'archivo' not in request.FILES:
            return Response({
                'status': 'error',
                'message': 'No se proporcionó archivo para cargar. Use el parámetro "archivo".'
            }, status=status.HTTP_400_BAD_REQUEST)

        archivo = request.FILES['archivo']
        enviar_emails = request.data.get('enviar_emails', 'true').lower() == 'true'
        edicion_anio = request.data.get('edicion_anio')
        
        edicion = None
        if edicion_anio:
            try:
                edicion, _ = Edicion.objects.get_or_create(
                    anio=int(edicion_anio),
                    defaults={'nombre': f'Congreso de Logística {edicion_anio}', 'activa': False}
                )
            except ValueError:
                return Response({'status': 'error', 'message': 'edicion_anio debe ser un número válido.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            edicion = Edicion.objects.filter(activa=True).first()
        
        try:
            # Validar tipo de archivo
            if not (archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls') or archivo.name.endswith('.csv')):
                return Response({
                    'status': 'error',
                    'message': 'Tipo de archivo no soportado. Use Excel (.xlsx, .xls) o CSV.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Leer el archivo
            try:
                # pandas ya está importado arriba como pd
                if archivo.name.endswith('.csv'):
                    df = pd.read_csv(archivo)
                else:
                    df = pd.read_excel(archivo)
            except ImportError:
                return Response({
                    'status': 'error',
                    'message': 'pandas no está instalado. Instale pandas para procesar archivos Excel/CSV.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': f'Error al leer el archivo: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mapear columnas esperadas (basado en la imagen proporcionada)
            columnas_esperadas = {
                'NOMBRE': ['nombre', 'first_name', 'primer_nombre'],
                'Apellido': ['apellido', 'last_name'],
                'CORREO ELECTRONICO': ['correo', 'email', 'correo_electronico', 'correo electrónico', 'correo_electrónico'],
                'NUMERO DE CELULAR (con código de área)': ['telefono', 'phone', 'celular', 'numero_celular', 'número de celular (con código de área)', 'numero de celular (con codigo de area)'],
                'DNI': ['dni', 'documento'],
                'TIPO DE PERFIL': ['tipo_perfil', 'profile_type', 'tipo_de_perfil', 'tipo de perfil'],
                'Columna1': ['columna1', 'rol_especifico', 'rol', 'column1']
            }

            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip()
            columnas_mapeadas = {}
            
            for col_esperada, variantes in columnas_esperadas.items():
                for col in df.columns:
                    if col == col_esperada or col.lower() in [v.lower() for v in variantes]:
                        columnas_mapeadas[col_esperada] = col
                        break

            # Verificar columnas mínimas requeridas
            columnas_requeridas = ['NOMBRE', 'Apellido', 'CORREO ELECTRONICO']
            columnas_faltantes: list[str] = []
            for col in columnas_requeridas:
                if col not in columnas_mapeadas:
                    columnas_faltantes.append(str(col))

            if columnas_faltantes:
                return Response({
                    'status': 'error',
                    'message': f'Faltan columnas requeridas: {", ".join(columnas_faltantes)}',
                    'columnas_disponibles': list(df.columns),
                    'columnas_esperadas': list(columnas_esperadas.keys())
                }, status=status.HTTP_400_BAD_REQUEST)

            # Procesar registros
            total_procesados = 0
            exitosos = 0
            errores = 0
            emails_enviados = 0
            emails_fallidos = 0
            detalles_list = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    fila_nro = index + 2 # type: ignore
                    try:
                        # Extraer datos de la fila
                        first_name = str(row[columnas_mapeadas['NOMBRE']]).strip() if pd.notna(row[columnas_mapeadas['NOMBRE']]) else ''
                        last_name = str(row[columnas_mapeadas['Apellido']]).strip() if pd.notna(row[columnas_mapeadas['Apellido']]) else ''
                        email = str(row[columnas_mapeadas['CORREO ELECTRONICO']]).strip() if pd.notna(row[columnas_mapeadas['CORREO ELECTRONICO']]) else ''
                        
                        # Validar datos mínimos
                        if not first_name or not last_name or not email:
                            errores += 1
                            detalles_list.append({
                                'fila': fila_nro,
                                'error': 'Faltan datos básicos (nombre, apellido, email)',
                                'datos': {'nombre': first_name, 'apellido': last_name, 'email': email}
                            })
                            continue

                        # Validar formato de email
                        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                            errores += 1
                            detalles_list.append({
                                'fila': fila_nro,
                                'error': 'Formato de email inválido',
                                'datos': {'email': email}
                            })
                            continue

                        # Verificar si ya existe el email para Upsert
                        asistente_by_email = Asistente.objects.filter(email=email).first()

                        # Procesar DNI (puede ser nulo)
                        dni = None
                        asistente_by_dni = None
                        if 'DNI' in columnas_mapeadas and pd.notna(row[columnas_mapeadas['DNI']]): # type: ignore
                            dni_raw = str(row[columnas_mapeadas['DNI']]).strip()
                            # Limpiar DNI (remover puntos, guiones, etc.)
                            dni = re.sub(r'[^\d]', '', dni_raw)
                            if not dni or len(dni) == 0:
                                dni = None
                            else:
                                asistente_by_dni = Asistente.objects.filter(dni=dni).first()

                        # Procesar teléfono (puede ser vacío)
                        phone = ''
                        if 'NUMERO DE CELULAR (con código de área)' in columnas_mapeadas and pd.notna(row[columnas_mapeadas['NUMERO DE CELULAR (con código de área)']]): # type: ignore
                            phone = str(row[columnas_mapeadas['NUMERO DE CELULAR (con código de área)']]).strip()

                        # Procesar tipo de perfil
                        profile_type = Asistente.ProfileType.OTRO  # Por defecto OTRO
                        if 'TIPO DE PERFIL' in columnas_mapeadas and pd.notna(row[columnas_mapeadas['TIPO DE PERFIL']]): # type: ignore
                            tipo_perfil_raw = str(row[columnas_mapeadas['TIPO DE PERFIL']]).strip().upper()
                            
                            # Mapear tipos de perfil
                            mapeo_perfiles = {
                                'VISITANTE': Asistente.ProfileType.VISITOR,
                                'ESTUDIANTE': Asistente.ProfileType.STUDENT,
                                'DOCENTE': Asistente.ProfileType.TEACHER,
                                'PROFESIONAL': Asistente.ProfileType.PROFESSIONAL,
                                'GRADUADO': Asistente.ProfileType.GRADUADO,
                                'OTRO': Asistente.ProfileType.OTRO,
                                'VISITOR': Asistente.ProfileType.VISITOR,
                                'STUDENT': Asistente.ProfileType.STUDENT,
                                'TEACHER': Asistente.ProfileType.TEACHER,
                                'PROFESSIONAL': Asistente.ProfileType.PROFESSIONAL
                            }
                            
                            if tipo_perfil_raw in mapeo_perfiles:
                                profile_type = mapeo_perfiles[tipo_perfil_raw]

                        # Procesar rol específico (Columna1)
                        rol_especifico = None
                        if 'Columna1' in columnas_mapeadas and pd.notna(row[columnas_mapeadas['Columna1']]): # type: ignore
                            rol_especifico = str(row[columnas_mapeadas['Columna1']]).strip()

                        # Crear o actualizar asistente (upsert)
                        asistente = asistente_by_dni or asistente_by_email
                        
                        if asistente:
                            asistente.first_name = first_name
                            asistente.last_name = last_name
                            asistente.phone = phone
                            asistente.profile_type = profile_type
                            asistente.rol_especifico = rol_especifico
                            if dni:
                                asistente.dni = dni
                            asistente.save()
                        else:
                            asistente = Asistente.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone,
                                dni=dni,
                                profile_type=profile_type,
                                rol_especifico=rol_especifico
                            )
                        
                        # Crear inscripción para la edición actual o dada
                        if edicion and not Inscripcion.objects.filter(asistente=asistente, edicion=edicion).exists():
                            Inscripcion.objects.create(asistente=asistente, edicion=edicion)

                        exitosos += 1
                        detalles_list.append({
                            'fila': fila_nro,
                            'success': 'Registro creado exitosamente',
                            'id': asistente.pk,
                            'datos': {
                                'nombre': first_name,
                                'apellido': last_name,
                                'email': email,
                                'dni': dni,
                                'perfil': profile_type,
                                'rol_especifico': rol_especifico
                            }
                        })

                        # Enviar email de confirmación si está habilitado
                        if enviar_emails:
                            try:
                                if send_bulk_confirmation_email(asistente, es_carga_masiva=True):
                                    emails_enviados += 1
                                else:
                                    emails_fallidos += 1
                            except Exception as e:
                                emails_fallidos += 1
                                print(f"[ERROR] Error enviando email a {email}: {e}")

                    except Exception as e:
                        errores += 1
                        detalles_list.append({
                            'fila': fila_nro,
                            'error': f'Error procesando fila: {str(e)}'
                        })

                    total_procesados += 1

            resultados = {
                'total_procesados': total_procesados,
                'exitosos': exitosos,
                'errores': errores,
                'emails_enviados': emails_enviados,
                'emails_fallidos': emails_fallidos,
                'detalles': detalles_list
            }

            return Response({
                'status': 'success',
                'message': f'Carga masiva completada. {exitosos} registros exitosos, {errores} errores.',
                'resultados': resultados
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error procesando archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CargaMasivaAsistentesView(views.APIView):
    """
    Vista para carga masiva de asistentes desde archivo Excel.
    Permite subir un archivo Excel con datos de asistentes y procesarlos en lote.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Método GET para mostrar información sobre la carga masiva"""
        return Response({
            'status': 'info',
            'message': 'Endpoint para carga masiva de asistentes desde Excel',
            'instrucciones': {
                'metodo': 'POST',
                'contenido': 'multipart/form-data',
                'parametros': {
                    'archivo': 'Archivo Excel (.xlsx o .xls) con datos de asistentes',
                    'enviar_emails': 'true/false - OPCIONAL (default: false)'
                }
            },
            'formato_excel': {
                'columnas_requeridas': [
                    'Nombre',
                    'Apellido', 
                    'Email',
                    'Institucion',
                    'Tipo de Perfil',
                    'DNI (opcional)',
                    'Columna1 (rol específico)'
                ],
                'tipos_perfil_validos': ['VISITOR', 'STUDENT', 'TEACHER', 'PROFESSIONAL', 'GRADUADO', 'OTRO']
            }
        })

    def post(self, request, *args, **kwargs):
        """Procesar archivo Excel para carga masiva"""
        if 'archivo' not in request.FILES:
            return Response({
                'status': 'error',
                'message': 'No se proporcionó ningún archivo'
            }, status=status.HTTP_400_BAD_REQUEST)

        archivo = request.FILES['archivo']
        enviar_emails = request.data.get('enviar_emails', 'false').lower() == 'true'
        edicion_anio = request.data.get('edicion_anio')
        
        edicion = None
        if edicion_anio:
            try:
                edicion, _ = Edicion.objects.get_or_create(
                    anio=int(edicion_anio),
                    defaults={'nombre': f'Congreso de Logística {edicion_anio}', 'activa': False}
                )
            except ValueError:
                return Response({'status': 'error', 'message': 'edicion_anio debe ser un número válido.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            edicion = Edicion.objects.filter(activa=True).first()

        try:
            # Leer archivo Excel
            if archivo.name.endswith('.xlsx'):
                df = pd.read_excel(archivo, engine='openpyxl')
            elif archivo.name.endswith('.xls'):
                df = pd.read_excel(archivo, engine='xlrd')
            else:
                return Response({
                    'status': 'error',
                    'message': 'Formato de archivo no soportado. Use .xlsx o .xls'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mapear nombres de columnas en español a inglés
            column_mapping = {
                'Nombre': 'first_name',
                'Apellido': 'last_name', 
                'Email': 'email',
                'Institucion': 'institution',
                'Tipo de Perfil': 'profile_type',
                'DNI': 'dni',
                'Columna1': 'rol_especifico'
            }

            # Renombrar columnas
            df.rename(columns=column_mapping, inplace=True)

            total_procesados = 0
            exitosos = 0
            errores = 0
            emails_enviados = 0
            emails_fallidos = 0
            detalles_list = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    fila_nro = index + 2 # type: ignore
                    try:
                        # Validar email
                        email = str(row.get('email', '')).strip()
                        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                            errores += 1
                            detalles_list.append({
                                'fila': fila_nro,
                                'email': email,
                                'error': 'Email inválido o vacío'
                            })
                            continue

                        # Verificar si ya existe el email para Upsert
                        asistente_by_email = Asistente.objects.filter(email=email).first()

                        # Mapear tipo de perfil
                        profile_type_map = {
                            'VISITOR': Asistente.ProfileType.VISITOR,
                            'STUDENT': Asistente.ProfileType.STUDENT,
                            'TEACHER': Asistente.ProfileType.TEACHER,
                            'PROFESSIONAL': Asistente.ProfileType.PROFESSIONAL,
                            'GRADUADO': Asistente.ProfileType.GRADUADO,
                            'OTRO': Asistente.ProfileType.OTRO
                        }

                        profile_type_str = str(row.get('profile_type', 'VISITOR')).upper()
                        profile_type = profile_type_map.get(profile_type_str, Asistente.ProfileType.VISITOR)

                        # Crear asistente
                        dni = row.get('dni')
                        if pd.isna(dni) or dni == '':
                            dni = None
                            
                        asistente_by_dni = None
                        if dni:
                            dni_str = str(dni).strip()
                            asistente_by_dni = Asistente.objects.filter(dni=dni_str).first()
                            
                        asistente = asistente_by_dni or asistente_by_email
                        
                        first_name = str(row.get('first_name', '')).strip()
                        last_name = str(row.get('last_name', '')).strip()
                        institution = str(row.get('institution', '')).strip() or None
                        rol_especifico = str(row.get('rol_especifico', '')).strip() or None
                        
                        if asistente:
                            asistente.first_name = first_name
                            asistente.last_name = last_name
                            asistente.profile_type = profile_type
                            if dni:
                                asistente.dni = str(dni).strip()
                            if rol_especifico:
                                asistente.rol_especifico = rol_especifico
                            asistente.save()
                        else:
                            asistente = Asistente.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                profile_type=profile_type,
                                dni=str(dni).strip() if dni else None,
                                rol_especifico=rol_especifico
                            )
                            
                        # Manejar institution
                        if institution:
                            from .models import DetalleEstudiante, DetalleDocente
                            if profile_type == Asistente.ProfileType.STUDENT:
                                DetalleEstudiante.objects.update_or_create(asistente=asistente, defaults={'institution': institution})
                            elif profile_type == Asistente.ProfileType.TEACHER:
                                DetalleDocente.objects.update_or_create(asistente=asistente, defaults={'institution': institution})

                        # Crear inscripción vinculada a la edicion correspondiente
                        if edicion and not Inscripcion.objects.filter(asistente=asistente, edicion=edicion).exists():
                            Inscripcion.objects.create(asistente=asistente, edicion=edicion)

                        exitosos += 1
                        detalles_list.append({
                            'fila': fila_nro,
                            'email': email,
                            'nombre': f"{asistente.first_name} {asistente.last_name}",
                            'profile_type': asistente.get_profile_type_display(), # type: ignore
                            'estado': 'creado'
                        })

                        # Enviar email si está habilitado
                        if enviar_emails:
                            try:
                                if send_bulk_confirmation_email(asistente, es_carga_masiva=True, fecha_evento='2026-11-07'):
                                    emails_enviados += 1
                                else:
                                    emails_fallidos += 1
                            except Exception as e:
                                emails_fallidos += 1
                                print(f"[ERROR] Error enviando email a {email}: {e}")

                    except Exception as e:
                        errores += 1
                        detalles_list.append({
                            'fila': fila_nro,
                            'error': f'Error procesando fila: {str(e)}'
                        })

                    total_procesados += 1

            resultados = {
                'total_procesados': total_procesados,
                'exitosos': exitosos,
                'errores': errores,
                'emails_enviados': emails_enviados,
                'emails_fallidos': emails_fallidos,
                'detalles': detalles_list
            }

            return Response({
                'status': 'success',
                'message': f'Carga masiva completada. {exitosos} registros exitosos, {errores} errores.',
                'resultados': resultados
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error procesando archivo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActualizarDNIView(views.APIView):
    """
    Vista para actualizar el DNI de un asistente usando un token único.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Verifica si el token es válido y devuelve la información del asistente.
        """
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'status': 'error',
                'message': 'Token no proporcionado.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asistente = Asistente.objects.get(dni_update_token=token)
            return Response({
                'status': 'success',
                'asistente': {
                    'nombre_completo': asistente.nombre_completo,
                    'email': asistente.email
                }
            }, status=status.HTTP_200_OK)
        except Asistente.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Token inválido o expirado.'
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Actualiza el DNI del asistente y elimina el token.
        """
        token = request.data.get('token')
        nuevo_dni = request.data.get('dni')
        
        if not token or not nuevo_dni:
            return Response({
                'status': 'error',
                'message': 'Token y DNI son requeridos.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asistente = Asistente.objects.get(dni_update_token=token)
            
            # Validar el DNI usando el serializer
            from .serializers import AsistenteSerializer
            serializer = AsistenteSerializer()
            try:
                dni_validado = serializer.validate_dni(nuevo_dni) # type: ignore
            except serializers.ValidationError as e:
                return Response({
                    'status': 'error',
                    'message': str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el DNI ya existe
            if Asistente.objects.filter(dni=dni_validado).exclude(id=asistente.pk).exists():
                return Response({
                    'status': 'error',
                    'message': 'Este DNI ya está registrado en el sistema.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar el DNI y eliminar el token
            asistente.dni = dni_validado
            asistente.dni_update_token = None
            asistente.save()
            
            return Response({
                'status': 'success',
                'message': 'DNI actualizado correctamente.'
            }, status=status.HTTP_200_OK)
            
        except Asistente.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Token inválido o expirado.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error actualizando el DNI: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatsDashboardView(views.APIView):
    """
    Vista para obtener estadísticas generales para el dashboard del admin.
    """
    permission_classes = [AllowAny]  # TODO: Cambiar a IsAdminUser en producción

    def get(self, request):
        try:
            # Obtener edición desde query params o usar la activa
            edicion_id = request.query_params.get('edicion_id')
            if edicion_id:
                try:
                    edicion = Edicion.objects.get(id=edicion_id)
                except (Edicion.DoesNotExist, ValueError):
                    edicion = Edicion.objects.filter(activa=True).first()
            else:
                edicion = Edicion.objects.filter(activa=True).first()

            # 1. Inscripciones por día (últimos 30 días o filtrado por edición)
            # Si no hay edición (raro), no filtramos por ella.
            inscripciones_base = Inscripcion.objects.all()
            if edicion:
                inscripciones_base = inscripciones_base.filter(edicion=edicion)

            hace_30_dias = timezone.now() - timezone.timedelta(days=30)
            inscripciones_por_dia = inscripciones_base.filter(
                fecha_inscripcion__gte=hace_30_dias
            ).annotate(
                date=TruncDate('fecha_inscripcion')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')

            daily_stats = [
                {'date': item['date'].strftime('%Y-%m-%d'), 'count': item['count']}
                for item in inscripciones_por_dia
            ]

            # 2. Comparativa por Edición (Siempre mostramos todas para comparar)
            ediciones_stats = Inscripcion.objects.values(
                'edicion__nombre', 'edicion__anio'
            ).annotate(
                total=Count('id')
            ).order_by('edicion__anio')

            comparative_stats = [
                {'name': f"{item['edicion__nombre']} ({item['edicion__anio']})", 'total': item['total']}
                for item in ediciones_stats
            ]

            # 3. Distribución por Tipo de Perfil (Filtrado por edición seleccionada)
            perfil_stats = Asistente.objects.all()
            if edicion:
                perfil_stats = perfil_stats.filter(inscripciones__edicion=edicion)
            
            perfil_stats = perfil_stats.values(
                'profile_type'
            ).annotate(
                value=Count('id', distinct=True)
            )

            # Mapeo de tipos de perfil a nombres legibles
            profile_map = dict(Asistente.ProfileType.choices)
            distribution_stats = [
                {'name': profile_map.get(item['profile_type'], item['profile_type']), 'value': item['value']}
                for item in perfil_stats
            ]

            # 4. KPIs Generales (Filtrado por edición seleccionada)
            total_inscritos = Inscripcion.objects.filter(edicion=edicion).count() if edicion else 0
            total_confirmados = Inscripcion.objects.filter(
                edicion=edicion,
                asistencia_confirmada=True
            ).distinct().count() if edicion else 0

            return Response({
                'status': 'success',
                'data': {
                    'daily_stats': daily_stats,
                    'comparative_stats': comparative_stats,
                    'distribution_stats': distribution_stats,
                    'kpis': {
                        'total_inscritos': total_inscritos,
                        'total_confirmados': total_confirmados,
                        'asistencia_ratio': float(f"{(total_confirmados / total_inscritos * 100):.2f}") if total_inscritos > 0 else 0.0
                    },
                    'edicion_actual': {
                        'id': edicion.id,
                        'nombre': edicion.nombre,
                        'anio': edicion.anio
                    } if edicion else None,
                    'todas_ediciones': list(Edicion.objects.values('id', 'nombre', 'anio').order_by('-anio'))
                }
            })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al obtener estadísticas: {str(e)}'
            }, status=500)


class InscripcionPrensaView(views.APIView):
    """
    POST /api/inscripcion-prensa/
    Registro voluntario de prensa e influencers sin convocatoria formal.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from django.db import transaction
        try:
            with transaction.atomic():
                serializer = InscripcionPrensaSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response({
                        'status': 'error',
                        'message': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                inscripcion = serializer.save()
                
                # Enviar alerta dedicada al administrador
                try:
                    send_admin_postulation_alert(inscripcion, "Prensa")
                except Exception as e:
                    print(f"[ERROR] No se pudo enviar alerta de prensa al admin: {e}")
                
                return Response({
                    'status': 'success',
                    'message': 'Tu inscripción fue recibida correctamente. Nos pondremos en contacto próximamente.',
                    'id': inscripcion.id,
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"[ERROR] Error inesperado en InscripcionPrensaView: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Ha ocurrido un error inesperado al procesar su solicitud de prensa. Por favor intente más tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BroadcastAPIView(views.APIView):
    """
    POST /api/broadcast/
    Envío de comunicaciones masivas vía API (Solo Admin).
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        rol = request.data.get('rol')
        asunto = request.data.get('asunto')
        mensaje_html = request.data.get('mensaje')

        if not asunto or not mensaje_html:
            return Response({
                'status': 'error',
                'message': 'Asunto y mensaje son obligatorios.'
            }, status=status.HTTP_400_BAD_REQUEST)

        emails = set()
        
        # Lógica de filtrado idéntica a la del Admin
        if rol == 'TODOS' or rol == 'ASISTENTES_TODOS':
            emails.update(Asistente.objects.values_list('email', flat=True))
        
        if rol == 'ASISTENTES_CONFIRMADOS':
            emails.update(Inscripcion.objects.filter(asistencia_confirmada=True).values_list('asistente__email', flat=True))
        
        if rol == 'TODOS' or rol == 'DISERTANTES':
            emails.update(PostulacionDisertante.objects.filter(estado='APROBADO').values_list('email', flat=True))
            
        if rol == 'TODOS' or rol == 'EMPRESAS':
            emails.update(Empresa.objects.filter(estado='APROBADO').values_list('email_contacto', flat=True))
            
        if rol == 'TODOS' or rol == 'PRENSA':
            emails.update(InscripcionPrensa.objects.values_list('email', flat=True))

        # Limpiar emails nulos o vacíos
        emails_list = [e for e in emails if e]

        if not emails_list:
            return Response({
                'status': 'error',
                'message': 'No se encontraron destinatarios para el filtro seleccionado.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Envío en segundo plano para no bloquear la respuesta
        import threading
        def start_broadcast():
            send_broadcast_batch_email(emails_list, asunto, mensaje_html)
            
        thread = threading.Thread(target=start_broadcast)
        thread.start()

        return Response({
            'status': 'success',
            'message': f'Proceso de envío iniciado para {len(emails_list)} destinatarios.'
        }, status=status.HTTP_202_ACCEPTED)
