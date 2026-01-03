from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.database import get_db
from app.services.historyService import HistoryService
from app.schemas.history import HistoryCreate, HistoryResponse,HistoryBulkRequest

router = APIRouter(prefix="/api/v1/history", tags=["History"])


@router.post("/", response_model=HistoryResponse)
async def create_history(
    payload: HistoryCreate,
    db: AsyncSession = Depends(get_db)
):
    service = HistoryService(db)
    return await service.create_history(payload)


@router.get("/{company_id}", response_model=list[HistoryResponse])
async def get_history_by_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = HistoryService(db)
    return await service.get_history_by_company(company_id)

@router.post("/bulk")
async def create_history_bulk(
    payload: HistoryBulkRequest,
    db: AsyncSession = Depends(get_db),
):
    return await HistoryService.bulk_create_history(
        db=db,
        items=payload.items,
    )