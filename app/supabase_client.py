import os
from supabase import create_client
from typing import Optional, List, Dict, Any

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError('SUPABASE_URL y SUPABASE_KEY deben estar en variables de entorno')
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    res = client.table('reports').insert(payload).execute()
    return res.data

def fetch_reports() -> List[Dict[str, Any]]:
    client = get_client()
    res = client.table('reports').select('*').execute()
    return res.data

def fetch_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    res = client.table('reports').select('*').eq('id', report_id).execute()
    data = res.data
    return data[0] if data else None


def upload_file_to_storage(bucket: str, path: str, content: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Sube un archivo (bytes) al bucket y devuelve el resultado de la operación."""
    client = get_client()
    # supabase-py acepta bytes o file-like
    if content_type:
        res = client.storage.from_(bucket).upload(path, content, {'content-type': content_type})
    else:
        res = client.storage.from_(bucket).upload(path, content)
    return res


def get_public_url(bucket: str, path: str) -> str:
    client = get_client()
    res = client.storage.from_(bucket).get_public_url(path)
    # la respuesta puede variar entre versiones
    if isinstance(res, dict):
        return res.get('publicUrl') or res.get('public_url') or ''
    return res


def create_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    client = get_client()
    res = client.storage.from_(bucket).create_signed_url(path, expires_in)
    if isinstance(res, dict):
        return res.get('signedURL') or res.get('signed_url') or ''
    return res


def remove_file_from_storage(bucket: str, path: str) -> Dict[str, Any]:
    """Elimina un archivo del bucket. `path` es la ruta relativa dentro del bucket (ej. images/uuid.jpg)."""
    client = get_client()
    # supabase-py storage remove espera una lista de paths
    res = client.storage.from_(bucket).remove([path])
    return res


def extract_path_from_public_url(url: str, bucket_name: str) -> str | None:
    """Intenta extraer la ruta relativa del objeto dentro del bucket a partir de una URL pública.
    Busca la primera ocurrencia del bucket_name en la URL y devuelve lo que sigue.
    Ejemplo: https://.../storage/v1/object/public/reports-images/images/uuid.jpg -> images/uuid.jpg
    """
    if not url or not bucket_name:
        return None
    try:
        idx = url.find(bucket_name)
        if idx == -1:
            return None
        # path comienza después de 'bucket_name/'
        start = idx + len(bucket_name) + 1
        path = url[start:]
        # quitar query params
        if '?' in path:
            path = path.split('?', 1)[0]
        return path
    except Exception:
        return None
