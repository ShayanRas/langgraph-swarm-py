"""Run the swarm locally without langgraph dev"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import and run our FastAPI app
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting TikTok Swarm API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\nPress CTRL+C to quit")
    
    # Try different host configurations
    # Use "127.0.0.1" for local only, "0.0.0.0" for all interfaces
    # Note: reload=True doesn't work when passing app directly, only with string import
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)