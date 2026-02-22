from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.bankConfigService import CompanyBankConfigManager

router = APIRouter(
    prefix="/api/v1/bank-config",
    tags=["Bank Config APIs"]
)


# Get bank config
@router.get(
    "/{company_id}",
    summary="Get bank configuration for a company"
)
async def get_bank_config(
    company_id: str,
    bank_name: str = Query(..., description="Name of the bank"),
    db: AsyncSession = Depends(get_db)
):
    manager = CompanyBankConfigManager(db)

    config = await manager.get_bank_config_by_company_and_bank(
        company_id=company_id,
        bank_name=bank_name
    )

    return config


# Create bank config
@router.post(
    "/create",
    summary="Create bank configuration"
)
async def create_bank_config(
    company_id: str,
    bank_name: str,
    bank_config: dict,
    db: AsyncSession = Depends(get_db)
):
    manager = CompanyBankConfigManager(db)

    new_config = await manager.create_bank_config(
        company_id=company_id,
        bank_name=bank_name,
        bank_config=bank_config
    )

    return {
        "message": "Bank config created successfully",
        "data": new_config
    }