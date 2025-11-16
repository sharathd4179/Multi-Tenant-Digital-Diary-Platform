"""
Rate limiting utilities using slowapi.
"""
from typing import Callable, Optional

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],
    storage_uri=settings.redis_url if settings.redis_url else "memory://",
)


def get_user_identifier(request) -> str:
    """Get identifier for rate limiting based on user.
    
    Uses user ID if available, otherwise falls back to IP address.
    """
    # Try to get current_user from request state (set by auth dependency)
    if hasattr(request.state, "current_user") and request.state.current_user:
        user = request.state.current_user
        return f"user:{user.id}"
    return get_remote_address(request)


def get_tenant_identifier(request) -> str:
    """Get identifier for rate limiting based on tenant.
    
    Uses tenant ID if available, otherwise falls back to IP address.
    """
    # Try to get current_user from request state (set by auth dependency)
    if hasattr(request.state, "current_user") and request.state.current_user:
        user = request.state.current_user
        return f"tenant:{user.tenant_id}"
    return get_remote_address(request)


# Rate limit decorators for different use cases
def rate_limit_per_user(limit: str = "100/hour") -> Callable:
    """Rate limit decorator that limits per user.
    
    Args:
        limit: Rate limit string (e.g., "100/hour", "10/minute").
    """
    def decorator(func):
        return limiter.limit(limit, key_func=get_user_identifier)(func)
    return decorator


def rate_limit_per_tenant(limit: str = "1000/hour") -> Callable:
    """Rate limit decorator that limits per tenant.
    
    Args:
        limit: Rate limit string (e.g., "1000/hour", "100/minute").
    """
    def decorator(func):
        return limiter.limit(limit, key_func=get_tenant_identifier)(func)
    return decorator


def rate_limit_per_ip(limit: str = "100/hour") -> Callable:
    """Rate limit decorator that limits per IP address.
    
    Args:
        limit: Rate limit string (e.g., "100/hour", "10/minute").
    """
    def decorator(func):
        return limiter.limit(limit, key_func=get_remote_address)(func)
    return decorator



