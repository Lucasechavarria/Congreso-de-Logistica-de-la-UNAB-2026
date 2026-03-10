#!/usr/bin/env python3
"""
Script de prueba para la carga masiva de asistentes
"""
import os
import sys
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/home/daro/Documentos/FolKode Group/proyectos/congreso/Congreso-UNAB/backend')
django.setup()

from api.models import Asistente

def crear_archivo_excel_prueba():
    """Crear un archivo Excel de prueba con la estructura esperada"""
    data = [
        {
            'NOMBRE': 'Juan Carlos',
            'Apellido': 'Pérez',
            'CORREO ELECTRONICO': 'juan.perez@example.com',
            'NUMERO DE CELULAR (con codigo de area)': '+54911123456789',
            'DNI': '12345678',
            'TIPO DE PERFIL': 'Visitante',
            'Columna1': 'Colaborador/a Estudiante'
        },
        {
            'NOMBRE': 'María Elena',
            'Apellido': 'González',
            'CORREO ELECTRONICO': 'maria.gonzalez@example.com',
            'NUMERO DE CELULAR (con codigo de area)': '+54911987654321',
            'DNI': '',  # DNI vacío para probar
            'TIPO DE PERFIL': '',  # Tipo de perfil vacío para probar
            'Columna1': 'Colaborador/a Docente'
        },
        {
            'NOMBRE': 'Roberto',
            'Apellido': 'Martínez',
            'CORREO ELECTRONICO': 'roberto.martinez@example.com',
            'NUMERO DE CELULAR (con codigo de area)': '+54911555666777',
            'DNI': '87654321',
            'TIPO DE PERFIL': 'Graduado',
            'Columna1': ''
        }
    ]
    
    df = pd.DataFrame(data)
    archivo = '/tmp/test_asistentes.xlsx'
    df.to_excel(archivo, index=False)
    return archivo

def probar_carga_masiva():
    """Probar la función de carga masiva"""
    print("🧪 Probando la carga masiva de asistentes...")
    
    # Crear archivo de prueba
    archivo = crear_archivo_excel_prueba()
    print(f"📁 Archivo de prueba creado: {archivo}")
    
    # Contar asistentes antes
    count_antes = Asistente.objects.count()
    print(f"📊 Asistentes antes de la carga: {count_antes}")
    
    # Importar la vista de carga masiva
    from api.views import cargar_asistentes_masivo
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.test import RequestFactory
    
    # Simular una request
    factory = RequestFactory()
    
    # Leer el archivo y crear un archivo mock
    with open(archivo, 'rb') as f:
        file_content = f.read()
    
    uploaded_file = SimpleUploadedFile(
        name='test_asistentes.xlsx',
        content=file_content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    request = factory.post('/api/cargar-asistentes/', {'archivo': uploaded_file})
    request.FILES['archivo'] = uploaded_file
    
    try:
        # Ejecutar la vista
        response = cargar_asistentes_masivo(request)
        print(f"✅ Respuesta del servidor: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"📝 Datos de respuesta: {response.data}")
        
        # Contar asistentes después
        count_despues = Asistente.objects.count()
        print(f"📊 Asistentes después de la carga: {count_despues}")
        print(f"➕ Asistentes agregados: {count_despues - count_antes}")
        
        # Mostrar los últimos asistentes creados
        ultimos_asistentes = Asistente.objects.order_by('-id')[:3]
        print("\n👥 Últimos asistentes creados:")
        for asistente in ultimos_asistentes:
            print(f"  - {asistente.first_name} {asistente.last_name}")
            print(f"    Email: {asistente.email}")
            print(f"    DNI: {asistente.dni or 'No proporcionado'}")
            print(f"    Tipo: {asistente.profile_type}")
            print(f"    Rol específico: {asistente.rol_especifico or 'No especificado'}")
            print()
            
    except Exception as e:
        print(f"❌ Error durante la carga: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Limpiar archivo de prueba
    if os.path.exists(archivo):
        os.remove(archivo)
        print(f"🗑️ Archivo de prueba eliminado")

if __name__ == "__main__":
    probar_carga_masiva()