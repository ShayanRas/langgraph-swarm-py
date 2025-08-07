"""TikTok API routes for direct access to analysis tools"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from src.api.models.tiktok import (
    TrendingRequest, TrendingResponse,
    HashtagRequest, HashtagResponse,
    VideoRequest, VideoResponse, VideoDetailsResponse,
    SearchRequest, SearchResponse,
    UserProfileRequest, UserProfileResponse
)
from src.auth import get_user_context, UserContext
from src.tools.tiktok.trending import TrendingAnalyzer
from src.tools.tiktok.hashtag import HashtagAnalyzer
from src.tools.tiktok.video import VideoAnalyzer
from src.tools.tiktok.search import ContentSearcher
from src.tools.tiktok.user import UserAnalyzer

# Create router
router = APIRouter(prefix="/tiktok", tags=["TikTok Analysis"])

# Initialize analyzers
trending_analyzer = TrendingAnalyzer()
hashtag_analyzer = HashtagAnalyzer()
video_analyzer = VideoAnalyzer()
content_searcher = ContentSearcher()
user_analyzer = UserAnalyzer()


@router.post("/analyze/trending", response_model=TrendingResponse)
async def analyze_trending(
    request: TrendingRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Analyze trending TikTok videos to identify viral patterns and popular content.
    
    This endpoint allows direct access to trending analysis without going through the chat interface.
    """
    try:
        # Convert user context to dict format expected by analyzer
        context_dict = user_context.to_config_dict()
        
        # Call the analyzer
        result = await trending_analyzer.get_trending_videos(
            request.count,
            context_dict
        )
        
        return TrendingResponse(**result)
        
    except Exception as e:
        return TrendingResponse(
            success=False,
            error=str(e),
            message="Failed to analyze trending videos"
        )


@router.post("/analyze/hashtag", response_model=HashtagResponse)
async def analyze_hashtag(
    request: HashtagRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Analyze a specific TikTok hashtag to understand its performance and content patterns.
    
    Provides insights on hashtag usage, top performing videos, and co-occurring hashtags.
    """
    try:
        context_dict = user_context.to_config_dict()
        
        result = await hashtag_analyzer.analyze_hashtag_content(
            request.hashtag,
            request.count,
            context_dict
        )
        
        return HashtagResponse(**result)
        
    except Exception as e:
        return HashtagResponse(
            success=False,
            hashtag=request.hashtag,
            error=str(e),
            message="Failed to analyze hashtag"
        )


@router.post("/analyze/video", response_model=VideoResponse)
async def analyze_video(
    request: VideoRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Analyze a specific TikTok video in detail to understand its performance and characteristics.
    
    Accepts either a TikTok video URL or video ID.
    """
    try:
        context_dict = user_context.to_config_dict()
        
        # Pass the full URL or ID to the analyzer
        # The analyzer will handle both URLs and IDs internally
        result = await video_analyzer.analyze_single_video(
            request.video_url_or_id,
            context_dict
        )
        
        return VideoResponse(**result)
        
    except Exception as e:
        return VideoResponse(
            success=False,
            error=str(e),
            message="Failed to analyze video"
        )


@router.post("/analyze/video/details", response_model=VideoDetailsResponse)
async def get_video_details(
    request: VideoRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Get comprehensive metadata for a TikTok video including all available fields.
    
    Returns both raw data from TikTok API and formatted data.
    """
    try:
        context_dict = user_context.to_config_dict()
        
        # Get API instance
        api = await video_analyzer.get_api_for_context(context_dict)
        
        # Get video object handling both URLs and IDs
        video = await video_analyzer.get_video_by_url_or_id(api, request.video_url_or_id)
        
        # Get full video info
        video_info = await video.info()
        
        # Extract video ID for response (optional, for backwards compatibility)
        video_id = video_analyzer.extract_video_id(request.video_url_or_id) or request.video_url_or_id
        
        return VideoDetailsResponse(
            success=True,
            video_id=video_id,
            raw_data=video_info,
            formatted_data=video_analyzer.format_video_data(video_info)
        )
        
    except Exception as e:
        return VideoDetailsResponse(
            success=False,
            video_id=request.video_url_or_id,
            error=str(e),
            message="Failed to get video details"
        )


@router.post("/search", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Search for TikTok videos by keyword or topic.
    
    Note: Due to API limitations, this uses hashtag search. For best results, use single-word queries.
    """
    try:
        context_dict = user_context.to_config_dict()
        
        result = await content_searcher.search_videos(
            request.query,
            request.count,
            context_dict
        )
        
        return SearchResponse(**result)
        
    except Exception as e:
        return SearchResponse(
            success=False,
            query=request.query,
            error=str(e),
            message="Failed to search content"
        )


@router.post("/analyze/user", response_model=UserProfileResponse)
async def analyze_user_profile(
    request: UserProfileRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """
    Analyze a TikTok user's profile, content strategy, and performance metrics.
    
    Provides insights on content patterns, engagement rates, and creator tier.
    """
    try:
        context_dict = user_context.to_config_dict()
        
        result = await user_analyzer.analyze_user(
            request.username,
            request.video_count,
            context_dict
        )
        
        return UserProfileResponse(**result)
        
    except Exception as e:
        return UserProfileResponse(
            success=False,
            username=request.username,
            error=str(e),
            message="Failed to analyze user profile"
        )


@router.get("/session/stats")
async def get_session_stats(
    user_context: UserContext = Depends(get_user_context)
):
    """
    Get statistics about TikTok sessions for monitoring and debugging.
    
    Shows active sessions, memory usage, and session health.
    """
    from src.tiktok.session_manager import get_session_manager
    
    session_manager = get_session_manager()
    stats = session_manager.get_session_stats()
    health = await session_manager.health_check()
    
    return {
        "stats": stats,
        "health": health,
        "user_id": user_context.user_id
    }