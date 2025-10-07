import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List

load_dotenv()

from app.schemas import ReportCreate, Report
from app.supabase_client import upload_file_to_storage, get_public_url
from app.db import get_reports, get_report_by_id, insert_report_db
from app.supabase_client import remove_file_from_storage, extract_path_from_public_url
from app.db import update_report_db, delete_report_db

app = FastAPI(
    title="Reports API MINGAFIX",
    version="0.1",
    description="""
API para la gestión de reportes.

**Creador:** Miguel Carapaz  
""",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/reports', response_model=Report, status_code=201)
async def create_report(
    file: UploadFile | None = File(None),
    category: str = Form(...),
    longitude: float | None = Form(None),
    latitude: float | None = Form(None),
    description: str | None = Form(None),
    status: str = Form('pendiente'),
):
    """Crea un reporte. El campo de imagen ahora se envía como `file` (multipart/form-data). Si se envía
    `file`, el servidor lo sube a Storage y guarda la URL resultante en `image_url`.
    """
    public_url = None
    try:
        if file is not None:
            content = await file.read()
            from uuid import uuid4
            import os

            ext = os.path.splitext(file.filename)[1]
            remote_path = f"images/{uuid4()}{ext}"
            # subir al storage al bucket fijo 'reports-images'
            upload_res = upload_file_to_storage('reports-images', remote_path, content, content_type=file.content_type)
            public_url = get_public_url('reports-images', remote_path)

        payload = {
            'image_url': public_url,
            'category': category,
            'longitude': longitude,
            'latitude': latitude,
            'description': description,
            'status': status
        }
        item = await insert_report_db(payload)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/reports', response_model=List[Report])
async def list_reports():
    """Trae todos los reportes de la base de datos`.
    """
    try:
        items = await get_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return items


@app.get('/reports/{report_id}', response_model=Report)
async def get_report(report_id: str):
    """Busca un reporte en especifico de la base de datos por el id del reporte`.
    """
    item = await get_report_by_id(report_id)
    if not item:
        raise HTTPException(status_code=404, detail='Reporte no encontrado')
    return item

@app.delete('/reports/{report_id}', status_code=204)
async def delete_report(report_id: str):
    # obtener registro para conocer image_url
    item = await get_report_by_id(report_id)
    if not item:
        raise HTTPException(status_code=404, detail='Reporte no encontrado')

    # si tiene image_url intentar borrarla del storage
    image_url = item.get('image_url')
    if image_url:
        path = extract_path_from_public_url(image_url, 'reports-images')
        if path:
            try:
                remove_file_from_storage('reports-images', path)
            except Exception:
                # no bloqueamos el borrado del registro aunque falle la eliminación en storage
                pass

    deleted = await delete_report_db(report_id)
    if not deleted:
        raise HTTPException(status_code=500, detail='No se pudo eliminar el reporte')
    return None


@app.post('/reports/upload', response_model=Report, status_code=201)
async def upload_report(
    report_id: str | None = Form(None),
    file: UploadFile = File(...),
    category: str = Form(...),
    longitude: float | None = Form(None),
    latitude: float | None = Form(None),
    description: str | None = Form(None),
    status: str = Form('pendiente'),
):
    """Actualiza un registro en la tabla reports.
    Si se envía `report_id` (Form), se intentará reemplazar la imagen del reporte existente y
    actualizar sus campos; si no existe `report_id`, se crea un nuevo registro.
    """
    try:
        content = await file.read()
        # generar un nombre único
        from uuid import uuid4
        import os

        ext = os.path.splitext(file.filename)[1]
        remote_path = f"images/{uuid4()}{ext}"
        upload_res = upload_file_to_storage('reports-images', remote_path, content, content_type=file.content_type)

        # obtener url pública (si el bucket es público)
        public_url = get_public_url('reports-images', remote_path)

        payload = {
            'image_url': public_url,
            'category': category,
            'longitude': longitude,
            'latitude': latitude,
            'description': description,
            'status': status
        }

        if report_id:
            # actualizar registro existente: borrar imagen anterior (si existe) y actualizar fila
            existing = await get_report_by_id(report_id)
            if not existing:
                raise HTTPException(status_code=404, detail='Reporte especificado no existe')

            old_url = existing.get('image_url')
            if old_url:
                old_path = extract_path_from_public_url(old_url, 'reports-images')
                if old_path:
                    try:
                        remove_file_from_storage('reports-images', old_path)
                    except Exception:
                        # ignorar errores de storage para no bloquear la operación
                        pass

            updated = await update_report_db(report_id, payload)
            if not updated:
                raise HTTPException(status_code=500, detail='No se pudo actualizar el reporte')
            return updated

        item = await insert_report_db(payload)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
