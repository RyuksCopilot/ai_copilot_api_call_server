from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from app.models.history import History
from app.schemas.history import HistoryCreate,HistoryBulkCreate


class HistoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_create_history(
        db: AsyncSession,
        items: List[HistoryBulkCreate],
    ):
        histories = [
            History(
                company_id=item.company_id,
                title=item.title,
                description=item.description,
                status=item.status,
            )
            for item in items
        ]

        db.add_all(histories)
        await db.commit()

        return {"inserted_count": len(histories)}
    
    async def create_history(self, data: HistoryCreate) -> History:
        history = History(
            company_id=data.company_id,
            title=data.title,
            description=data.description,
            status=data.status,
        )

        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_history_by_company(self, company_id: UUID):
        stmt = select(History).where(History.company_id == company_id).order_by(
            History.created_at.desc()
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
