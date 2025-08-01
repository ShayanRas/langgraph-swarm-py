"""User-scoped TikTok session management with stealth capabilities"""
import asyncio
from typing import Dict, Optional, Any, List, Literal
from datetime import datetime, timedelta
import logging
import random
import time
import os
from TikTokApi import TikTokApi
from playwright.async_api import BrowserContext, Page
try:
    # Try new API first (playwright-stealth 2.0+)
    from playwright_stealth import Stealth
    STEALTH_NEW_API = True
except ImportError:
    # Fall back to old API
    try:
        from playwright_stealth import stealth_async
        STEALTH_NEW_API = False
    except ImportError:
        # No stealth available
        Stealth = None
        stealth_async = None
        STEALTH_NEW_API = None
from .exceptions import TikTokAuthError, TikTokSessionError
from .proxy_manager import ProxyManager, get_proxy_manager, ProxyConfig

logger = logging.getLogger(__name__)


def is_running_in_container() -> bool:
    """Detect if running inside a Docker container"""
    # Check for Docker-specific files
    if os.path.exists("/.dockerenv"):
        return True
    
    # Check for container environment variables
    if os.environ.get("DOCKER_CONTAINER") or os.environ.get("KUBERNETES_SERVICE_HOST"):
        return True
    
    # Check cgroup for docker/containerd
    try:
        with open("/proc/self/cgroup", "r") as f:
            return "docker" in f.read() or "containerd" in f.read()
    except:
        pass
    
    return False


def can_run_headed_browser() -> bool:
    """Check if environment supports headed browsers"""
    # Check if DISPLAY is set (X11 available)
    if os.environ.get("DISPLAY"):
        return True
    
    # Check if running on Windows or macOS (usually have display)
    if os.name == "nt" or os.sys.platform == "darwin":
        return True
    
    # In container without display
    if is_running_in_container() and not os.environ.get("DISPLAY"):
        return False
    
    return True


# Stealth configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

VIEWPORT_SIZES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]

BrowserType = Literal["chromium", "webkit", "firefox"]
StealthLevel = Literal["none", "basic", "aggressive"]


