"""Tool for analyzing TikTok user profiles"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from .base import TikTokToolBase
import logging
import os
import re

logger = logging.getLogger(__name__)


class UserAnalyzer(TikTokToolBase):
    """Handles user profile analysis"""
    
    async def analyze_user(self, username: str, video_count: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a TikTok user's profile and content"""
        try:
            # Log the request
            logger.info(f"Analyzing user profile: {username} (video_count: {video_count})")
            
            api = await self.get_api_for_context(context)
            
            # Remove @ if present
            username = username.lstrip('@')
            
            # Basic username validation
            if not username or len(username) < 2:
                return {
                    "success": False,
                    "username": username,
                    "error": "Invalid Username",
                    "message": "Username must be at least 2 characters long"
                }
            
            # Check for invalid characters (TikTok usernames are alphanumeric with . and _)
            if not re.match(r'^[a-zA-Z0-9._]+$', username):
                return {
                    "success": False,
                    "username": username,
                    "error": "Invalid Username",
                    "message": "Username can only contain letters, numbers, dots, and underscores"
                }
            
            # Get user object
            user = api.user(username=username)
            
            # Get user info
            logger.debug(f"Fetching info for user: {username}")
            user_info = await user.info()
            logger.debug(f"Received user info for {username}: {bool(user_info)}")
            
            # Validate user data - handle multiple response structures
            if not user_info:
                logger.warning(f"Empty user info returned for {username}")
                return {
                    "success": False,
                    "username": username,
                    "error": "Invalid User Data",
                    "message": f"No data available for user '@{username}'"
                }
            
            # Check for successful API response
            if user_info.get("statusCode") == 0 or user_info.get("status_code") == 0:
                # Success response - check different possible structures
                user_data = (user_info.get("userInfo", {}).get("user") or 
                           user_info.get("user") or 
                           user_info.get("data", {}).get("user"))
                
                stats_data = (user_info.get("userInfo", {}).get("stats") or
                            user_info.get("stats") or
                            user_info.get("data", {}).get("stats"))
                
                if user_data:
                    # Restructure to expected format
                    user_info["user"] = user_data
                    if stats_data:
                        user_info["stats"] = stats_data
                else:
                    logger.warning(f"User data structure not recognized for {username}: {list(user_info.keys())}")
                    return {
                        "success": False,
                        "username": username,
                        "error": "Unexpected API Response",
                        "message": "User data returned in unexpected format",
                        "raw_response_keys": list(user_info.keys())
                    }
            elif not user_info.get("user"):
                logger.warning(f"No user field in response for {username}")
                return {
                    "success": False,
                    "username": username,
                    "error": "Invalid User Data",
                    "message": f"No data available for user '@{username}'"
                }
            
            # Get user's videos
            videos = []
            async for video in user.videos(count=video_count):
                try:
                    video_data = self.format_video_data(video.as_dict)
                    videos.append(video_data)
                except Exception as e:
                    logger.warning(f"Failed to format video: {e}")
                    continue
            
            if not videos:
                return {
                    "success": True,
                    "username": username,
                    "user_info": self._format_user_info(user_info),
                    "message": "User found but no public videos available",
                    "videos": []
                }
            
            # Calculate user performance metrics
            total_views = sum(v["stats"]["views"] for v in videos)
            total_likes = sum(v["stats"]["likes"] for v in videos)
            total_comments = sum(v["stats"]["comments"] for v in videos)
            total_shares = sum(v["stats"]["shares"] for v in videos)
            
            avg_views = total_views // len(videos) if videos else 0
            avg_likes = total_likes // len(videos) if videos else 0
            avg_engagement = ((total_likes + total_comments + total_shares) / total_views * 100) if total_views > 0 else 0
            
            # Find best performing content
            best_videos = sorted(videos, key=lambda x: x["stats"]["views"], reverse=True)[:5]
            
            # Analyze content patterns
            all_hashtags = []
            for video in videos:
                all_hashtags.extend(video.get("hashtags", []))
            
            hashtag_counts = {}
            for tag in all_hashtags:
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            favorite_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Content posting analysis
            content_categories = self._categorize_content(videos)
            
            return {
                "success": True,
                "username": username,
                "user_info": self._format_user_info(user_info),
                "content_analysis": {
                    "videos_analyzed": len(videos),
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "average_views_per_video": avg_views,
                    "average_likes_per_video": avg_likes,
                    "average_engagement_rate": round(avg_engagement, 2),
                    "content_categories": content_categories,
                    "favorite_hashtags": [
                        {"hashtag": tag, "usage_count": count} 
                        for tag, count in favorite_hashtags
                    ]
                },
                "performance_insights": {
                    "creator_tier": self._get_creator_tier(user_info, avg_views),
                    "content_consistency": self._analyze_consistency(videos),
                    "viral_ratio": sum(1 for v in videos if v["stats"]["views"] > 1000000) / len(videos) if videos else 0
                },
                "best_performing_videos": best_videos,
                "recent_videos": videos[:10]  # Most recent 10
            }
            
        except Exception as e:
            # Log detailed error information
            logger.error(f"Error analyzing user {username}: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full error traceback for {username}:", exc_info=True)
            
            # Format the error response with all details
            error_response = self.format_error(e)
            
            # Add username to the response
            return {
                "success": False,
                "username": username,
                **error_response
            }
    
    def _format_user_info(self, user_data: Dict) -> Dict[str, Any]:
        """Format user profile information - handle multiple response structures"""
        # Handle nested userInfo structure from API
        if "userInfo" in user_data:
            user_info = user_data["userInfo"]
            stats = user_info.get("stats", {}) or user_info.get("statsV2", {})
            user_detail = user_info.get("user", {})
        else:
            stats = user_data.get("stats", {}) or user_data.get("statsV2", {})
            user_detail = user_data.get("user", {})
        
        return {
            "id": user_detail.get("id"),
            "username": user_detail.get("uniqueId"),
            "nickname": user_detail.get("nickname"),
            "verified": user_detail.get("verified", False),
            "bio": user_detail.get("signature", ""),
            "avatar_url": user_detail.get("avatarLarger"),
            "stats": {
                "follower_count": stats.get("followerCount", 0),
                "following_count": stats.get("followingCount", 0),
                "video_count": stats.get("videoCount", 0),
                "heart_count": stats.get("heartCount", 0)  # Total likes received
            }
        }
    
    def _get_creator_tier(self, user_info: Dict, avg_views: int) -> str:
        """Categorize creator tier based on followers and performance"""
        stats = user_info.get("stats", {})
        followers = stats.get("followerCount", 0)
        
        if followers > 10000000:
            return "mega_influencer"
        elif followers > 1000000:
            return "macro_influencer"
        elif followers > 100000:
            return "mid_tier_influencer"
        elif followers > 10000:
            return "micro_influencer"
        elif followers > 1000:
            return "nano_influencer"
        else:
            return "emerging_creator"
    
    def _categorize_content(self, videos: List[Dict]) -> Dict[str, int]:
        """Categorize content types based on hashtags and descriptions"""
        categories = {
            "comedy": ["funny", "comedy", "joke", "humor", "meme"],
            "dance": ["dance", "dancing", "dancer", "choreo"],
            "education": ["learn", "education", "howto", "tutorial", "tips"],
            "lifestyle": ["life", "daily", "routine", "vlog", "day"],
            "food": ["food", "cooking", "recipe", "foodie", "eat"],
            "beauty": ["beauty", "makeup", "skincare", "hair"],
            "fitness": ["fitness", "workout", "gym", "exercise", "health"]
        }
        
        category_counts = {cat: 0 for cat in categories}
        
        for video in videos:
            text = (video.get("description", "") + " " + " ".join(video.get("hashtags", []))).lower()
            for category, keywords in categories.items():
                if any(keyword in text for keyword in keywords):
                    category_counts[category] += 1
        
        # Return only categories with content
        return {cat: count for cat, count in category_counts.items() if count > 0}
    
    def _analyze_consistency(self, videos: List[Dict]) -> str:
        """Analyze posting consistency"""
        if len(videos) < 5:
            return "insufficient_data"
        
        # Simple consistency check based on view variance
        views = [v["stats"]["views"] for v in videos]
        avg_views = sum(views) / len(views)
        variance = sum((v - avg_views) ** 2 for v in views) / len(views)
        std_dev = variance ** 0.5
        
        consistency_ratio = std_dev / avg_views if avg_views > 0 else 1
        
        if consistency_ratio < 0.5:
            return "highly_consistent"
        elif consistency_ratio < 1:
            return "moderately_consistent"
        else:
            return "variable_performance"


# Create the tool instance
_analyzer = UserAnalyzer()


@tool
async def analyze_user_profile(state: Dict[str, Any], username: str, video_count: int = 20) -> Dict[str, Any]:
    """
    Analyze a TikTok user's profile, content strategy, and performance metrics.
    
    Args:
        state: The current state containing user context
        username: TikTok username (with or without @)
        video_count: Number of recent videos to analyze (max 50)
        
    Returns:
        Dictionary containing user profile analysis and content insights
    """
    if video_count > 50:
        video_count = 50
    if video_count < 1:
        video_count = 20
    
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
        return await _analyzer.analyze_user(username, video_count, user_context)
    
    # Use API client to call endpoint
    from src.tools.api_client import TikTokAPIClient
    client = TikTokAPIClient()
    return await client.analyze_user_profile(api_token, username, video_count)