"""
FastAPI application entry point.

This module initialises the FastAPI app, configures middleware, includes API
routers and ensures that database tables exist on startup.  It also exposes
automatic OpenAPI documentation at `/docs`.
"""
import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .models.base import Base
from .core.database import engine
from .api.routers import auth as auth_router
from .api.routers import notes as notes_router
from .api.routers import search as search_router
from .api.routers import tasks as tasks_router
from .api.routers import health as health_router

# Configure root logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure structured logging with appropriate format for environment."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Use JSON format in production, readable format in development
    if settings.is_production:
        import json
        from datetime import datetime
        
        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logging.basicConfig(level=log_level, handlers=[handler])
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    logger.info(f"Logging configured - Level: {settings.log_level}, Environment: {settings.environment}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Setup logging
    setup_logging()
    
    app = FastAPI(
        title="Multi‑Tenant Diary Assistant",
        version="0.1.0",
        description="A multi‑tenant digital diary platform with RAG‑powered knowledge assistant",
    )
    
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["1000/hour"],
        storage_uri=settings.redis_url if settings.redis_url else "memory://",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS configuration
    # In production, restrict origins to specific domains
    allowed_origins = ["*"] if settings.is_development else [
        "http://localhost:8501",
        "https://yourdomain.com",  # Update with actual domain
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request/Response logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> Response:
        """Log all HTTP requests and responses."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} - "
                f"Exception: {str(e)} - "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(e) if settings.is_development else "An error occurred"}
            )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions globally."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc) if settings.is_development else "An unexpected error occurred"
            }
        )

    # Include routers
    app.include_router(health_router.router, prefix="/health", tags=["health"])
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(notes_router.router, prefix="/notes", tags=["notes"])
    app.include_router(search_router.router, prefix="/search", tags=["search"])
    app.include_router(tasks_router.router, prefix="/tasks", tags=["tasks"])

    @app.on_event("startup")
    def on_startup() -> None:
        """Create database tables on startup and validate configuration."""
        logger.info("Starting up application...")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Log level: {settings.log_level}")
        
        # Validate critical settings
        if not settings.database_url:
            logger.error("DATABASE_URL is not configured!")
            raise ValueError("DATABASE_URL is required")
        
        if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
            logger.warning("JWT_SECRET_KEY is too short or missing. Using default (NOT SECURE FOR PRODUCTION)")
        
        if settings.is_production and not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured - RAG features will be limited")
        
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}", exc_info=True)
            raise
        
        logger.info("Application startup complete")

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        """Cleanup on shutdown."""
        logger.info("Shutting down application...")

    return app


app = create_app()