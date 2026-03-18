from django.core.files.storage import Storage
from supabase import create_client, Client
from django.conf import settings
from django.utils.deconstruct import deconstructible
import os
import io

@deconstructible
class SupabaseStorage(Storage):
    def __init__(self, bucket_name=None, location=None, **kwargs):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_KEY
        self.bucket_name = bucket_name or getattr(settings, 'SUPABASE_PUBLIC_BUCKET', 'congreso-public')
        self.location = (location or "").rstrip('/')
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def _get_supabase_path(self, name):
        path = os.path.join(self.location, name).replace("\\", "/")
        # Eliminar barras iniciales si existen
        return path.lstrip('/')

    def _open(self, name, mode='rb'):
        path = self._get_supabase_path(name)
        try:
            response = self.client.storage.from_(self.bucket_name).download(path)
            return io.BytesIO(response)
        except Exception as e:
            print(f"[ERROR] No se pudo abrir el archivo {path} en Supabase: {e}")
            return None

    def _save(self, name, content):
        path = self._get_supabase_path(name)
        file_data = content.read()
        
        try:
            # En v2.x el método upload espera path y file
            self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=file_data,
                file_options={"upsert": "true"}
            )
        except Exception as e:
            print(f"[ERROR] No se pudo guardar el archivo {path} en Supabase: {e}")
            # Si falla porque ya existe y upsert falló por algo, intentamos update
            try:
                self.client.storage.from_(self.bucket_name).update(
                    path=path,
                    file=file_data
                )
            except Exception as e2:
                print(f"[ERROR] Error fatal al subir archivo: {e2}")
        
        return name

    def exists(self, name):
        # Por simplicidad para el registro de Django, retornamos False 
        # para que siempre intente subir (con upsert=true en _save)
        return False

    def url(self, name):
        path = self._get_supabase_path(name)
        # Si el bucket tiene 'private' en el nombre, generamos una URL firmada
        if "private" in self.bucket_name.lower():
            try:
                # URL válida por 1 hora para visualización inmediata
                res = self.client.storage.from_(self.bucket_name).create_signed_url(path, expires_in=3600)
                return res.get('signedURL') or res # Depende de la versión exacta de supabase-py
            except:
                return f"/{self.bucket_name}/{path}" # Fallback
        
        return self.client.storage.from_(self.bucket_name).get_public_url(path)

    def size(self, name):
        return 0 # Placeholder

    def delete(self, name):
        path = self._get_supabase_path(name)
        try:
            self.client.storage.from_(self.bucket_name).remove([path])
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar el archivo {path} en Supabase: {e}")
