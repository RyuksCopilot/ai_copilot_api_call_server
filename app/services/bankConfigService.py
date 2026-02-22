import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.future import select

from app.models.bank_config import CompanyBankConfig


class CompanyBankConfigManager:
    def __init__(self, session: AsyncSession):
        """
        Initialize the CompanyBankConfigManager with a database session.

        Args:
            session (AsyncSession): Async SQLAlchemy session for DB operations.
        """
        self.session = session
        
    async def create_bank_config(
        self,
        company_id: str,
        bank_name: str,
        bank_config: dict
    ):
        """
        Create new bank configuration entry.
        """

        try:
            # Optional: check if already exists
            result = await self.session.execute(
                select(CompanyBankConfig).where(
                    CompanyBankConfig.company_id == company_id,
                    CompanyBankConfig.bank_name == bank_name
                )
            )

            existing = result.scalar_one_or_none()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Bank config already exists for this company and bank."
                )

            new_config = CompanyBankConfig(
                id=str(uuid.uuid4()),
                company_id=company_id,
                bank_name=bank_name,
                bank_config=bank_config
            )

            self.session.add(new_config)

            await self.session.commit()
            await self.session.refresh(new_config)

            return new_config

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create bank config: {str(e)}"
            )


    async def get_bank_config_by_company_and_bank(
        self,
        company_id: str,
        bank_name: str
    ):
        """
        Retrieve bank config JSON using company_id and bank_name.

        Args:
            company_id (str): Company UUID
            bank_name (str): Name of bank

        Returns:
            dict: bank_config JSON
        """

        try:
            result = await self.session.execute(
                select(CompanyBankConfig).where(
                    CompanyBankConfig.company_id == company_id,
                    CompanyBankConfig.bank_name == bank_name
                )
            )

            bank_config = result.scalar_one_or_none()

            if not bank_config:
                raise HTTPException(
                    status_code=404,
                    detail="Bank config not found for this company."
                )

            return bank_config.bank_config

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve bank config: {str(e)}"
            )