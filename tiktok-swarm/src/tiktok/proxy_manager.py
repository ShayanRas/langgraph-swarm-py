"""
Proxy management for TikTok API with support for multiple proxy providers
and intelligent rotation strategies.
"""
import os
import random
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

ProxyProvider = Literal["webshare", "custom", "list"]


@dataclass
class ProxyConfig:
    """Configuration for a single proxy"""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    last_used: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    response_time: float = 0.0
    is_banned: bool = False
    
    def to_playwright_format(self) -> Dict[str, Any]:
        """Convert to Playwright proxy format"""
        parsed = urlparse(self.url)
        
        proxy_dict = {
            "server": self.url
        }
        
        # Add auth if available
        if self.username and self.password:
            proxy_dict["username"] = self.username
            proxy_dict["password"] = self.password
        elif parsed.username and parsed.password:
            # Extract from URL if present
            proxy_dict["username"] = parsed.username
            proxy_dict["password"] = parsed.password
        
        return proxy_dict
    
    @property
    def health_score(self) -> float:
        """Calculate proxy health score (0-1)"""
        if self.is_banned:
            return 0.0
        
        # Calculate based on success rate and response time
        total_requests = self.success_count + self.failure_count
        if total_requests == 0:
            return 0.5  # Neutral for new proxies
        
        success_rate = self.success_count / total_requests
        
        # Penalize slow proxies (response time in seconds)
        speed_score = max(0, 1 - (self.response_time / 10))
        
        # Weighted score
        return (success_rate * 0.7) + (speed_score * 0.3)


