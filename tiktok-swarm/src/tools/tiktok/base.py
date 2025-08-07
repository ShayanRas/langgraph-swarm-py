"""Base class for TikTok tools"""
import logging
import re
from typing import Dict, Any, Optional
from src.tiktok.session_manager import UserScopedTikTokManager
from src.tiktok.exceptions import TikTokAuthError, TikTokSessionError, TikTokDataError

logger = logging.getLogger(__name__)

# Global session manager instance
_session_manager: Optional[UserScopedTikTokManager] = None


def get_session_manager() -> UserScopedTikTokManager:
    """Get or create the global session manager"""
    global _session_manager
    if _session_manager is None:
        import os
        _session_manager = UserScopedTikTokManager(
            max_sessions_per_user=int(os.getenv("TIKTOK_MAX_SESSIONS_PER_USER", "2")),
            session_timeout_seconds=int(os.getenv("TIKTOK_SESSION_TIMEOUT", "300")),
            headless=os.getenv("TIKTOK_HEADLESS", "true").lower() == "true",
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            stealth_level=os.getenv("TIKTOK_STEALTH_LEVEL", "aggressive"),
            enable_proxy=os.getenv("TIKTOK_PROXY_ENABLED", "false").lower() == "true",
            proxy_url=os.getenv("TIKTOK_PROXY_URL"),
            random_browser=os.getenv("TIKTOK_RANDOM_BROWSER", "true").lower() == "true"
        )
    return _session_manager


async def get_user_ms_token_from_context(context: Dict[str, Any]) -> str:
    """Extract MS token from user context"""
    ms_token = context.get("ms_token")
    if not ms_token:
        raise TikTokAuthError("No TikTok MS token configured. Please set your MS token via the API.")
    return ms_token


