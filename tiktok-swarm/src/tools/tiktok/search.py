"""Tool for searching TikTok content"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from .base import TikTokToolBase
import logging
import os

logger = logging.getLogger(__name__)


class ContentSearcher(TikTokToolBase):
    """Handles content search operations"""
    
    async def search_videos(self, query: str, count: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search for videos by keyword"""
        try:
            api = await self.get_api_for_context(context)
            
            # Try user search first (requires prior search history)
            search_worked = False
            videos = []
            
            try:
                # Attempt direct search
                logger.debug(f"Attempting direct search for: {query}")
                search_results = []
                async for user in api.search.users(query, count=1):
                    search_results.append(user)
                    search_worked = True
                    break
                
                if search_worked:
                    # If user search worked, we can try general search
                    logger.info(f"Search capability enabled, searching for: {query}")
                    # Note: The API doesn't have a direct video search, using hashtag approach
            except Exception as e:
                logger.debug(f"Direct search not available: {e}")
                search_worked = False
            
            # Fallback to hashtag search
            if not search_worked:
                logger.info("Using hashtag search as fallback")
            
            # Process query for hashtag search
            # Handle multi-word queries better
            hashtags_to_try = []
            
            # Try exact match first (remove spaces)
            hashtags_to_try.append(query.replace(" ", "").lower())
            
            # Try individual words as hashtags
            words = query.lower().split()
            hashtags_to_try.extend(words)
            
            # Try to find videos with these hashtags
            for hashtag_query in hashtags_to_try:
                if len(videos) >= count:
                    break
                    
                try:
                    hashtag = api.hashtag(name=hashtag_query)
                    remaining_count = count - len(videos)
                    
                    async for video in hashtag.videos(count=remaining_count):
                        try:
                            video_data = self.format_video_data(video.as_dict)
                            videos.append(video_data)
                        except Exception as e:
                            logger.warning(f"Failed to format video: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Hashtag '{hashtag_query}' search failed: {e}")
                    continue
            
            if not videos:
                return {
                    "success": True,
                    "query": query,
                    "message": f"No videos found for '{query}'. Try using trending hashtags or different keywords.",
                    "videos": [],
                    "suggestions": [
                        "Use single-word hashtags for better results",
                        "Try trending topics like: #cooking, #dance, #funny",
                        "Search functionality requires prior TikTok search history"
                    ]
                }
            
            # Analyze search results
            total_views = sum(v["stats"]["views"] for v in videos)
            avg_views = total_views // len(videos) if videos else 0
            
            # Sort by relevance (views for now)
            videos.sort(key=lambda x: x["stats"]["views"], reverse=True)
            
            return {
                "success": True,
                "query": query,
                "results_count": len(videos),
                "search_insights": {
                    "total_views": total_views,
                    "average_views": avg_views,
                    "top_creators": self._get_top_creators(videos),
                    "common_hashtags": self._get_common_hashtags(videos)
                },
                "videos": videos
            }
            
        except Exception as e:
            logger.error(f"Error in content search: {e}")
            return {
                "success": False,
                "query": query,
                **self.format_error(e)
            }
    
    def _get_top_creators(self, videos: List[Dict]) -> List[Dict]:
        """Extract top creators from search results"""
        creator_stats = {}
        for video in videos:
            author = video.get("author", {})
            username = author.get("username")
            if username:
                if username not in creator_stats:
                    creator_stats[username] = {
                        "username": username,
                        "nickname": author.get("nickname"),
                        "video_count": 0,
                        "total_views": 0
                    }
                creator_stats[username]["video_count"] += 1
                creator_stats[username]["total_views"] += video["stats"]["views"]
        
        # Sort by video count
        top_creators = sorted(creator_stats.values(), key=lambda x: x["video_count"], reverse=True)
        return top_creators[:5]
    
    def _get_common_hashtags(self, videos: List[Dict]) -> List[Dict]:
        """Extract common hashtags from search results"""
        hashtag_counts = {}
        for video in videos:
            for tag in video.get("hashtags", []):
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        common_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"hashtag": tag, "count": count} for tag, count in common_hashtags[:10]]


# Create the tool instance
_searcher = ContentSearcher()


@tool
async def search_content(state: Dict[str, Any], query: str, count: int = 20) -> Dict[str, Any]:
    """
    Search for TikTok videos by keyword or topic.
    
    Note: Due to API limitations, this uses hashtag search. For best results, use single-word queries.
    
    Args:
        state: The current state containing user context
        query: Search query (works best with single words/hashtags)
        count: Number of videos to return (max 50)
        
    Returns:
        Dictionary containing search results and insights
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
        return await _searcher.search_videos(query, count, user_context)
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.search_content(api_token, query, count)