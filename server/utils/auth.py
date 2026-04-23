"""Authentication utility functions for token validation and user management."""
import hashlib
import secrets
from datetime import datetime
from fastapi import HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.token import Token
from models.user import User


def hash_token(token: str) -> str:
    """
    Generate SHA256 hash of a token.

    Args:
        token: The raw token string to hash

    Returns:
        Hexadecimal SHA256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    """
    Generate a cryptographically secure random token.

    Returns:
        URL-safe random token string (32 bytes)
    """
    return secrets.token_urlsafe(32)


async def get_current_user(
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from a token.

    This function is designed to be used as a FastAPI dependency in protected routes.
    It extracts and validates the authentication token from the Authorization header
    or directly from the token parameter, then returns the associated user.

    Args:
        token: Authentication token (can be passed as "Bearer <token>" or raw token)
        db: Database session (injected by FastAPI)

    Returns:
        The authenticated User object

    Raises:
        HTTPException 401: If no token is provided or token is invalid
        HTTPException 403: If user account is disabled
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )

    # Extract token from Authorization header if present
    if token.startswith("Bearer "):
        token = token[7:]

    # Hash the token for database lookup
    token_hash = hash_token(token)

    # Query token and user in a single join
    result = await db.execute(
        select(Token, User)
        .join(User, Token.user_id == User.id)
        .where(Token.token_hash == token_hash)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    token_obj, user = row

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # Update last used timestamp for tracking
    token_obj.last_used_at = datetime.utcnow()
    await db.commit()

    return user
