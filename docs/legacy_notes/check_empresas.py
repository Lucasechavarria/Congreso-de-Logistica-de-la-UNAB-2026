#!/usr/bin/env python3
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Empresa

print("=== EMPRESAS EN BASE DE DATOS ===")
empresas = Empresa.objects.all()
print(f"Total de empresas: {empresas.count()}")
print("\nÚltimas 10 empresas:")
for i, empresa in enumerate(empresas.order_by('-id')[:10], 1):
    print(f"{i}. {empresa.nombre_empresa} - {empresa.email_contacto}")
    print(f"   Participación: {empresa.participacion_opciones}")
    print(f"   Fecha: {getattr(empresa, 'fecha_registro', 'No disponible')}")
    print()
