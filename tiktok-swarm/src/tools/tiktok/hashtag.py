"""Tool for analyzing TikTok hashtags"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from .base import TikTokToolBase
import logging
import os

logger = logging.getLogger(__name__)


class HashtagAnalyzer(TikTokToolBase):
    """Handles hashtag analysis"""
    
    async def analyze_hashtag_content(self, hashtag_name: str, count: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze videos under a specific hashtag"""
        try:
            api = await self.get_api_for_context(context)
            
            # Remove # if present
            hashtag_name = hashtag_name.lstrip('#')
            
            # Get hashtag object
            hashtag = api.hashtag(name=hashtag_name)
            
            # Get hashtag info
            hashtag_info = await hashtag.info()
            
            # Get videos with this hashtag
            videos = []
            async for video in hashtag.videos(count=count):
                try:
                    video_data = self.format_video_data(video.as_dict)
                    videos.append(video_data)
                except Exception as e:
                    logger.warning(f"Failed to format video: {e}")
                    continue
            
            if not videos:
                return {
                    "success": True,
                    "hashtag": hashtag_name,
                    "message": "No videos found for this hashtag",
                    "videos": []
                }
            
            # Calculate hashtag performance metrics
            total_views = sum(v["stats"]["views"] for v in videos)
            total_likes = sum(v["stats"]["likes"] for v in videos)
            total_comments = sum(v["stats"]["comments"] for v in videos)
            total_shares = sum(v["stats"]["shares"] for v in videos)
            
            avg_views = total_views // len(videos) if videos else 0
            avg_engagement = ((total_likes + total_comments + total_shares) / total_views * 100) if total_views > 0 else 0
            
            # Find top performing videos
            top_videos = sorted(videos, key=lambda x: x["stats"]["views"], reverse=True)[:5]
            
            # Extract co-occurring hashtags
            co_hashtags = {}
            for video in videos:
                for tag in video.get("hashtags", []):
                    if tag.lower() != hashtag_name.lower():
                        co_hashtags[tag] = co_hashtags.get(tag, 0) + 1
            
            top_co_hashtags = sorted(co_hashtags.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "hashtag": hashtag_name,
                "hashtag_info": {
                    "name": hashtag_info.get("title", hashtag_name),
                    "view_count": hashtag_info.get("stats", {}).get("viewCount", 0),
                    "video_count": hashtag_info.get("stats", {}).get("videoCount", 0)
                },
                "analysis": {
                    "videos_analyzed": len(videos),
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "average_views_per_video": avg_views,
                    "average_engagement_rate": round(avg_engagement, 2),
                    "top_co_occurring_hashtags": [
                        {"hashtag": tag, "count": count} 
                        for tag, count in top_co_hashtags
                    ]
                },
                "top_performing_videos": top_videos,
                "all_videos": videos
            }
            
        except Exception as e:
            logger.error(f"Error in hashtag analysis: {e}")
            return {
                "success": False,
                "hashtag": hashtag_name,
                **self.format_error(e)
            }


# Create the tool instance
_analyzer = HashtagAnalyzer()


@tool
async def analyze_hashtag(state: Dict[str, Any], hashtag: str, count: int = 20) -> Dict[str, Any]:
    """
    Analyze a specific TikTok hashtag to understand its performance and content patterns.
    
    Args:
        state: The current state containing user context
        hashtag: The hashtag to analyze (with or without #)
        count: Number of videos to analyze (max 50)
        
    Returns:
        Dictionary containing hashtag analysis and top videos
    """
    if count > 50:
        count = 50
    if count < 1:
        count = 20
    
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
        return await _analyzer.analyze_hashtag_content(hashtag, count, user_context)
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.analyze_hashtag(api_token, hashtag, count)