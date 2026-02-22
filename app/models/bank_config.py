from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class CompanyBankConfig(Base):
    __tablename__ = "company_bank_configs"

    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bank_name = Column(String, nullable=False)
    # Link to company
    company_id = Column(
        String,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Bank configuration JSON
    bank_config = Column(JSONB, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )