import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.future import select
from app.models.company import Company

class CompanyManager:
    def __init__(self, session: AsyncSession):
        """
        Initialize the CompanyManager with a database session.

        Args:
            session (AsyncSession): Async SQLAlchemy session for DB operations.
        """
        self.session = session
        
    async def get_company_details_by_company_id(self, company_id: str) -> str:
            """
            Retrieve the auth_token of a company by its ID.

            Args:
                company_id (str): UUID of the company.

            Returns:
                str: Auth token of the company.
            """
            try:
                result = await self.session.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = result.scalar_one_or_none()
                if not company:
                    raise HTTPException(status_code=404, detail="Company not found.")
                return company
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve auth token: {str(e)}")
        