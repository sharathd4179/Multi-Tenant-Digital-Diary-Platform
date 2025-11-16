"""
Authentication request and response schemas.
"""
from uuid import UUID

from pydantic import BaseModel

from .user import Token


class LoginRequest(BaseModel):
    tenant_id: UUID
    username: str
    password: str
