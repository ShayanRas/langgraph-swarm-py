"""FastAPI dependencies for authentication"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .supabase_client import verify_jwt_token, create_user_info
from .models import UserInfo, UserContext, TokenValidationError

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> UserInfo:
    """Get the current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify the token and get user
        user = await verify_jwt_token(credentials.credentials)
        return create_user_info(user)
    except TokenValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )


async def get_user_context(
    user: UserInfo = Depends(get_current_user)
) -> UserContext:
    """Create user context from authenticated user"""
    # Extract permissions from app_metadata if available
    permissions = user.app_metadata.get("permissions", [])
    
    # Create user context
    return UserContext(
        user_id=user.id,
        email=user.email,
        permissions=permissions,
        metadata={
            "email_confirmed": user.email_confirmed_at is not None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            **user.user_metadata
        }
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[UserInfo]:
    """Get the current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        user = await verify_jwt_token(credentials.credentials)
        return create_user_info(user)
    except:
        return None


class RequirePermission:
    """Dependency to require specific permissions"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    async def __call__(self, user_context: UserContext = Depends(get_user_context)):
        if self.permission not in user_context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.permission}' required"
            )
        return user_context