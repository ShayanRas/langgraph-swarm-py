"""Supabase client initialization and helpers"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from gotrue.types import Session, User
from .models import UserInfo, TokenValidationError

# Global client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton"""
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client


async def verify_jwt_token(token: str) -> User:
    """Verify a JWT token and return user info"""
    try:
        client = get_supabase_client()
        
        # Get user from token
        response = client.auth.get_user(token)
        
        if not response or not response.user:
            raise TokenValidationError("Invalid token")
        
        return response.user
        
    except Exception as e:
        raise TokenValidationError(f"Token validation failed: {str(e)}")


def create_user_info(user: User) -> UserInfo:
    """Convert Supabase User to our UserInfo model"""
    return UserInfo(
        id=user.id,
        email=user.email or "",
        email_confirmed_at=user.email_confirmed_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        app_metadata=user.app_metadata or {},
        user_metadata=user.user_metadata or {}
    )


async def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user with email and password"""
    client = get_supabase_client()
    
    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    
    if not response.session:
        raise ValueError("Sign in failed")
    
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "expires_in": response.session.expires_in,
        "user": response.user.model_dump() if response.user and hasattr(response.user, 'model_dump') else {
            "id": response.user.id if response.user else None,
            "email": response.user.email if response.user else None,
            "created_at": response.user.created_at.isoformat() if response.user and response.user.created_at else None
        } if response.user else {}
    }


async def sign_up(email: str, password: str, redirect_to: Optional[str] = None) -> Dict[str, Any]:
    """Sign up a new user with proper email verification support"""
    client = get_supabase_client()
    
    # Default redirect URL for email confirmation
    app_url = os.getenv('APP_URL', 'http://localhost:8000')
    if not redirect_to:
        redirect_to = f"{app_url}/auth/confirm"
    
    try:
        # Sign up with options for email redirect
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "emailRedirectTo": redirect_to,
                "data": {
                    "app_name": "TikTok Swarm",
                    "registered_at": datetime.utcnow().isoformat()
                }
            }
        })
        
        # Check if email confirmation is required
        if response.user and not response.session:
            return {
                "status": "pending_confirmation",
                "message": "Success! Please check your email to confirm your account.",
                "user_id": response.user.id,
                "email": email,
                "requires_email_confirmation": True
            }
        
        # Immediate login (if email confirmation is disabled)
        if response.session:
            return {
                "status": "confirmed",
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in,
                "user": response.user.model_dump() if hasattr(response.user, 'model_dump') else {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at.isoformat() if response.user.created_at else None
                }
            }
        
        # Shouldn't reach here
        raise ValueError("Unexpected response from Supabase")
        
    except Exception as e:
        # Log the actual error for debugging
        print(f"Signup error: {str(e)}")
        # Parse common Supabase errors
        error_msg = str(e).lower()
        if "already registered" in error_msg:
            raise ValueError("This email is already registered. Please sign in instead.")
        elif "invalid email" in error_msg:
            raise ValueError("Please provide a valid email address.")
        elif "password" in error_msg:
            raise ValueError("Password must be at least 6 characters long.")
        else:
            raise ValueError(f"Sign up failed: {str(e)}")


async def sign_out(token: str) -> None:
    """Sign out a user"""
    client = get_supabase_client()
    client.auth.sign_out()


async def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh an access token"""
    client = get_supabase_client()
    
    response = client.auth.refresh_session(refresh_token)
    
    if not response.session:
        raise ValueError("Token refresh failed")
    
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "expires_in": response.session.expires_in,
        "user": response.user.model_dump() if response.user and hasattr(response.user, 'model_dump') else {
            "id": response.user.id if response.user else None,
            "email": response.user.email if response.user else None,
            "created_at": response.user.created_at.isoformat() if response.user and response.user.created_at else None
        } if response.user else {}
    }