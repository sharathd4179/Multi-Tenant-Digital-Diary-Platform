"""
Pydantic schemas for tasks extracted from notes.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ..models.task import TaskStatus


class TaskBase(BaseModel):
    description: str
    due_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.open

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    tenant_id: UUID
    user_id: UUID
    note_id: UUID


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    note_id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None