class UserSession:
    """Represents a user's TikTok session"""
    def __init__(self, user_id: str, api: TikTokApi, ms_token: str, proxy: Optional[ProxyConfig] = None):
        self.user_id = user_id
        self.api = api
        self.ms_token = ms_token
        self.proxy = proxy
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.request_count = 0
        self._lock = asyncio.Lock()
    
    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if session has expired"""
        return (datetime.utcnow() - self.last_used).seconds > timeout_seconds
    
    async def use(self):
        """Mark session as used"""
        async with self._lock:
            self.last_used = datetime.utcnow()
            self.request_count += 1


class UserScopedTikTokManager:
    """Manages TikTok sessions per user with resource limits and stealth capabilities"""
    
    def __init__(
        self,
        max_sessions_per_user: int = 2,
        session_timeout_seconds: int = 300,
        headless: bool = True,
        browser: str = "chromium",
        stealth_level: StealthLevel = "aggressive",
        enable_proxy: bool = False,
        proxy_url: Optional[str] = None,
        random_browser: bool = True,
        proxy_manager: Optional[ProxyManager] = None
    ):
        self._user_sessions: Dict[str, UserSession] = {}
        self._max_sessions_per_user = max_sessions_per_user
        self._session_timeout = session_timeout_seconds
        self._headless = headless
        self._browser = browser
        self._stealth_level = stealth_level
        self._enable_proxy = enable_proxy
        self._proxy_url = proxy_url
        self._random_browser = random_browser
        self._proxy_manager = proxy_manager or (get_proxy_manager() if enable_proxy else None)
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._browser_types: List[BrowserType] = ["chromium", "webkit", "firefox"]
        
    async def start(self):
        """Start the session manager with cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("TikTok session manager started with cleanup task")
        
    async def stop(self):
        """Stop the session manager and cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all sessions
        async with self._lock:
            for session in self._user_sessions.values():
                try:
                    await session.api.close_sessions()
                    await session.api.stop_playwright()
                except Exception as e:
                    logger.error(f"Error closing session for user {session.user_id}: {e}")
            self._user_sessions.clear()
    
    async def _cleanup_loop(self):
        """Periodically cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        async with self._lock:
            expired_users = []
            for user_id, session in self._user_sessions.items():
                if session.is_expired(self._session_timeout):
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                session = self._user_sessions.pop(user_id)
                try:
                    await session.api.close_sessions()
                    await session.api.stop_playwright()
                    logger.info(f"Cleaned up expired session for user {user_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up session for user {user_id}: {e}")
    
    def _get_random_browser(self) -> str:
        """Get a random browser type for diversity"""
        if self._random_browser:
            return random.choice(self._browser_types)
        return self._browser
    
    def _proxy_to_tiktok_format(self, proxy: Optional[ProxyConfig]) -> Optional[List[Dict[str, str]]]:
        """Convert ProxyConfig to TikTokApi expected format"""
        if not proxy:
            return None
        
        # TikTokApi expects a list of proxy dictionaries
        proxy_dict = {"server": proxy.url}
        
        # Add authentication if available
        if proxy.username and proxy.password:
            proxy_dict["username"] = proxy.username
            proxy_dict["password"] = proxy.password
        
        return [proxy_dict]
    
    async def _get_stealth_context_options(self, proxy: Optional[ProxyConfig] = None) -> Dict[str, Any]:
        """Generate stealth context options based on stealth level"""
        viewport = random.choice(VIEWPORT_SIZES)
        user_agent = random.choice(USER_AGENTS)
        
        base_options = {
            "viewport": viewport,
            "user_agent": user_agent,
            "locale": random.choice(["en-US", "en-GB", "en-CA"]),
            "timezone_id": random.choice(["America/New_York", "America/Chicago", "America/Los_Angeles"]),
            "ignore_https_errors": True,
            "java_script_enabled": True,
        }
        
        if self._stealth_level == "aggressive":
            # Add more aggressive stealth options
            # Note: Some options like ignore_default_args are browser launch options,
            # not context options. Since TikTokApi manages browser launch, we can
            # only control context-level settings here.
            base_options.update({
                # Valid context-level options for stealth
                "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
                "is_mobile": False,
                "has_touch": False,
                "color_scheme": random.choice(["light", "dark", "no-preference"]),
                # Additional stealth context options
                "reduced_motion": random.choice(["no-preference", "reduce"]),
                "forced_colors": "none",
            })
            
            # Add WebRTC leak prevention
            base_options["permissions"] = []  # Deny all permissions by default
        
        # Note: Proxy is now passed via TikTokApi's proxies parameter
        # to avoid conflicts with playwright context creation
        
        return base_options
    
    async def _add_human_behavior(self, sleep_min: float = 2.0, sleep_max: float = 5.0):
        """Add random human-like delays"""
        if self._stealth_level != "none":
            delay = random.uniform(sleep_min, sleep_max)
            await asyncio.sleep(delay)
    
    async def _setup_stealth_page(self, page: Page):
        """Apply stealth modifications to a page (for old API only)"""
        if self._stealth_level != "none" and STEALTH_NEW_API is False and stealth_async:
            # Old API: apply stealth to individual pages
            await stealth_async(page)
            
            # Additional stealth measures
            if self._stealth_level == "aggressive":
                # Override navigator properties
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'denied' })
                        })
                    });
                """)
    
    async def get_api_for_user(self, user_id: str, ms_token: str) -> TikTokApi:
        """Get or create TikTok API instance for user"""
        async with self._lock:
            # Check if user has existing session
            if user_id in self._user_sessions:
                session = self._user_sessions[user_id]
                
                # Check if token has changed
                if session.ms_token != ms_token:
                    # Close old session and create new one
                    try:
                        await session.api.close_sessions()
                        await session.api.stop_playwright()
                    except Exception as e:
                        logger.error(f"Error closing old session: {e}")
                    del self._user_sessions[user_id]
                else:
                    # Use existing session
                    await session.use()
                    return session.api
            
            # Check session limit
            user_session_count = sum(1 for s in self._user_sessions.values() if s.user_id == user_id)
            if user_session_count >= self._max_sessions_per_user:
                raise TikTokSessionError(f"User {user_id} has reached session limit of {self._max_sessions_per_user}")
            
            # Create new session with stealth
            try:
                # Select browser type
                browser_type = self._get_random_browser()
                
                # Get proxy from proxy manager if enabled
                proxy = None
                if self._enable_proxy and self._proxy_manager:
                    proxy = await self._proxy_manager.get_proxy()
                    if proxy:
                        logger.info(f"Using proxy {proxy.url} for user {user_id}")
                    else:
                        logger.warning(f"No available proxy for user {user_id}")
                
                # Get stealth context options with proxy
                context_options = await self._get_stealth_context_options(proxy)
                
                # Add human-like delay before creating session
                await self._add_human_behavior(1.0, 3.0)
                
                logger.info(f"Creating TikTok session for user {user_id} with browser: {browser_type}, stealth: {self._stealth_level}")
                
                api = TikTokApi(logging_level=logging.INFO)
                
                # Note: playwright-stealth integration is limited because TikTokApi manages
                # its own playwright instance. We rely on context_options for stealth:
                # - Custom user agents
                # - Browser arguments to disable automation detection
                # - Viewport randomization
                # - Timezone/locale settings
                # Future improvement: Fork TikTokApi to integrate playwright-stealth directly
                
                # Smart headless detection
                use_headless = self._headless
                
                # If aggressive stealth wants non-headless but environment can't support it
                if self._stealth_level == "aggressive" and not self._headless:
                    if not can_run_headed_browser():
                        logger.warning(
                            f"Cannot run headed browser in container without display. "
                            f"Forcing headless=True. To run headed, ensure Xvfb is running "
                            f"or set DISPLAY environment variable."
                        )
                        use_headless = True
                    else:
                        use_headless = False
                
                # Convert proxy to TikTokApi format
                tiktok_proxies = self._proxy_to_tiktok_format(proxy)
                
                # Handle static proxy if no dynamic proxy
                if not tiktok_proxies and self._enable_proxy and self._proxy_url:
                    tiktok_proxies = [{"server": self._proxy_url}]
                
                await api.create_sessions(
                    ms_tokens=[ms_token],
                    num_sessions=1,
                    headless=use_headless,
                    browser=browser_type,
                    proxies=tiktok_proxies,  # Pass proxy via proxies parameter
                    sleep_after=5 if self._stealth_level != "none" else 3,
                    suppress_resource_load_types=["font"] if self._stealth_level == "aggressive" else ["image", "media", "font"],
                    context_options=context_options
                )
                
                # Store session with proxy info
                session = UserSession(user_id, api, ms_token, proxy)
                self._user_sessions[user_id] = session
                logger.info(f"Created new TikTok session for user {user_id}")
                
                return api
                
            except Exception as e:
                logger.error(f"Failed to create TikTok session for user {user_id}: {e}")
                # Report proxy failure if proxy was used
                if proxy and self._proxy_manager:
                    await self._proxy_manager.report_failure(proxy, str(e))
                raise TikTokAuthError(f"Failed to create TikTok session: {str(e)}")
    
    async def report_request_success(self, user_id: str, response_time: float = 0):
        """Report successful request for proxy tracking"""
        if user_id in self._user_sessions:
            session = self._user_sessions[user_id]
            if session.proxy and self._proxy_manager:
                await self._proxy_manager.report_success(session.proxy, response_time)
    
    async def report_request_failure(self, user_id: str, error: str):
        """Report failed request for proxy tracking"""
        if user_id in self._user_sessions:
            session = self._user_sessions[user_id]
            if session.proxy and self._proxy_manager:
                await self._proxy_manager.report_failure(session.proxy, error)
    
    async def remove_user_session(self, user_id: str):
        """Manually remove a user's session"""
        async with self._lock:
            if user_id in self._user_sessions:
                session = self._user_sessions.pop(user_id)
                try:
                    await session.api.close_sessions()
                    await session.api.stop_playwright()
                    logger.info(f"Removed session for user {user_id}")
                except Exception as e:
                    logger.error(f"Error removing session for user {user_id}: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions"""
        total_sessions = len(self._user_sessions)
        users_with_sessions = len(set(s.user_id for s in self._user_sessions.values()))
        
        session_details = []
        for session in self._user_sessions.values():
            session_details.append({
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_used": session.last_used.isoformat(),
                "request_count": session.request_count,
                "is_expired": session.is_expired(self._session_timeout),
                "proxy": session.proxy.url if session.proxy else None
            })
        
        stats = {
            "total_sessions": total_sessions,
            "unique_users": users_with_sessions,
            "max_sessions_per_user": self._max_sessions_per_user,
            "session_timeout_seconds": self._session_timeout,
            "sessions": session_details
        }
        
        # Add proxy stats if available
        if self._proxy_manager:
            stats["proxy_stats"] = self._proxy_manager.get_stats()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for session manager"""
        active_sessions = len(self._user_sessions)
        expired_count = sum(
            1 for s in self._user_sessions.values() 
            if s.is_expired(self._session_timeout)
        )
        
        # Estimate memory usage (rough estimate)
        memory_per_session_mb = 400 if not self._headless else 300  # Non-headless uses more
        estimated_memory_mb = active_sessions * memory_per_session_mb
        
        return {
            "healthy": active_sessions < 10,  # Arbitrary limit for health
            "active_sessions": active_sessions,
            "expired_sessions": expired_count,
            "estimated_memory_mb": estimated_memory_mb,
            "max_sessions_per_user": self._max_sessions_per_user,
            "cleanup_task_running": self._cleanup_task is not None and not self._cleanup_task.done(),
            "stealth_config": {
                "level": self._stealth_level,
                "headless": self._headless,
                "browser": self._browser,
                "random_browser": self._random_browser,
                "proxy_enabled": self._enable_proxy
            }
        }


# Global session manager instance
_session_manager: Optional[UserScopedTikTokManager] = None


def get_session_manager() -> UserScopedTikTokManager:
    """Get the global session manager instance with configuration from environment"""
    global _session_manager
    if _session_manager is None:
        import os
        
        # Read configuration from environment
        stealth_level = os.getenv("TIKTOK_STEALTH_LEVEL", "aggressive").lower()
        if stealth_level not in ["none", "basic", "aggressive"]:
            stealth_level = "aggressive"
        
        _session_manager = UserScopedTikTokManager(
            max_sessions_per_user=int(os.getenv("TIKTOK_MAX_SESSIONS_PER_USER", "2")),
            session_timeout_seconds=int(os.getenv("TIKTOK_SESSION_TIMEOUT", "300")),
            headless=os.getenv("TIKTOK_HEADLESS", "true").lower() == "true",
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            stealth_level=stealth_level,  # type: ignore
            enable_proxy=os.getenv("TIKTOK_PROXY_ENABLED", "false").lower() == "true",
            proxy_url=os.getenv("TIKTOK_PROXY_URL"),
            random_browser=os.getenv("TIKTOK_RANDOM_BROWSER", "true").lower() == "true"
        )
    return _session_manager