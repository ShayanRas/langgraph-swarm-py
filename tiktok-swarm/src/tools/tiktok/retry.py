"""Retry logic for TikTok API calls with bot detection handling"""
import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional, Dict
from functools import wraps
import backoff

logger = logging.getLogger(__name__)

T = TypeVar('T')


def is_bot_detection_error(exception: Exception) -> bool:
    """Check if the exception is related to bot detection"""
    error_msg = str(exception).lower()
    bot_detection_keywords = [
        "emptyresponseexception",
        "empty response",
        "bot detection",
        "detecting you're a bot",
        "blocked",
        "captcha",
        "verification required"
    ]
    return any(keyword in error_msg for keyword in bot_detection_keywords)


def with_retry_on_bot_detection(
    max_tries: int = 3,
    escalate_strategy: bool = True
):
    """
    Decorator to retry TikTok API calls with escalating anti-detection strategies.
    
    Args:
        max_tries: Maximum number of retry attempts
        escalate_strategy: Whether to escalate anti-detection measures on retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_tries):
                try:
                    # Log attempt
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{max_tries} for {func.__name__}")
                    
                    # Escalate strategy on retry
                    if escalate_strategy and attempt > 0:
                        # Modify context if available
                        if len(args) > 1 and isinstance(args[1], dict):
                            context = args[1]
                            
                            # Escalation strategies
                            if attempt == 1:
                                # Second attempt: Switch browser
                                logger.info("Escalating: Switching to webkit browser")
                                context["override_browser"] = "webkit"
                                context["override_headless"] = True
                            elif attempt == 2:
                                # Third attempt: Non-headless firefox
                                logger.info("Escalating: Using non-headless firefox")
                                context["override_browser"] = "firefox"
                                context["override_headless"] = False
                    
                    # Add delay between retries
                    if attempt > 0:
                        delay = 5 * attempt  # Exponential backoff
                        logger.info(f"Waiting {delay} seconds before retry...")
                        await asyncio.sleep(delay)
                    
                    # Call the function
                    result = await func(*args, **kwargs)
                    
                    # Check if result indicates bot detection
                    if isinstance(result, dict) and not result.get("success", True):
                        error_msg = result.get("error", "")
                        if is_bot_detection_error(Exception(error_msg)):
                            raise Exception(f"Bot detection in result: {error_msg}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if is_bot_detection_error(e):
                        logger.warning(f"Bot detection error on attempt {attempt + 1}: {e}")
                        
                        if attempt < max_tries - 1:
                            continue  # Retry
                        else:
                            # Final attempt failed, return helpful error
                            return {
                                "success": False,
                                "error": "BotDetectionError",
                                "message": str(e),
                                "suggestions": [
                                    "Try again in a few minutes",
                                    "Use a different MS token",
                                    "Enable proxy in settings",
                                    "Switch to non-headless mode",
                                    "Try a different browser (webkit/firefox)"
                                ],
                                "attempts": max_tries
                            }
                    else:
                        # Non-bot detection error, don't retry
                        raise
            
            # Should not reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


# Backoff decorator for rate limiting
rate_limit_backoff = backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    max_time=30,
    giveup=lambda e: not is_bot_detection_error(e)
)