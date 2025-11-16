"""
Pydantic schemas for notes.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NoteCreate(NoteBase):
    tenant_id: UUID
    user_id: UUID


class NoteUpdate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
