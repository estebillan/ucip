"""
FastAPI dependencies for the Universal Consultant Intelligence Platform.

Provides database sessions, authentication, rate limiting,
and other shared dependencies with proper cleanup.
"""

import logging
import time
from typing import AsyncGenerator, Optional

import redis.asyncio as aioredis
import structlog
from fastapi import Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_session

logger = structlog.get_logger(__name__)

# Redis client for caching and rate limiting
_redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Get Redis client with connection pooling."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
        )
    
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connections."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# Database session dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper cleanup."""
    async with get_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Rate limiting dependency
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)


def get_rate_limiter() -> Limiter:
    """Get rate limiter instance."""
    return limiter


# Authentication dependencies
async def get_current_user(request: Request) -> dict:
    """Get current authenticated user (placeholder for now)."""
    # TODO: Implement proper authentication
    # For now, return a mock user
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not api_key.startswith(settings.api_key_prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )
    
    # Mock user data - replace with actual authentication
    return {
        "id": 1,
        "email": "user@example.com",
        "is_active": True,
        "api_key": api_key,
    }


async def get_optional_user(request: Request) -> Optional[dict]:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


# Caching dependencies
class CacheManager:
    """Cache manager for Redis operations."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            value = await self.redis.get(f"{settings.redis_prefix}{key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            result = await self.redis.set(
                f"{settings.redis_prefix}{key}",
                value,
                ex=expire or settings.redis_cache_timeout
            )
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = await self.redis.delete(f"{settings.redis_prefix}{key}")
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            result = await self.redis.exists(f"{settings.redis_prefix}{key}")
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache exists error: {e}")
            return False


async def get_cache_manager(
    redis_client: aioredis.Redis = Depends(get_redis_client)
) -> CacheManager:
    """Get cache manager instance."""
    return CacheManager(redis_client)


# Pagination dependencies
class PaginationParams:
    """Pagination parameters with validation."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1"
            )
        
        if per_page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Per page must be >= 1"
            )
        
        if per_page > max_per_page:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Per page must be <= {max_per_page}"
            )
        
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page
        self.limit = per_page
    
    def get_pagination_metadata(self, total_items: int) -> dict:
        """Get pagination metadata for responses."""
        total_pages = (total_items + self.per_page - 1) // self.per_page
        
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": total_items,
            "total_pages": total_pages,
            "has_next": self.page < total_pages,
            "has_prev": self.page > 1,
        }


def get_pagination_params(
    page: int = 1,
    per_page: int = 20
) -> PaginationParams:
    """Get pagination parameters with validation."""
    return PaginationParams(page=page, per_page=per_page)


# Search and filtering dependencies
class SearchParams:
    """Search parameters with validation."""
    
    def __init__(
        self,
        q: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        filters: Optional[dict] = None
    ):
        self.query = q.strip() if q else None
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "desc"
        self.filters = filters or {}
    
    def has_search(self) -> bool:
        """Check if search query is provided."""
        return bool(self.query and len(self.query) >= 2)
    
    def has_filters(self) -> bool:
        """Check if filters are provided."""
        return bool(self.filters)


def get_search_params(
    q: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> SearchParams:
    """Get search parameters with validation."""
    return SearchParams(q=q, sort_by=sort_by, sort_order=sort_order)


# Request validation dependencies
async def validate_content_type(request: Request) -> None:
    """Validate request content type for POST/PUT requests."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Content-Type must be application/json"
            )


# Background task dependencies
class BackgroundTaskManager:
    """Manager for background tasks and job queuing."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def queue_task(
        self,
        task_name: str,
        task_data: dict,
        priority: int = 1,
        delay: Optional[int] = None
    ) -> str:
        """Queue a background task for processing."""
        import json
        import uuid
        
        task_id = str(uuid.uuid4())
        task_payload = {
            "id": task_id,
            "name": task_name,
            "data": task_data,
            "priority": priority,
            "created_at": int(time.time()),
            "delay": delay,
        }
        
        try:
            # Add to task queue
            queue_key = f"{settings.redis_prefix}tasks:queue"
            await self.redis.lpush(queue_key, json.dumps(task_payload))
            
            # Track task status
            status_key = f"{settings.redis_prefix}tasks:status:{task_id}"
            await self.redis.hset(status_key, mapping={
                "status": "queued",
                "created_at": task_payload["created_at"],
                "data": json.dumps(task_data),
            })
            await self.redis.expire(status_key, 86400)  # 24 hours
            
            return task_id
        except Exception as e:
            logger.error(f"Failed to queue task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to queue background task"
            )
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get status of a background task."""
        try:
            status_key = f"{settings.redis_prefix}tasks:status:{task_id}"
            status_data = await self.redis.hgetall(status_key)
            
            if not status_data:
                return None
            
            return {
                "id": task_id,
                "status": status_data.get("status"),
                "created_at": int(status_data.get("created_at", 0)),
                "updated_at": int(status_data.get("updated_at", 0)),
                "progress": int(status_data.get("progress", 0)),
                "result": status_data.get("result"),
                "error": status_data.get("error"),
            }
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return None


async def get_background_task_manager(
    redis_client: aioredis.Redis = Depends(get_redis_client)
) -> BackgroundTaskManager:
    """Get background task manager instance."""
    return BackgroundTaskManager(redis_client)