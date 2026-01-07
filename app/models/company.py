from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base
from sqlalchemy import Column, String, DateTime, Boolean,ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.sql import func

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact_number = Column(String)
    auth_token =  Column(String)
    twilio_sid = Column(String)
    twilio_token = Column(String)
    joining_tag = Column(String)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    category_id = Column(String, ForeignKey("categories.id"))