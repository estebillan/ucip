"""
Main FastAPI application for the Universal Consultant Intelligence Platform.

Production-ready application with comprehensive middleware stack,
error handling, and lifespan management.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api.dependencies import get_redis_client
from backend.api.routes import campaigns, consultants, prospects, reports, research
from backend.core.config import settings
from backend.core.database import close_database, database_health_check, init_database
from backend.core.logging import setup_logging
from backend.core.monitoring import health_check_endpoint, metrics_endpoint
from backend.utils.exceptions import (
    ConsultantPlatformException,
    consultant_platform_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

# Initialize structured logging
logger = structlog.get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Setup logging
    setup_logging()
    logger.info("Starting Universal Consultant Intelligence Platform")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Perform health checks
        db_healthy = await database_health_check()
        if not db_healthy:
            logger.error("Database health check failed")
            raise RuntimeError("Database is not healthy")
        
        logger.info("Application startup complete")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down application")
        await close_database()
        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Universal Consultant Intelligence Platform",
        description="AI-powered prospect research and intelligence platform for consultants",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Add routes
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Request-ID"],
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Request correlation ID middleware
    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next):
        """Add correlation ID to requests for tracing."""
        import uuid
        
        correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Add to structured logging context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log HTTP requests and responses."""
        import time
        
        start_time = time.time()
        
        # Log request
        logger.info(
            "HTTP request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "HTTP request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure application exception handlers."""
    
    app.add_exception_handler(
        ConsultantPlatformException,
        consultant_platform_exception_handler
    )
    
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )
    
    app.add_exception_handler(
        Exception,
        http_exception_handler
    )


def setup_routes(app: FastAPI) -> None:
    """Configure application routes."""
    
    # Health check and monitoring
    app.get("/health", tags=["Health"])(health_check_endpoint)
    app.get("/metrics", tags=["Monitoring"])(metrics_endpoint)
    
    # API routes
    app.include_router(
        consultants.router,
        prefix="/api/v1/consultants",
        tags=["Consultants"]
    )
    
    app.include_router(
        prospects.router,
        prefix="/api/v1/prospects",
        tags=["Prospects"]
    )
    
    app.include_router(
        research.router,
        prefix="/api/v1/research",
        tags=["Research"]
    )
    
    app.include_router(
        reports.router,
        prefix="/api/v1/reports",
        tags=["Reports"]
    )
    
    app.include_router(
        campaigns.router,
        prefix="/api/v1/campaigns",
        tags=["Campaigns"]
    )
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Universal Consultant Intelligence Platform",
            "version": settings.app_version,
            "status": "operational",
            "docs": "/docs" if settings.debug else None,
        }


# Create application instance
app = create_app()