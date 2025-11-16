"""
SQLAlchemy model for tasks extracted from notes.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


from enum import Enum


class TaskStatus(str, Enum):
    open = "open"
    completed = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(512), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(16), nullable=False, default=TaskStatus.open.value)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")
    note = relationship("Note", back_populates="tasks")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task id={self.id} status={self.status} description={self.description[:20]}>"