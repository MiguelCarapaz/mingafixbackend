Proyecto FastAPI que conecta con Supabase para almacenar y consultar reportes de incidencias.

Archivos principales:
- `supabase_init.sql` : Script SQL para crear tipos ENUM y la tabla `reports` en Supabase.
- `app/main.py` : API FastAPI con endpoints para crear y leer reportes.
- `app/supabase_client.py` : Cliente ligero para interactuar con Supabase (REST via supabase-py).

Instrucciones rápidas:
1. Crea el proyecto en Supabase y ejecuta `supabase_init.sql` en SQL Editor.
2. Llena `.env` con `SUPABASE_URL` y `SUPABASE_KEY` (service_role o anon según permisos).
3. Instala dependencias: `pip install -r requirements.txt`.
4. Ejecuta la API (opciones):

- Usando el módulo `fastapi` (recomendado si estás usando la CLI de FastAPI):

	```powershell
	python -m fastapi app.main --reload --port 8000
	```

- O usando `uvicorn` directamente si lo prefieres:

	```powershell
	python -m uvicorn app.main:app --reload --port 8000
	```

5. Abre Swagger en `http://localhost:8000/docs`.

Nota: dependiendo de la versión de FastAPI/uvicorn instalada, el primer comando puede requerir la CLI de `fastapi` disponible en `fastapi[all]`. La segunda opción usando `python -m uvicorn` funciona con cualquier instalación de `uvicorn`.

Storage y subida de imágenes:
- Este proyecto por defecto sube las imágenes "vanilla" al bucket (URL pública). No estamos generando signed URLs.
- Asegúrate de que el bucket (`reports-images`) sea público si quieres servir las imágenes directamente por la URL.
- Añade `SUPABASE_URL` y `SUPABASE_KEY` a tu `.env` antes de usar el endpoint `/reports/upload`.

