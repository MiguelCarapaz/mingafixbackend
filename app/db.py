import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import List, Dict, Any, Optional

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    # convertir a asyncpg dialect
    ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

engine = create_async_engine(ASYNC_DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_reports() -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT * FROM reports ORDER BY created_at DESC'))
        rows = result.fetchall()
        return [dict(r._mapping) for r in rows]

async def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT * FROM reports WHERE id = :id'), {'id': report_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None

async def insert_report_db(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(
            """
            INSERT INTO reports (image_url, category, longitude, latitude, description, status)
            VALUES (:image_url, :category, :longitude, :latitude, :description, :status)
            RETURNING *
            """
        ), {
            'image_url': payload.get('image_url'),
            'category': payload.get('category'),
            'longitude': payload.get('longitude'),
            'latitude': payload.get('latitude'),
            'description': payload.get('description'),
            'status': payload.get('status', 'pendiente')
        })
        await session.commit()
        row = result.fetchone()
        return dict(row._mapping)


async def update_report_db(report_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        # construir dinámicamente los campos a actualizar
        set_clauses = []
        params = {'id': report_id}
        for k, v in payload.items():
            set_clauses.append(f"{k} = :{k}")
            params[k] = v
        if not set_clauses:
            return await get_report_by_id(report_id)
        sql = text(f"UPDATE reports SET {', '.join(set_clauses)} WHERE id = :id RETURNING *")
        result = await session.execute(sql, params)
        await session.commit()
        row = result.fetchone()
        return dict(row._mapping) if row else None


async def delete_report_db(report_id: str) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('DELETE FROM reports WHERE id = :id RETURNING id'), {'id': report_id})
        await session.commit()
        row = result.fetchone()
        return bool(row)
