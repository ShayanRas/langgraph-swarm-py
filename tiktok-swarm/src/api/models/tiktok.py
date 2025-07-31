"""Request and response models for TikTok API endpoints"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


# Base request with stealth parameters
class StealthConfigRequest(BaseModel):
    """Base request model with optional stealth configuration"""
    stealth_mode: bool = Field(default=True, description="Enable stealth mode to avoid bot detection")
    browser_type: Optional[Literal["chromium", "webkit", "firefox"]] = Field(
        default=None, 
        description="Browser to use (default: random selection)"
    )
    headless: Optional[bool] = Field(default=None, description="Override headless mode (default: based on stealth level)")
    proxy_url: Optional[str] = Field(default=None, description="Proxy URL for requests (format: http://user:pass@host:port)")


# Request Models
class TrendingRequest(StealthConfigRequest):
    """Request model for analyzing trending videos"""
    count: int = Field(default=10, ge=1, le=30, description="Number of trending videos to analyze")


class HashtagRequest(StealthConfigRequest):
    """Request model for analyzing hashtag"""
    hashtag: str = Field(..., description="Hashtag to analyze (with or without #)")
    count: int = Field(default=20, ge=1, le=50, description="Number of videos to analyze")


class VideoRequest(StealthConfigRequest):
    """Request model for analyzing a video"""
    video_url_or_id: str = Field(..., description="TikTok video URL or video ID")


class SearchRequest(StealthConfigRequest):
    """Request model for searching content"""
    query: str = Field(..., description="Search query (works best with single words)")
    count: int = Field(default=20, ge=1, le=50, description="Number of results to return")


class UserProfileRequest(StealthConfigRequest):
    """Request model for analyzing user profile"""
    username: str = Field(..., description="TikTok username (with or without @)")
    video_count: int = Field(default=20, ge=1, le=50, description="Number of recent videos to analyze")


# Response Models (shared structures)
class TikTokUserInfo(BaseModel):
    """User information model"""
    username: str
    nickname: str
    verified: bool
    follower_count: int


class TikTokVideoStats(BaseModel):
    """Video statistics model"""
    views: int
    likes: int
    comments: int
    shares: int
    saves: int


class TikTokMusicInfo(BaseModel):
    """Music information model"""
    title: str
    author: str
    original: bool


class TikTokVideoInfo(BaseModel):
    """Video information model"""
    id: str
    description: str
    create_time: Optional[int] = None
    author: TikTokUserInfo
    stats: TikTokVideoStats
    music: TikTokMusicInfo
    hashtags: List[str]
    url: str


class TrendingInsights(BaseModel):
    """Insights from trending analysis"""
    total_videos: int
    total_views: int
    total_likes: int
    average_engagement_rate: float
    top_hashtags: List[Dict[str, Any]]


class TrendingResponse(BaseModel):
    """Response model for trending analysis"""
    success: bool
    videos: Optional[List[TikTokVideoInfo]] = None
    insights: Optional[TrendingInsights] = None
    error: Optional[str] = None
    message: Optional[str] = None
    action_required: Optional[str] = None


class HashtagInfo(BaseModel):
    """Hashtag information model"""
    name: str
    view_count: int
    video_count: int


class HashtagAnalysis(BaseModel):
    """Hashtag analysis results"""
    videos_analyzed: int
    total_views: int
    total_likes: int
    average_views_per_video: int
    average_engagement_rate: float
    top_co_occurring_hashtags: List[Dict[str, Any]]


class HashtagResponse(BaseModel):
    """Response model for hashtag analysis"""
    success: bool
    hashtag: str
    hashtag_info: Optional[HashtagInfo] = None
    analysis: Optional[HashtagAnalysis] = None
    top_performing_videos: Optional[List[TikTokVideoInfo]] = None
    all_videos: Optional[List[TikTokVideoInfo]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class VideoAnalysis(BaseModel):
    """Video analysis results"""
    engagement_rate: float
    virality_score: float
    total_engagements: int
    characteristics: List[str]
    performance_tier: str


class VideoResponse(BaseModel):
    """Response model for video analysis"""
    success: bool
    video: Optional[TikTokVideoInfo] = None
    analysis: Optional[VideoAnalysis] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class VideoDetailsResponse(BaseModel):
    """Response model for video details"""
    success: bool
    video_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    formatted_data: Optional[TikTokVideoInfo] = None
    error: Optional[str] = None
    message: Optional[str] = None


class SearchInsights(BaseModel):
    """Search results insights"""
    total_views: int
    average_views: int
    top_creators: List[Dict[str, Any]]
    common_hashtags: List[Dict[str, Any]]


class SearchResponse(BaseModel):
    """Response model for content search"""
    success: bool
    query: str
    results_count: Optional[int] = None
    search_insights: Optional[SearchInsights] = None
    videos: Optional[List[TikTokVideoInfo]] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class UserProfileInfo(BaseModel):
    """User profile information"""
    id: str
    username: str
    nickname: str
    verified: bool
    bio: str
    avatar_url: Optional[str] = None
    stats: Dict[str, int]


class ContentAnalysis(BaseModel):
    """User content analysis"""
    videos_analyzed: int
    total_views: int
    total_likes: int
    average_views_per_video: int
    average_likes_per_video: int
    average_engagement_rate: float
    content_categories: Dict[str, int]
    favorite_hashtags: List[Dict[str, Any]]


class PerformanceInsights(BaseModel):
    """User performance insights"""
    creator_tier: str
    content_consistency: str
    viral_ratio: float


class UserProfileResponse(BaseModel):
    """Response model for user profile analysis"""
    success: bool
    username: str
    user_info: Optional[UserProfileInfo] = None
    content_analysis: Optional[ContentAnalysis] = None
    performance_insights: Optional[PerformanceInsights] = None
    best_performing_videos: Optional[List[TikTokVideoInfo]] = None
    recent_videos: Optional[List[TikTokVideoInfo]] = None
    error: Optional[str] = None
    message: Optional[str] = None