class TikTokToolBase:
    """Base class for all TikTok tools"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_api_for_context(self, context: Dict[str, Any]):
        """Get TikTok API instance for the current user context"""
        user_id = context.get("user_id")
        if not user_id:
            raise TikTokAuthError("No user_id found in context")
        
        # Get MS token from context (already passed from API)
        ms_token = await get_user_ms_token_from_context(context)
        
        # Get or create session
        return await self.session_manager.get_api_for_user(user_id, ms_token)
    
    def format_error(self, error: Exception) -> Dict[str, Any]:
        """Format error response with detailed information"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the full error for debugging
        logger.error(f"Full error details: {error_type}: {error_message}")
        
        # Parse statusCode errors
        status_code = None
        if "statusCode:" in error_message:
            try:
                # Extract statusCode from error message
                match = re.search(r'statusCode:\s*(-?\d+)', error_message)
                if match:
                    status_code = int(match.group(1))
            except:
                pass
        
        # Handle TikTokApi library bug with malformed exceptions
        if "missing 2 required positional arguments" in error_message and "TikTokException" in error_message:
            # Extract the actual error details from the message
            actual_error = "Unknown error"
            possible_causes = []
            suggestions = []
            
            if "statusCode: -1" in error_message:
                actual_error = "TikTok API request failed with statusCode: -1"
                if "userInfo: {}" in error_message:
                    possible_causes = [
                        "User does not exist or is not accessible",
                        "User account may be private",
                        "MS token may be invalid or expired",
                        "Rate limit may have been exceeded"
                    ]
                    suggestions = [
                        "Verify the username is correct",
                        "Check if the user account is public",
                        "Get a fresh MS token",
                        "Wait a few minutes before retrying"
                    ]
                else:
                    possible_causes = [
                        "MS token may be invalid or expired", 
                        "Bot detection triggered",
                        "Network connectivity issues",
                        "TikTok API temporary failure"
                    ]
                    suggestions = [
                        "Get a fresh MS token from TikTok",
                        "Enable stealth mode and retry",
                        "Try a different browser type",
                        "Wait a few minutes before retrying"
                    ]
            
            return {
                "error": "TikTok API Error",
                "message": actual_error,
                "raw_error": error_message,
                "status_code": status_code,
                "possible_causes": possible_causes,
                "suggestions": suggestions
            }
        
        # Handle authentication errors
        if isinstance(error, TikTokAuthError) or "auth" in error_message.lower():
            return {
                "error": "Authentication Error",
                "message": error_message,
                "status_code": status_code,
                "possible_causes": ["MS token is missing or invalid"],
                "suggestions": ["Configure a valid TikTok MS token"]
            }
        
        # Handle session errors
        elif isinstance(error, TikTokSessionError):
            return {
                "error": "Session Error",
                "message": error_message,
                "status_code": status_code,
                "possible_causes": ["Session limit reached", "Session expired"],
                "suggestions": ["Wait a moment and retry", "Restart the container if issue persists"]
            }
        
        # Handle data errors
        elif isinstance(error, TikTokDataError):
            return {
                "error": "Data Error",
                "message": error_message,
                "status_code": status_code,
                "possible_causes": ["Content not available", "Invalid request parameters"],
                "suggestions": ["Verify the requested data exists", "Check request parameters"]
            }
        
        # Handle rate limiting
        elif "rate limit" in error_message.lower() or status_code == 429:
            return {
                "error": "Rate Limit Error",
                "message": "Too many requests to TikTok API",
                "status_code": status_code or 429,
                "possible_causes": ["API rate limit exceeded"],
                "suggestions": ["Wait 5-10 minutes before retrying", "Reduce request frequency"]
            }
        
        # Handle bot detection
        elif "bot" in error_message.lower() or "captcha" in error_message.lower():
            return {
                "error": "Bot Detection Error",
                "message": "TikTok detected automated access",
                "status_code": status_code,
                "possible_causes": ["Bot detection triggered", "Captcha required"],
                "suggestions": [
                    "Enable stealth mode",
                    "Use a different browser type",
                    "Add proxy configuration",
                    "Get a fresh MS token"
                ]
            }
        
        # Default error response with preserved details
        else:
            return {
                "error": error_type,
                "message": error_message,
                "raw_error": error_message,
                "status_code": status_code,
                "possible_causes": ["Unknown error occurred"],
                "suggestions": ["Check logs for more details", "Contact support if issue persists"]
            }
    
    def safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert a value to integer, handling strings and None values"""
        if value is None:
            return default
        
        # If already an integer, return it
        if isinstance(value, int):
            return value
        
        # If it's a string, try to convert
        if isinstance(value, str):
            # Handle empty strings
            if not value.strip():
                return default
            
            # Remove commas from numbers like "1,234,567"
            value = value.replace(',', '')
            
            try:
                # Try to convert to float first (handles "123.0") then to int
                return int(float(value))
            except (ValueError, TypeError):
                logger.warning(f"Could not convert '{value}' to int, using default {default}")
                return default
        
        # Try direct conversion for other types
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert {type(value).__name__} '{value}' to int, using default {default}")
            return default
    
    def format_video_data(self, video_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format video data consistently"""
        stats = video_dict.get("stats", {})
        author = video_dict.get("author", {})
        music = video_dict.get("music", {})
        
        return {
            "id": video_dict.get("id"),
            "description": video_dict.get("desc", ""),
            "create_time": video_dict.get("createTime"),
            "author": {
                "username": author.get("uniqueId", ""),
                "nickname": author.get("nickname", ""),
                "verified": author.get("verified", False),
                "follower_count": self.safe_int(author.get("followerCount", 0))
            },
            "stats": {
                "views": self.safe_int(stats.get("playCount", 0)),
                "likes": self.safe_int(stats.get("diggCount", 0)),
                "comments": self.safe_int(stats.get("commentCount", 0)),
                "shares": self.safe_int(stats.get("shareCount", 0)),
                "saves": self.safe_int(stats.get("collectCount", 0))
            },
            "music": {
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "original": music.get("original", False)
            },
            "hashtags": [tag.get("name", "") for tag in video_dict.get("challenges", [])],
            "url": f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{video_dict.get('id')}"
        }