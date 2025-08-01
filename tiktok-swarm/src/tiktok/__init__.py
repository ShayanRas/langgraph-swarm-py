"""TikTok integration module"""
from .session_manager import UserScopedTikTokManager, get_session_manager
from .proxy_manager import ProxyManager, get_proxy_manager, ProxyConfig
from .models import TikTokVideo, TikTokUser, TikTokHashtag, TikTokSound
from .exceptions import TikTokAuthError, TikTokSessionError, TikTokDataError

__all__ = [
    "UserScopedTikTokManager",
    "get_session_manager",
    "ProxyManager",
    "get_proxy_manager",
    "ProxyConfig",
    "TikTokVideo",
    "TikTokUser",
    "TikTokHashtag",
    "TikTokSound",
    "TikTokAuthError",
    "TikTokSessionError",
    "TikTokDataError",
]