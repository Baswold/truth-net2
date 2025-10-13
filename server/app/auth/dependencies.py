"""Authentication dependencies for FastAPI routes."""
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Member
from .jwt import decode_token

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_session)],
) -> Member:
    """Dependency to get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token type is "access" (not refresh)
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    member = db.query(Member).filter(Member.id == int(user_id)).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return member


def get_current_active_user(
    current_user: Annotated[Member, Depends(get_current_user)]
) -> Member:
    """Dependency to ensure the user is active (not suspended)."""
    if current_user.strike_count >= 3:  # Configurable threshold
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended due to strikes"
        )
    return current_user


def require_role(*required_roles: str) -> Callable:
    """Dependency factory to require specific roles.
    
    Usage:
        @router.get("/admin")
        def admin_route(user: Member = Depends(require_role("admin", "curator"))):
            ...
    """
    def role_checker(current_user: Annotated[Member, Depends(get_current_active_user)]) -> Member:
        user_roles = set(role.strip() for role in current_user.roles.split(","))
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker
