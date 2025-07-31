"""API client for tools to call backend endpoints"""
import os
import httpx
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class TikTokAPIClient:
    """Client for calling TikTok API endpoints from tools"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.timeout = httpx.Timeout(30.0)  # 30 second timeout
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API endpoint"""
        url = urljoin(self.base_url, endpoint)
        
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                
                # Check for success
                if response.status_code >= 400:
                    error_detail = response.text
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("detail", error_detail)
                    except:
                        pass
                    
                    return {
                        "success": False,
                        "error": f"API Error ({response.status_code})",
                        "message": error_detail
                    }
                
                # Parse response
                return response.json()
                
            except httpx.TimeoutException:
                logger.error(f"Timeout calling {endpoint}")
                return {
                    "success": False,
                    "error": "Request Timeout",
                    "message": "The request took too long to complete"
                }
            except httpx.NetworkError as e:
                logger.error(f"Network error calling {endpoint}: {e}")
                return {
                    "success": False,
                    "error": "Network Error",
                    "message": "Could not connect to API server"
                }
            except Exception as e:
                logger.error(f"Unexpected error calling {endpoint}: {e}")
                return {
                    "success": False,
                    "error": "Unexpected Error",
                    "message": str(e)
                }
    
    async def analyze_trending(self, token: str, count: int = 10) -> Dict[str, Any]:
        """Call trending analysis endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/analyze/trending",
            token=token,
            json_data={"count": count}
        )
    
    async def analyze_hashtag(self, token: str, hashtag: str, count: int = 20) -> Dict[str, Any]:
        """Call hashtag analysis endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/analyze/hashtag",
            token=token,
            json_data={"hashtag": hashtag, "count": count}
        )
    
    async def analyze_video(self, token: str, video_url_or_id: str) -> Dict[str, Any]:
        """Call video analysis endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/analyze/video",
            token=token,
            json_data={"video_url_or_id": video_url_or_id}
        )
    
    async def get_video_details(self, token: str, video_url_or_id: str) -> Dict[str, Any]:
        """Call video details endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/analyze/video/details",
            token=token,
            json_data={"video_url_or_id": video_url_or_id}
        )
    
    async def search_content(self, token: str, query: str, count: int = 20) -> Dict[str, Any]:
        """Call search endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/search",
            token=token,
            json_data={"query": query, "count": count}
        )
    
    async def analyze_user_profile(self, token: str, username: str, video_count: int = 20) -> Dict[str, Any]:
        """Call user profile analysis endpoint"""
        return await self._make_request(
            method="POST",
            endpoint="/tiktok/analyze/user",
            token=token,
            json_data={"username": username, "video_count": video_count}
        )