from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ReportCreate(BaseModel):
    image_url: Optional[str] = None
    category: str = Field(..., example='Basura y Limpieza')
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = 'pendiente'


class Report(ReportCreate):
    id: UUID
    status: str
    created_at: datetime
