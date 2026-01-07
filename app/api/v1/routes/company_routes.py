from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.companyService import CompanyManager

router = APIRouter(prefix="/api/v1/company", tags=["Company APIs"])

@router.post("/verification/{company_id}", summary="Verify company credentials")
async def verification(company_id: str, db: AsyncSession = Depends(get_db)):
    manager = CompanyManager(db)
    company = await manager.get_company_details_by_company_id(company_id)

    if not company:
        raise HTTPException(status_code=400, detail="Credentials do not match")

    return {"company": company}