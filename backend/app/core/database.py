"""Database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.core.config import settings


# Create async engine
def create_engine() -> AsyncEngine:
    """
    Create and configure the async database engine.

    Returns:
        AsyncEngine: Configured async SQLAlchemy engine
    """
    engine_kwargs = {
        "echo": settings.is_development,  # Log SQL in development
        "future": True,
    }

    # Use NullPool for testing/serverless, QueuePool for production
    if settings.is_production:
        engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
        engine_kwargs["pool_size"] = 20
        engine_kwargs["max_overflow"] = 10
        engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
        engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
    else:
        engine_kwargs["poolclass"] = NullPool

    return create_async_engine(
        settings.DATABASE_URL,
        **engine_kwargs
    )


# Create engine instance
engine = create_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy loading issues
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Provides a database session for the duration of a request,
    with automatic cleanup and rollback on errors.

    Yields:
        AsyncSession: Database session for the request

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """
    Close database connections.

    Should be called during application shutdown.
    """
    await engine.dispose()
