"""Database session management."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://dev:devpass@localhost:5432/accessible_pdf"
)

# Control SQL query logging (useful for debugging, noisy in production)
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    future=True,
)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Note: This auto-commits after successful request completion.
    For read-only operations, the commit is a no-op but harmless.

    Example usage in FastAPI:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """
    Initialize database schema.

    Creates all tables defined in SQLModel metadata.
    Note: Imports all models to ensure they're registered.
    """
    # Import all models to register them with SQLModel metadata
    from db.models import Job, ProcessingMetrics, User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
