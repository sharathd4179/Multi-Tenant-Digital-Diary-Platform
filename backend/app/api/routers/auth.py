"""
Authentication and user management endpoints.
"""
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.tenant import Tenant
from ...models.user import User
from ...schemas.user import UserCreate, UserRead, Token
from ...schemas.auth import LoginRequest
from ...core.security import (create_token, get_password_hash, verify_password)
from ...core.config import settings

router = APIRouter()


def create_access_and_refresh_tokens(data: Dict[str, Any]) -> Token:
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    access_token = create_token(data, expires_delta=access_token_expires)
    refresh_token = create_token(data, expires_delta=refresh_token_expires)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register-tenant", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_tenant(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Register a new tenant and create an admin user.

    The request must include `tenant_id` with a new UUID.  In practice the client
    should generate the tenant ID.  The first user created for a tenant is
    automatically assigned the admin role.
    """
    # Check that tenant does not already exist
    existing_tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if existing_tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant already exists")
    # Create tenant
    tenant = Tenant(id=user.tenant_id, name=f"Tenant-{user.tenant_id}")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    # Create admin user
    admin_user = User(
        tenant_id=tenant.id,
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role="admin",
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return UserRead.model_validate(admin_user)


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Register a new user under an existing tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    db_user = User(
        tenant_id=user.tenant_id,
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserRead.model_validate(db_user)


@router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and return JWT tokens.

    The client must send `username`, `password` and `tenant_id` in the request
    body.  We do not use OAuth2PasswordRequestForm here to simplify multi‑tenant
    support.
    """
    user = db.query(User).filter(
        User.username == form_data.username,
        User.tenant_id == form_data.tenant_id,
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token_data = {"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    return create_access_and_refresh_tokens(token_data)