"""Test conversation persistence"""
import requests
import json

BASE_URL = "http://localhost:8000"
THREAD_ID = "test-persistence-123"

def test_chat(message, expected_context=None):
    """Send a message and check the response"""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": message,
            "thread_id": THREAD_ID
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n{'='*60}")
        print(f"You: {message}")
        print(f"Agent ({data['active_agent']}): {data['response']}")
        
        # Check if context is maintained
        if expected_context:
            if expected_context.lower() in data['response'].lower():
                print("✓ Context maintained!")
            else:
                print("✗ Context lost!")
                
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

print("Testing conversation persistence...")
print("Thread ID:", THREAD_ID)

# Test 1: Initial message
test_chat("Hi! My name is Alex and I want to create TikTok videos about cooking.")

# Test 2: Check if the agent remembers the name
test_chat("What's my name?", expected_context="Alex")

# Test 3: Check if the agent remembers the topic
test_chat("What topic did I mention I want to create videos about?", expected_context="cooking")

# Test 4: Continue the conversation
test_chat("Can you analyze what cooking content is trending on TikTok?")

# Test 5: Switch agents and check if context is maintained
test_chat("Now create a video spec for a 30-second cooking video based on the trends")

print("\n" + "="*60)
print("Persistence test complete!")
print("\nTo verify persistence is working:")
print("1. The agent should remember your name (Alex)")
print("2. The agent should remember your topic (cooking)")
print("3. Context should be maintained across agent switches")