class ProxyManager:
    """Manages proxy rotation and health tracking"""
    
    def __init__(
        self,
        provider: ProxyProvider = "custom",
        webshare_api_key: Optional[str] = None,
        custom_proxies: Optional[List[str]] = None,
        rotation_strategy: Literal["random", "round_robin", "health_based"] = "health_based",
        min_proxy_delay: float = 5.0,  # Minimum seconds between uses of same proxy
        ban_threshold: int = 5,  # Failures before banning
        test_on_init: bool = True
    ):
        self.provider = provider
        self.webshare_api_key = webshare_api_key or os.getenv("WEBSHARE_API_KEY")
        self.rotation_strategy = rotation_strategy
        self.min_proxy_delay = min_proxy_delay
        self.ban_threshold = ban_threshold
        
        self.proxies: List[ProxyConfig] = []
        self.current_index = 0
        self._lock = asyncio.Lock()
        self._initialized = False
        self._test_on_init = test_on_init
        
        # Initialize with custom proxies if provided
        if custom_proxies:
            self.proxies = [self._parse_proxy_url(url) for url in custom_proxies]
    
    def _parse_proxy_url(self, proxy_url: str) -> ProxyConfig:
        """Parse proxy URL into ProxyConfig"""
        # Support various formats:
        # http://user:pass@host:port
        # http://host:port
        # socks5://user:pass@host:port
        
        parsed = urlparse(proxy_url)
        
        # Extract auth from URL if present
        username = parsed.username
        password = parsed.password
        
        # Reconstruct URL without auth
        if username and password:
            clean_url = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
        else:
            clean_url = proxy_url
        
        return ProxyConfig(
            url=clean_url,
            username=username,
            password=password
        )
    
    async def initialize(self):
        """Initialize proxy list from provider"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                if self.provider == "webshare":
                    await self._fetch_webshare_proxies()
                elif self.provider == "list":
                    # Load from environment or file
                    proxy_list = os.getenv("PROXY_LIST", "").split(",")
                    self.proxies = [self._parse_proxy_url(url.strip()) 
                                   for url in proxy_list if url.strip()]
                    if not self.proxies:
                        raise ValueError("No proxies found in PROXY_LIST environment variable")
                elif self.provider == "custom" and not self.proxies:
                    # Custom proxies should be provided in constructor
                    logger.warning("No custom proxies provided, proxy rotation disabled")
                
                if self._test_on_init and self.proxies:
                    logger.info(f"Testing {len(self.proxies)} proxies...")
                    await self._test_all_proxies()
                
                self._initialized = True
                logger.info(f"Initialized {len(self.proxies)} proxies from {self.provider} provider")
                
            except Exception as e:
                logger.error(f"Failed to initialize proxy manager: {e}")
                self._initialized = False
                # Re-raise with more context
                raise Exception(f"Proxy initialization failed ({self.provider}): {str(e)}")
    
    async def _fetch_webshare_proxies(self):
        """Fetch proxy list from Webshare API"""
        if not self.webshare_api_key:
            raise ValueError("Webshare API key not provided")
        
        headers = {
            "Authorization": f"Token {self.webshare_api_key}"
        }
        
        # Get mode from environment (default to direct)
        mode = os.getenv("WEBSHARE_MODE", "direct").lower()
        if mode not in ["direct", "backbone"]:
            logger.warning(f"Invalid WEBSHARE_MODE '{mode}', defaulting to 'direct'")
            mode = "direct"
        
        try:
            async with aiohttp.ClientSession() as session:
                page = 1
                has_more = True
                
                while has_more:
                    # Webshare API requires mode parameter
                    params = {
                        "mode": mode,
                        "page": page,
                        "page_size": 100  # Max allowed
                    }
                    
                    async with session.get(
                        "https://proxy.webshare.io/api/v2/proxy/list/",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Process proxies
                            results = data.get("results", [])
                            for proxy_data in results:
                                # Webshare provides proxies in a specific format
                                proxy_url = f"http://{proxy_data['proxy_address']}:{proxy_data['port']}"
                                
                                config = ProxyConfig(
                                    url=proxy_url,
                                    username=proxy_data.get("username"),
                                    password=proxy_data.get("password")
                                )
                                self.proxies.append(config)
                            
                            # Check if there are more pages
                            has_more = data.get("next") is not None
                            page += 1
                            
                            # Log progress
                            logger.info(f"Fetched {len(results)} proxies from Webshare (page {page-1})")
                        else:
                            error_text = await response.text()
                            error_msg = f"Failed to fetch Webshare proxies: {response.status} - {error_text}"
                            
                            # Provide helpful error messages
                            if response.status == 400 and "mode" in error_text:
                                error_msg += "\nEnsure WEBSHARE_MODE is set to 'direct' or 'backbone' based on your plan"
                            elif response.status == 401:
                                error_msg += "\nCheck your WEBSHARE_API_KEY is valid"
                            
                            raise Exception(error_msg)
                
                if not self.proxies:
                    raise Exception("No proxies returned from Webshare. Check your subscription status.")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching Webshare proxies: {e}")
            raise Exception(f"Network error connecting to Webshare: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching Webshare proxies: {e}")
            raise
    
    async def _test_proxy(self, proxy: ProxyConfig) -> bool:
        """Test if a proxy is working"""
        test_url = "https://www.tiktok.com/robots.txt"
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Create proxy auth
            proxy_auth = None
            if proxy.username and proxy.password:
                proxy_auth = aiohttp.BasicAuth(proxy.username, proxy.password)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    test_url,
                    proxy=proxy.url,
                    proxy_auth=proxy_auth,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                ) as response:
                    if response.status == 200:
                        proxy.response_time = asyncio.get_event_loop().time() - start_time
                        proxy.success_count += 1
                        return True
                    else:
                        proxy.failure_count += 1
                        return False
        
        except Exception as e:
            logger.debug(f"Proxy test failed for {proxy.url}: {e}")
            proxy.failure_count += 1
            return False
    
    async def _test_all_proxies(self):
        """Test all proxies concurrently"""
        tasks = [self._test_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        working_count = sum(1 for r in results if r is True)
        logger.info(f"Proxy test complete: {working_count}/{len(self.proxies)} working")
    
    async def get_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy based on rotation strategy"""
        if not self._initialized:
            await self.initialize()
        
        async with self._lock:
            if not self.proxies:
                return None
            
            # Filter out banned and recently used proxies
            available_proxies = [
                p for p in self.proxies 
                if not p.is_banned and (
                    p.last_used is None or 
                    datetime.now() - p.last_used > timedelta(seconds=self.min_proxy_delay)
                )
            ]
            
            if not available_proxies:
                # If no proxies available, reset ban on least failed proxy
                if all(p.is_banned for p in self.proxies):
                    least_failed = min(self.proxies, key=lambda p: p.failure_count)
                    least_failed.is_banned = False
                    least_failed.failure_count = 0
                    available_proxies = [least_failed]
                else:
                    # Wait a bit and try again
                    return None
            
            # Select proxy based on strategy
            if self.rotation_strategy == "random":
                proxy = random.choice(available_proxies)
            elif self.rotation_strategy == "round_robin":
                proxy = available_proxies[self.current_index % len(available_proxies)]
                self.current_index += 1
            elif self.rotation_strategy == "health_based":
                # Sort by health score and pick from top performers
                sorted_proxies = sorted(available_proxies, key=lambda p: p.health_score, reverse=True)
                # Add some randomness to top performers
                top_count = max(1, len(sorted_proxies) // 3)
                proxy = random.choice(sorted_proxies[:top_count])
            else:
                proxy = available_proxies[0]
            
            proxy.last_used = datetime.now()
            return proxy
    
    async def report_success(self, proxy: ProxyConfig, response_time: float = 0):
        """Report successful proxy use"""
        async with self._lock:
            proxy.success_count += 1
            if response_time > 0:
                # Running average of response time
                proxy.response_time = (proxy.response_time + response_time) / 2
    
    async def report_failure(self, proxy: ProxyConfig, error: Optional[str] = None):
        """Report proxy failure"""
        async with self._lock:
            proxy.failure_count += 1
            
            # Check if we should ban this proxy
            if proxy.failure_count >= self.ban_threshold:
                proxy.is_banned = True
                logger.warning(f"Banning proxy {proxy.url} after {proxy.failure_count} failures")
            
            # Log specific error patterns
            if error and "captcha" in error.lower():
                logger.info(f"Proxy {proxy.url} triggered captcha")
            elif error and "statusCode: -1" in error:
                logger.info(f"Proxy {proxy.url} blocked by TikTok")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        total = len(self.proxies)
        banned = sum(1 for p in self.proxies if p.is_banned)
        
        avg_success_rate = 0
        if total > 0:
            success_rates = []
            for p in self.proxies:
                total_requests = p.success_count + p.failure_count
                if total_requests > 0:
                    success_rates.append(p.success_count / total_requests)
            
            if success_rates:
                avg_success_rate = sum(success_rates) / len(success_rates)
        
        return {
            "total_proxies": total,
            "banned_proxies": banned,
            "active_proxies": total - banned,
            "average_success_rate": avg_success_rate,
            "rotation_strategy": self.rotation_strategy,
            "provider": self.provider
        }


# Global proxy manager instance
_proxy_manager: Optional[ProxyManager] = None


def get_proxy_manager() -> ProxyManager:
    """Get or create global proxy manager instance"""
    global _proxy_manager
    
    if _proxy_manager is None:
        # Initialize based on environment
        provider = os.getenv("PROXY_PROVIDER", "custom")
        
        if provider == "webshare":
            _proxy_manager = ProxyManager(
                provider="webshare",
                webshare_api_key=os.getenv("WEBSHARE_API_KEY"),
                rotation_strategy=os.getenv("PROXY_ROTATION_STRATEGY", "health_based"),
                test_on_init=os.getenv("PROXY_TEST_ON_INIT", "true").lower() == "true"
            )
        else:
            # Custom proxy list
            proxy_list = os.getenv("PROXY_LIST", "").split(",")
            proxy_list = [p.strip() for p in proxy_list if p.strip()]
            
            _proxy_manager = ProxyManager(
                provider="custom",
                custom_proxies=proxy_list,
                rotation_strategy=os.getenv("PROXY_ROTATION_STRATEGY", "health_based"),
                test_on_init=os.getenv("PROXY_TEST_ON_INIT", "true").lower() == "true"
            )
    
    return _proxy_manager