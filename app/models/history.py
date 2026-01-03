from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.sql import func

class History(Base):
    __tablename__ = "history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(JSONB, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())