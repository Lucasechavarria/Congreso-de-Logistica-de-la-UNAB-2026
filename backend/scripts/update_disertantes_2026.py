import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from api.models import Disertante, Edicion

edicion_2026, _ = Edicion.objects.get_or_create(anio=2026, defaults={'nombre': 'Congreso de Logística 2026', 'activa': True})
if not edicion_2026.activa:
    Edicion.objects.filter(activa=True).update(activa=False)
    edicion_2026.activa = True
    edicion_2026.save()

disertantes_data = [
    {
        "nombre": "Aldo José Tombión",
        "empresa": "LCM",
        "tema": "Herramientas para la transformación digital de una operación logística",
        "linkedin": "https://www.linkedin.com/in/aldo-tombion-lcm-logistic-co-56001b13/"
    },
    {
        "nombre": "Arnaldo Martín Ventancu",
        "empresa": "UCASAL",
        "tema": "Del Salar a la Batería: Logística e Integración de Cadenas de Valor en la Minería del Litio en el Norte Argentino",
        "linkedin": "https://www.linkedin.com/in/arnaldo-martin-ventancu-163239176/"
    },
    {
        "nombre": "Diego Baglietto",
        "empresa": "DIBAG SCM",
        "tema": "Cómo usar la IA para desarrollar la estrategia de tu negocio",
        "linkedin": "https://www.linkedin.com/company/dibag-supply-chain-management/?viewAsMember=true"
    },
    {
        "nombre": "Fabio Contino",
        "empresa": "Austral",
        "tema": "El Paradigma de la Innovación en logística",
        "linkedin": "https://www.linkedin.com/in/fabiocontino/"
    },
    {
        "nombre": "Fernando Nahuel Méndez",
        "empresa": "",
        "tema": "La Logística Invisible en el Eje \"Una Salud\": Resiliencia Institucional, Analítica de Datos y Salud Ocupacional en la Gestión Pública.",
        "linkedin": "https://www.linkedin.com/in/fernando-nahuel-mendez-a15600367/"
    },
    {
        "nombre": "Guido Barrionuevo",
        "empresa": "EasyDocking",
        "tema": "Cómo automatizar el ingreso de camiones a planta",
        "linkedin": "https://www.linkedin.com/in/guidobarrionuevo"
    },
    {
        "nombre": "Ignacio Albinati",
        "empresa": "Shipro",
        "tema": "La logística no se transforma con tecnología: se transforma con criterio",
        "linkedin": "https://www.linkedin.com/in/ignacio-albinati/"
    },
    {
        "nombre": "Juan Manuel Telechea",
        "empresa": "T+1",
        "tema": "La economía de Milei y su impacto en la logística.",
        "linkedin": ""
    },
    {
        "nombre": "Julieta Toffani",
        "empresa": "La Postal",
        "tema": "Formar para innovar: cómo las empresas preparan talento para el futuro",
        "linkedin": "https://www.linkedin.com/in/julieta-toffani-b2602327"
    },
    {
        "nombre": "Marcelo Pagano",
        "empresa": "CARMOVE",
        "tema": "Vehículos Eléctricos y los cambios que se requieren en Parques Industriales",
        "linkedin": "https://www.carmove.ar"
    },
    {
        "nombre": "Maximiliano Martinelli",
        "empresa": "United Airlines",
        "tema": "“Lo que no vemos cuando miramos un avión” Logística aérea, Air Cargo y Supply Chain",
        "linkedin": ""
    },
    {
        "nombre": "Pablo González",
        "empresa": "Logística del ALTO",
        "tema": "Data Driven Logistics: De los datos a decisiones que transforman el negocio.",
        "linkedin": "https://logisticadelalto.com"
    },
    {
        "nombre": "Rodolfo Pérez",
        "empresa": "ISFT N° 234",
        "tema": "El rol estratégico del Warehouse en operaciones críticas",
        "linkedin": "https://www.linkedin.com/in/rodolfoluisperez"
    },
    {
        "nombre": "Sebastián Carrizo",
        "empresa": "Municipio de Lanús",
        "tema": "Corredor intermodal Hidroferroporruario",
        "linkedin": ""
    },
    {
        "nombre": "Sebastián San Martín",
        "empresa": "Edenor - ISFT N° 234",
        "tema": "Operaciones críticas: el rol estratégico del warehouse en la continuidad de servicios esenciales",
        "linkedin": "https://www.linkedin.com/in/sebastian-sanmartin94/"
    },
    {
        "nombre": "Vanina Pugliese",
        "empresa": "ANDREANI GRUPO LOGÍSTICO",
        "tema": "Mucho más que logística: Crear valor para los negocios a través de la tecnología y el talento de las personas.",
        "linkedin": "https://linkedin.com/in/vanina-pugliese"
    },
    {
        "nombre": "Yanina Frizzotti",
        "empresa": "Universidad Nacional de Quilmes",
        "tema": "Transportes y agentes en el comercio exterior.",
        "linkedin": "https://www.linkedin.com/in/yanina-frizzotti-b065521a4/"
    }
]

# Update or replace edicion 2026 disertantes
Disertante.objects.filter(edicion=edicion_2026).delete()

for d in disertantes_data:
    Disertante.objects.create(
        edicion=edicion_2026,
        nombre=d["nombre"],
        empresa_institucion=d["empresa"],
        tema_presentacion=d["tema"],
        linkedin=d["linkedin"] if d["linkedin"] != "-" else "",
        estado="APROBADO"
    )

print(f"EXITO: {len(disertantes_data)} disertantes oficiales 2026 cargados correctamente.")
