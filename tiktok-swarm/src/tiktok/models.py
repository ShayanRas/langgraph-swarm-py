"""Pydantic models for TikTok data"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TikTokStats(BaseModel):
    """Video statistics"""
    view_count: int = Field(alias="viewCount", default=0)
    like_count: int = Field(alias="likeCount", default=0)
    comment_count: int = Field(alias="commentCount", default=0)
    share_count: int = Field(alias="shareCount", default=0)
    save_count: int = Field(alias="saveCount", default=0)


class TikTokUser(BaseModel):
    """TikTok user/creator model"""
    id: str
    username: str = Field(alias="uniqueId")
    nickname: str
    avatar_url: Optional[str] = Field(alias="avatarThumb", default=None)
    follower_count: Optional[int] = Field(alias="followerCount", default=0)
    following_count: Optional[int] = Field(alias="followingCount", default=0)
    verified: bool = False
    signature: Optional[str] = None
    
    class Config:
        populate_by_name = True


class TikTokSound(BaseModel):
    """TikTok sound/music model"""
    id: str
    title: str
    author: Optional[str] = None
    duration: Optional[int] = None
    original: bool = False
    use_count: Optional[int] = Field(alias="useCount", default=0)
    
    class Config:
        populate_by_name = True


class TikTokHashtag(BaseModel):
    """TikTok hashtag model"""
    id: Optional[str] = None
    name: str
    view_count: Optional[int] = Field(alias="viewCount", default=0)
    use_count: Optional[int] = Field(alias="useCount", default=0)
    trending: bool = False
    
    class Config:
        populate_by_name = True


class TikTokVideo(BaseModel):
    """TikTok video model"""
    id: str
    url: Optional[str] = None
    create_time: Optional[datetime] = Field(alias="createTime", default=None)
    description: str = ""
    author: Optional[TikTokUser] = None
    sound: Optional[TikTokSound] = None
    hashtags: List[TikTokHashtag] = []
    stats: Optional[TikTokStats] = None
    duration: Optional[int] = None
    cover_url: Optional[str] = Field(alias="coverUrl", default=None)
    download_url: Optional[str] = Field(alias="downloadUrl", default=None)
    
    class Config:
        populate_by_name = True


class TikTokAnalysis(BaseModel):
    """Analysis result model"""
    video_id: str
    virality_score: float = Field(ge=0, le=100)
    engagement_rate: float
    trending_factors: List[str] = []
    content_category: Optional[str] = None
    optimal_posting_time: Optional[str] = None
    recommendations: List[str] = []
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)