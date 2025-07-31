"""Authentication models for Supabase integration"""
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime


class AuthRequest(BaseModel):
    """Request model for authentication endpoints"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication endpoints"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserInfo(BaseModel):
    """User information from Supabase auth"""
    id: str
    email: str
    email_confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    app_metadata: Dict[str, Any] = {}
    user_metadata: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserContext(BaseModel):
    """User context to be passed through LangGraph config"""
    user_id: str
    email: str
    permissions: List[str] = []
    metadata: Dict[str, Any] = {}
    ms_token: Optional[str] = None  # TikTok MS token from user metadata
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LangGraph config"""
        return {
            "user_id": self.user_id,
            "user_email": self.email,
            "permissions": self.permissions,
            "user_metadata": self.metadata,
            "ms_token": self.ms_token
        }


class TokenValidationError(Exception):
    """Raised when JWT token validation fails"""
    pass