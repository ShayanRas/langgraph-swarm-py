"""Factory for creating per-request configured session managers"""
from typing import Optional
from .session_manager import UserScopedTikTokManager, StealthLevel
import logging

logger = logging.getLogger(__name__)


def create_session_manager(
    stealth_mode: bool = True,
    browser_type: Optional[str] = None,
    headless: Optional[bool] = None,
    proxy_url: Optional[str] = None
) -> UserScopedTikTokManager:
    """
    Create a session manager with specific configuration for a request.
    
    This allows per-request customization of stealth settings.
    """
    import os
    
    # Determine stealth level
    if not stealth_mode:
        stealth_level: StealthLevel = "none"
    else:
        stealth_level = os.getenv("TIKTOK_STEALTH_LEVEL", "aggressive").lower()  # type: ignore
        if stealth_level not in ["basic", "aggressive"]:
            stealth_level = "aggressive"  # type: ignore
    
    # Use provided values or fall back to environment/defaults
    actual_browser = browser_type or os.getenv("TIKTOK_BROWSER", "chromium")
    actual_headless = headless if headless is not None else (
        os.getenv("TIKTOK_HEADLESS", "true").lower() == "true"
    )
    
    # For aggressive stealth, force non-headless
    if stealth_level == "aggressive" and actual_headless:
        logger.info("Overriding headless=True for aggressive stealth mode")
        actual_headless = False
    
    # Create configured session manager
    return UserScopedTikTokManager(
        max_sessions_per_user=int(os.getenv("TIKTOK_MAX_SESSIONS_PER_USER", "2")),
        session_timeout_seconds=int(os.getenv("TIKTOK_SESSION_TIMEOUT", "300")),
        headless=actual_headless,
        browser=actual_browser,
        stealth_level=stealth_level,
        enable_proxy=bool(proxy_url),
        proxy_url=proxy_url,
        random_browser=browser_type is None  # Random only if not specified
    )