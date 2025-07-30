"""Test script to verify the swarm works"""
import asyncio
from src.swarm import app

async def test_swarm():
    """Test basic swarm functionality"""
    print("Testing TikTok Swarm...")
    
    # Test with Analysis Agent
    result = await app.ainvoke({
        "messages": [{"role": "user", "content": "Analyze this TikTok video: https://tiktok.com/example123"}]
    })
    
    print("\n=== Analysis Agent Response ===")
    print(f"Active Agent: {result.get('active_agent')}")
    print(f"Response: {result['messages'][-1]['content'][:200]}...")
    
    # Test handoff to Video Creation Agent
    result2 = await app.ainvoke({
        "messages": [{"role": "user", "content": "Now create a video based on trending dance content"}]
    }, {"configurable": {"thread_id": "test-thread"}})
    
    print("\n=== After Handoff ===")
    print(f"Active Agent: {result2.get('active_agent')}")
    print(f"Response: {result2['messages'][-1]['content'][:200]}...")

if __name__ == "__main__":
    print("Starting test...")
    asyncio.run(test_swarm())