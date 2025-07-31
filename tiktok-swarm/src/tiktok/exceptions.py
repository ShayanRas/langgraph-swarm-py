"""Custom exceptions for TikTok integration"""


class TikTokError(Exception):
    """Base exception for TikTok integration"""
    pass


class TikTokAuthError(TikTokError):
    """Raised when TikTok authentication fails"""
    pass


class TikTokSessionError(TikTokError):
    """Raised when session management fails"""
    pass


class TikTokRateLimitError(TikTokError):
    """Raised when rate limit is exceeded"""
    pass


class TikTokDataError(TikTokError):
    """Raised when data extraction fails"""
    pass