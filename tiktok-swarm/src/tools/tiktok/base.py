"""Base class for TikTok tools"""
import logging
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
        _session_manager = UserScopedTikTokManager(
            max_sessions_per_user=2,
            session_timeout_seconds=300,
            headless=True,  # Always headless in production
            browser="chromium"
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
        """Format error response consistently"""
        error_type = type(error).__name__
        error_message = str(error)
        
        if isinstance(error, TikTokAuthError):
            return {
                "error": "Authentication Error",
                "message": error_message,
                "action_required": "Please configure your TikTok MS token"
            }
        elif isinstance(error, TikTokSessionError):
            return {
                "error": "Session Error",
                "message": error_message,
                "action_required": "Please try again or contact support"
            }
        elif isinstance(error, TikTokDataError):
            return {
                "error": "Data Error", 
                "message": error_message,
                "action_required": "The requested data could not be retrieved"
            }
        else:
            return {
                "error": error_type,
                "message": error_message,
                "action_required": "An unexpected error occurred"
            }
    
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
                "follower_count": author.get("followerCount", 0)
            },
            "stats": {
                "views": stats.get("playCount", 0),
                "likes": stats.get("diggCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
                "saves": stats.get("collectCount", 0)
            },
            "music": {
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "original": music.get("original", False)
            },
            "hashtags": [tag.get("name", "") for tag in video_dict.get("challenges", [])],
            "url": f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{video_dict.get('id')}"
        }