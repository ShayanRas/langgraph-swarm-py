"""Tools for analyzing individual TikTok videos"""
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from .base import TikTokToolBase
import logging
import re
import os

logger = logging.getLogger(__name__)


class VideoAnalyzer(TikTokToolBase):
    """Handles individual video analysis"""
    
    async def get_video_by_url_or_id(self, api, url_or_id: str) -> Optional[Any]:
        """Get video object handling both URLs and IDs"""
        # If it's already a full URL, use it directly
        if url_or_id.startswith(('http://', 'https://')):
            return api.video(url=url_or_id)
        
        # If it's a numeric ID, we need more info
        if url_or_id.isdigit():
            # Try to get video info with just ID first
            video = api.video(id=url_or_id)
            # The API might require a URL for some operations
            # We'll handle errors in the calling function
            return video
        
        # Might be a short URL code
        if len(url_or_id) < 20:  # Short codes are typically shorter
            short_url = f"https://vm.tiktok.com/{url_or_id}"
            return api.video(url=short_url)
        
        # Default: treat as ID
        return api.video(id=url_or_id)
    
    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """Extract video ID from URL or return ID if already provided"""
        # If it's already just an ID (numeric string)
        if url_or_id.isdigit():
            return url_or_id
        
        # Try to extract from URL patterns
        patterns = [
            r'tiktok\.com/@[\w.-]+/video/(\d+)',
            r'tiktok\.com/v/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
            r'vt\.tiktok\.com/(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None
    
    async def analyze_single_video(self, video_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single video in detail"""
        try:
            api = await self.get_api_for_context(context)
            
            # Get video object handling both URLs and IDs
            video = await self.get_video_by_url_or_id(api, video_id)
            
            # Get full video info
            try:
                video_info = await video.info()
            except Exception as e:
                if "url" in str(e).lower():
                    # Try alternative approach - extract video info from URL
                    logger.info(f"Trying alternative video info retrieval for ID: {video_id}")
                    # If the ID approach doesn't work, we need the full URL
                    return {
                        "success": False,
                        "video_id": video_id,
                        "error": "Video URL Required",
                        "message": "Please provide the full TikTok video URL instead of just the ID",
                        "suggestions": [
                            "Use the full URL like: https://www.tiktok.com/@username/video/123456",
                            "Or use a short URL like: https://vm.tiktok.com/ABC123"
                        ]
                    }
                raise
            
            # Format the video data
            formatted_video = self.format_video_data(video_info)
            
            # Calculate engagement metrics
            stats = formatted_video["stats"]
            total_engagements = stats["likes"] + stats["comments"] + stats["shares"] + stats["saves"]
            engagement_rate = (total_engagements / stats["views"] * 100) if stats["views"] > 0 else 0
            
            # Virality score (simple heuristic based on engagement)
            virality_score = min(100, engagement_rate * 5)  # Scale engagement rate
            
            # Content analysis
            description = formatted_video["description"]
            hashtags = formatted_video["hashtags"]
            
            # Identify content characteristics
            characteristics = []
            if len(description) < 50:
                characteristics.append("short_caption")
            if len(hashtags) > 10:
                characteristics.append("hashtag_heavy")
            if stats["views"] > 1000000:
                characteristics.append("viral")
            if engagement_rate > 10:
                characteristics.append("high_engagement")
            
            return {
                "success": True,
                "video": formatted_video,
                "analysis": {
                    "engagement_rate": round(engagement_rate, 2),
                    "virality_score": round(virality_score, 2),
                    "total_engagements": total_engagements,
                    "characteristics": characteristics,
                    "performance_tier": self._get_performance_tier(stats["views"], engagement_rate)
                },
                "recommendations": self._generate_recommendations(formatted_video, engagement_rate)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video {video_id}: {e}")
            return {
                "success": False,
                "video_id": video_id,
                **self.format_error(e)
            }
    
    def _get_performance_tier(self, views: int, engagement_rate: float) -> str:
        """Categorize video performance"""
        if views > 10000000 and engagement_rate > 8:
            return "mega_viral"
        elif views > 1000000 and engagement_rate > 5:
            return "viral"
        elif views > 100000 and engagement_rate > 3:
            return "trending"
        elif views > 10000:
            return "moderate"
        else:
            return "emerging"
    
    def _generate_recommendations(self, video: Dict, engagement_rate: float) -> List[str]:
        """Generate content recommendations based on video analysis"""
        recommendations = []
        
        if engagement_rate > 10:
            recommendations.append("This content format is highly engaging - consider creating similar content")
        
        if len(video["hashtags"]) < 5:
            recommendations.append("Consider using more hashtags (5-10) to increase discoverability")
        
        if video["music"]["original"]:
            recommendations.append("Original sounds can help content go viral - great choice!")
        
        if video["stats"]["shares"] > video["stats"]["likes"] * 0.1:
            recommendations.append("High share rate indicates shareable content - focus on this style")
        
        return recommendations


# Create analyzer instances
_video_analyzer = VideoAnalyzer()


@tool
async def analyze_video(state: Dict[str, Any], video_url_or_id: str) -> Dict[str, Any]:
    """
    Analyze a specific TikTok video in detail to understand its performance and characteristics.
    
    Args:
        state: The current state containing user context
        video_url_or_id: TikTok video URL or video ID
        
    Returns:
        Dictionary containing detailed video analysis
    """
    # Extract user context from state
    user_context = state.get("user_context", {})
    
    # Check if we have a token for API call
    api_token = state.get("api_token") or os.environ.get("INTERNAL_API_TOKEN")
    
    if not api_token:
        # Fallback to direct analyzer call if no API token
        if not user_context or not user_context.get("user_id"):
            return {
                "success": False,
                "error": "Authentication Required",
                "message": "User context not found. Please ensure you're authenticated.",
                "action_required": "Sign in and configure your MS token"
            }
        
        video_id = _video_analyzer.extract_video_id(video_url_or_id)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid video URL or ID",
                "message": "Please provide a valid TikTok video URL or numeric video ID"
            }
        
        return await _video_analyzer.analyze_single_video(video_id, user_context)
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.analyze_video(api_token, video_url_or_id)


@tool
async def get_video_details(state: Dict[str, Any], video_url_or_id: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a TikTok video including all available fields.
    
    Args:
        state: The current state containing user context
        video_url_or_id: TikTok video URL or video ID
        
    Returns:
        Dictionary containing all video metadata
    """
    # Extract user context from state
    user_context = state.get("user_context", {})
    
    # Check if we have a token for API call
    api_token = state.get("api_token") or os.environ.get("INTERNAL_API_TOKEN")
    
    if not api_token:
        # Fallback to direct analyzer call if no API token
        if not user_context or not user_context.get("user_id"):
            return {
                "success": False,
                "error": "Authentication Required",
                "message": "User context not found. Please ensure you're authenticated.",
                "action_required": "Sign in and configure your MS token"
            }
        
        try:
            video_id = _video_analyzer.extract_video_id(video_url_or_id)
            if not video_id:
                return {
                    "success": False,
                    "error": "Invalid video URL or ID",
                    "message": "Please provide a valid TikTok video URL or numeric video ID"
                }
            
            api = await _video_analyzer.get_api_for_context(user_context)
            video = api.video(id=video_id)
            video_info = await video.info()
            
            return {
                "success": True,
                "video_id": video_id,
                "raw_data": video_info,
                "formatted_data": _video_analyzer.format_video_data(video_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting video details: {e}")
            return {
                "success": False,
                "video_id": video_url_or_id,
                **_video_analyzer.format_error(e)
            }
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.get_video_details(api_token, video_url_or_id)