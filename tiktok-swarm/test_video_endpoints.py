#!/usr/bin/env python3
"""Test script for video analysis endpoints with full URLs"""
import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:7000"
TEST_VIDEO_URL = "https://www.tiktok.com/@khaby.lame/video/7363199420536532256"

async def test_video_analysis(token: str):
    """Test the video analysis endpoint"""
    print("\n=== Testing Video Analysis Endpoint ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tiktok/analyze/video",
            json={"video_url_or_id": TEST_VIDEO_URL},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("✅ Video analysis successful!")
            print(f"Video ID: {result.get('video', {}).get('id')}")
            print(f"Views: {result.get('video', {}).get('stats', {}).get('views'):,}")
            print(f"Engagement Rate: {result.get('analysis', {}).get('engagement_rate')}%")
            print(f"Performance Tier: {result.get('analysis', {}).get('performance_tier')}")
        else:
            print(f"❌ Video analysis failed: {result.get('error')}")
            print(f"Message: {result.get('message')}")
        
        return result

async def test_video_details(token: str):
    """Test the video details endpoint"""
    print("\n=== Testing Video Details Endpoint ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tiktok/analyze/video/details",
            json={"video_url_or_id": TEST_VIDEO_URL},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("✅ Video details retrieved successfully!")
            formatted = result.get("formatted_data", {})
            print(f"Video ID: {formatted.get('id')}")
            print(f"Description: {formatted.get('description', '')[:100]}...")
            print(f"Hashtags: {', '.join(formatted.get('hashtags', [])[:5])}")
            print(f"Duration: {formatted.get('duration')}s")
        else:
            print(f"❌ Video details failed: {result.get('error')}")
            print(f"Message: {result.get('message')}")
        
        return result

async def test_with_id_only(token: str):
    """Test with just video ID (extracted from URL)"""
    print("\n=== Testing with Video ID Only ===")
    
    # Extract ID from URL
    video_id = TEST_VIDEO_URL.split("/")[-1]
    print(f"Using ID: {video_id}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tiktok/analyze/video",
            json={"video_url_or_id": video_id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        result = response.json()
        
        if result.get("success"):
            print("✅ Analysis with ID successful!")
        else:
            print(f"❌ Analysis with ID failed: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            if result.get("suggestions"):
                print("Suggestions:")
                for suggestion in result.get("suggestions", []):
                    print(f"  - {suggestion}")

async def get_auth_token():
    """Get authentication token"""
    # You can modify this to get the token from environment or prompt
    import os
    token = os.environ.get("INTERNAL_API_TOKEN")
    if not token:
        token = input("Enter your API token: ").strip()
    return token

async def main():
    """Run all tests"""
    print("TikTok Video Analysis Test Suite")
    print("================================")
    print(f"Testing URL: {TEST_VIDEO_URL}")
    
    token = await get_auth_token()
    
    try:
        # Test video analysis
        await test_video_analysis(token)
        
        # Test video details
        await test_video_details(token)
        
        # Test with ID only (should fail and suggest using full URL)
        await test_with_id_only(token)
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())