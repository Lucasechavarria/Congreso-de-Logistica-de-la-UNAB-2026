import os
import django
from django.http import JsonResponse
from django.db import connection

def debug_db_view(request):
    """Temporary view to check database encoding and schema on production."""
    try:
        data = {
            "status": "ok",
            "django_settings_module": os.environ.get('DJANGO_SETTINGS_MODULE'),
        }
        
        with connection.cursor() as cursor:
            # Check database encoding
            cursor.execute("SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database();")
            data["database_encoding"] = cursor.fetchone()[0]
            
            # Check client encoding
            cursor.execute("SHOW client_encoding;")
            data["client_encoding"] = cursor.fetchone()[0]
            
            # Check PostulacionDisertante column types
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'api_postulaciondisertante' 
                AND column_name IN ('ejes_tematicos', 'titulo_charla', 'resumen_charla');
            """)
            columns = cursor.fetchall()
            data["table_schema"] = {col[0]: col[1] for col in columns}
            
            # Test a query with non-ascii characters directly
            try:
                cursor.execute("SELECT 'Gestión' as test;")
                data["test_query_raw"] = cursor.fetchone()[0]
            except Exception as e:
                data["test_query_error"] = str(e)

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
