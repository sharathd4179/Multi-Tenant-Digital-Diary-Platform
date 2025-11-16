"""
Health check and system status endpoints.
"""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.config import settings


router = APIRouter()


@router.get("/", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """Basic health check endpoint.
    
    Returns:
        Status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "multi-tenant-diary-assistant"
    }


@router.get("/ready", response_model=Dict[str, Any])
def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check - verifies database connectivity.
    
    Returns:
        Status with database connectivity information.
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check OpenAI API key (optional)
    openai_configured = bool(settings.openai_api_key)
    
    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "openai_configured": openai_configured,
        "service": "multi-tenant-diary-assistant"
    }


@router.get("/live", response_model=Dict[str, str])
def liveness_check() -> Dict[str, str]:
    """Liveness check - indicates the service is running.
    
    Returns:
        Simple status.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

