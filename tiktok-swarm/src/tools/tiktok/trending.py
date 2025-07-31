"""Tool for analyzing trending TikTok videos"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from .base import TikTokToolBase
import logging
import os

logger = logging.getLogger(__name__)


class TrendingAnalyzer(TikTokToolBase):
    """Handles trending video analysis"""
    
    async def get_trending_videos(self, count: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch and analyze trending videos"""
        try:
            api = await self.get_api_for_context(context)
            
            videos = []
            async for video in api.trending.videos(count=count):
                try:
                    video_data = self.format_video_data(video.as_dict)
                    videos.append(video_data)
                except Exception as e:
                    logger.warning(f"Failed to format video: {e}")
                    continue
            
            # Calculate trending insights
            total_views = sum(v["stats"]["views"] for v in videos)
            total_likes = sum(v["stats"]["likes"] for v in videos)
            avg_engagement = (total_likes / total_views * 100) if total_views > 0 else 0
            
            # Extract common hashtags
            all_hashtags = []
            for video in videos:
                all_hashtags.extend(video.get("hashtags", []))
            
            hashtag_counts = {}
            for tag in all_hashtags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "videos": videos,
                "insights": {
                    "total_videos": len(videos),
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "average_engagement_rate": round(avg_engagement, 2),
                    "top_hashtags": [{"hashtag": tag, "count": count} for tag, count in top_hashtags]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in trending analysis: {e}")
            return {
                "success": False,
                **self.format_error(e)
            }


# Create the tool instance
_analyzer = TrendingAnalyzer()


@tool
async def analyze_trending(state: Dict[str, Any], count: int = 10) -> Dict[str, Any]:
    """
    Analyze trending TikTok videos to identify viral patterns and popular content.
    
    NOTE: This tool requires a TikTok MS token to be configured for your account.
    
    Args:
        state: The current state containing user context
        count: Number of trending videos to analyze (max 30)
        
    Returns:
        Dictionary containing trending videos and insights
    """
    if count > 30:
        count = 30
    if count < 1:
        count = 10
    
    # Extract user context from state
    user_context = state.get("user_context", {})
    
    # Check if we have a token for API call
    # Note: In a real implementation, this token should come from the chat session
    # For now, we'll use a placeholder approach
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
        return await _analyzer.get_trending_videos(count, user_context)
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.analyze_trending(api_token, count)