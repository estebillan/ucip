"""
Database configuration and session management for the Universal Consultant Intelligence Platform.

Provides async SQLAlchemy session management with connection pooling,
health checks, and proper cleanup patterns.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool
from sqlmodel import SQLModel

from backend.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager with connection pooling and health checks."""
    
    def __init__(self) -> None:
        """Initialize database manager with async engine."""
        # Configure connection pool based on environment
        poolclass = QueuePool if settings.environment == "production" else NullPool
        
        self.engine = create_async_engine(
            settings.database_url,
            poolclass=poolclass,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=True,  # Validate connections before use
            echo=settings.debug,  # Log SQL queries in debug mode
            echo_pool=settings.debug,  # Log pool events in debug mode
        )
        
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.async_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close database connections."""
        try:
            await self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with proper cleanup."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with db_manager.get_session() as session:
        yield session


async def init_database() -> None:
    """Initialize database tables."""
    await db_manager.create_tables()


async def close_database() -> None:
    """Close database connections."""
    await db_manager.close()


async def database_health_check() -> bool:
    """Check database health."""
    return await db_manager.health_check()