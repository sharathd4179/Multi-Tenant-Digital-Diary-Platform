"""
SQLAlchemy model for tenants.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tenant id={self.id} name={self.name}>"