"""Mock tools for testing the swarm system"""
from typing import Dict, List
import random
from datetime import datetime


def analyze_tiktok_url(url: str) -> Dict:
    """
    Mock tool to analyze a TikTok video URL.
    Returns mock analytics data for testing.
    
    Args:
        url: TikTok video URL to analyze
        
    Returns:
        Dictionary containing mock video analytics
    """
    return {
        "url": url,
        "title": f"Mock TikTok Video - {random.randint(1000, 9999)}",
        "views": random.randint(10000, 1000000),
        "likes": random.randint(1000, 100000),
        "shares": random.randint(100, 10000),
        "comments": random.randint(50, 5000),
        "engagement_rate": round(random.uniform(2.5, 15.0), 2),
        "trending_score": random.randint(60, 95),
        "hashtags": ["#fyp", "#viral", "#trend", "#mockdata"],
        "analyzed_at": datetime.now().isoformat()
    }


def analyze_trend(hashtag: str) -> Dict:
    """
    Mock tool to analyze a TikTok trend or hashtag.
    
    Args:
        hashtag: Hashtag to analyze (with or without #)
        
    Returns:
        Dictionary containing trend analysis
    """
    if not hashtag.startswith("#"):
        hashtag = f"#{hashtag}"
    
    return {
        "hashtag": hashtag,
        "total_views": random.randint(1000000, 100000000),
        "daily_growth": round(random.uniform(5.0, 25.0), 2),
        "top_creators": [f"creator_{i}" for i in range(1, 6)],
        "peak_posting_times": ["9:00 AM", "12:00 PM", "7:00 PM"],
        "trend_status": random.choice(["Rising", "Stable", "Peaking"]),
        "analyzed_at": datetime.now().isoformat()
    }


def create_video_spec(
    title: str,
    description: str,
    target_audience: str = "General",
    duration_seconds: int = 30
) -> Dict:
    """
    Mock tool to create a video specification.
    
    Args:
        title: Video title
        description: Video description or concept
        target_audience: Target audience for the video
        duration_seconds: Target video duration in seconds
        
    Returns:
        Dictionary containing video specification
    """
    return {
        "spec_id": f"SPEC-{random.randint(10000, 99999)}",
        "title": title,
        "description": description,
        "target_audience": target_audience,
        "duration_seconds": duration_seconds,
        "scenes": [
            {
                "scene_number": 1,
                "duration": 5,
                "type": "intro",
                "description": "Hook viewer with compelling opening"
            },
            {
                "scene_number": 2,
                "duration": duration_seconds - 10,
                "type": "main_content",
                "description": "Main content delivery"
            },
            {
                "scene_number": 3,
                "duration": 5,
                "type": "outro",
                "description": "Call to action and closing"
            }
        ],
        "recommended_music": ["Upbeat Pop Track", "Trending Audio #1"],
        "recommended_effects": ["Smooth Transitions", "Text Overlays"],
        "created_at": datetime.now().isoformat()
    }


def generate_script(video_spec_id: str, tone: str = "casual") -> Dict:
    """
    Mock tool to generate a video script based on specification.
    
    Args:
        video_spec_id: ID of the video specification
        tone: Tone of the script (casual, professional, humorous, etc.)
        
    Returns:
        Dictionary containing the generated script
    """
    return {
        "script_id": f"SCRIPT-{random.randint(10000, 99999)}",
        "video_spec_id": video_spec_id,
        "tone": tone,
        "script": {
            "intro": "Hey everyone! You won't believe what I discovered today...",
            "main_content": "Here's the thing that will blow your mind. [Main content goes here based on the video concept]",
            "outro": "If you found this helpful, don't forget to follow for more amazing content!"
        },
        "voiceover_notes": "Speak enthusiastically, maintain energy throughout",
        "caption_suggestions": [
            "Wait for it... 🤯",
            "This changed everything!",
            "Save this for later 📌"
        ],
        "created_at": datetime.now().isoformat()
    }


def search_trending_sounds() -> List[Dict]:
    """
    Mock tool to search for trending sounds on TikTok.
    
    Returns:
        List of trending sounds
    """
    sounds = []
    for i in range(5):
        sounds.append({
            "sound_id": f"SOUND-{random.randint(10000, 99999)}",
            "name": f"Trending Sound #{i+1}",
            "artist": f"Artist {i+1}",
            "usage_count": random.randint(10000, 1000000),
            "trend_score": random.randint(70, 99),
            "best_for": random.choice(["Dance", "Comedy", "Educational", "Lifestyle"])
        })
    return sounds