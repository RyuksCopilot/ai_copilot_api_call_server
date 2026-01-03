from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, List


class HistoryBulkCreate(BaseModel):
    company_id: UUID
    title: str
    description: Dict
    status: str


class HistoryBulkRequest(BaseModel):
    items: List[HistoryBulkCreate]


class HistoryCreate(BaseModel):
    company_id: UUID
    title: str
    description: dict | None = None
    status: str


class HistoryResponse(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: dict | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
