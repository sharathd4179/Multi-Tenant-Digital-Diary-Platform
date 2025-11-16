"""
Pydantic schemas for users.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = Field(default="user", description="Role within the tenant (admin or user)")

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    tenant_id: UUID


class UserRead(UserBase):
    id: UUID
    tenant_id: UUID
    created_at: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
