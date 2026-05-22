from typing import Optional, Tuple
from .models import Edicion, Asistente, Inscripcion

def get_active_edition() -> Optional[Edicion]:
    """
    Retorna la edición activa del congreso o None si no hay ninguna.
    """
    return Edicion.objects.filter(activa=True).first()

def get_asistente_by_dni(dni: str) -> Optional[Asistente]:
    """
    Busca un asistente registrado por su DNI. Retorna None si no existe.
    """
    try:
        return Asistente.objects.get(dni=dni)
    except Asistente.DoesNotExist:
        return None

def get_inscripcion_for_edition(asistente: Asistente, edicion: Edicion) -> Optional[Inscripcion]:
    """
    Busca y retorna la inscripción de un asistente para una edición dada o None.
    """
    return asistente.inscripciones.filter(edicion=edicion).first()

def resolve_qr_screen_data(asistente: Asistente) -> Tuple[str, str, str]:
    """
    Determina de manera limpia el tipo de pantalla, subtítulo y nombre de entidad vinculada
    para los diferentes casos de acreditación en el escaneo QR.
    Retorna una tupla (pantalla, subtitulo, nombre_vinculado).
    """
    perfil = asistente.profile_type
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

    return pantalla, subtitulo, nombre_vinculado
