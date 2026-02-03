"""API dependencies for authentication and database sessions."""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.database import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> None:
    """Verify API key from request header."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def get_authenticated_db(
    db: AsyncGenerator = Depends(get_db),
    _: None = Depends(verify_api_key),
) -> AsyncGenerator:
    """Get database session with API key authentication."""
    # get_db is already a generator that FastAPI handles,
    # so db is already the AsyncSession, not an async generator
    yield db
