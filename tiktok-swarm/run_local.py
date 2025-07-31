"""Run the swarm locally without langgraph dev"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_environment():
    """Validate required environment variables at startup"""
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    
    missing_required = [var for var in required_vars if not os.environ.get(var)]
    missing_optional = [var for var in optional_vars if not os.environ.get(var)]
    
    if missing_required:
        print("❌ Missing required environment variables:")
        for var in missing_required:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        sys.exit(1)
    
    if missing_optional:
        print("⚠️  Missing optional environment variables:")
        for var in missing_optional:
            print(f"  - {var}")
        print("  Some features may not work without these\n")
    
    # Validate Supabase configuration if provided
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")
    
    if supabase_url and supabase_key:
        # Basic validation
        if not supabase_url.startswith("https://") or not ".supabase.co" in supabase_url:
            print("⚠️  Warning: SUPABASE_URL doesn't look valid")
            print(f"  Got: {supabase_url}")
            print("  Expected format: https://your-project.supabase.co")
        
        if len(supabase_key) < 100:  # Supabase keys are typically very long
            print("⚠️  Warning: SUPABASE_ANON_KEY seems too short")
            print("  Make sure you're using the anon/public key, not the service role key")
        else:
            print("✅ Supabase configuration detected")

# Now we can import and run our FastAPI app
if __name__ == "__main__":
    import uvicorn
    
    # Detect if running in Docker
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER', False)
    
    # Configuration
    host = "0.0.0.0" if in_docker else "127.0.0.1"
    port = int(os.environ.get("PORT", 8000))
    reload = not in_docker and os.environ.get("ENVIRONMENT", "development") == "development"
    
    # Validate environment before starting
    validate_environment()
    
    print("🚀 Starting TikTok Swarm API...")
    print(f"📍 API will be available at: http://{host}:{port}")
    print("📚 API docs at: http://localhost:8000/docs")
    if in_docker:
        print("🐳 Running in Docker container")
    print("\nPress CTRL+C to quit")
    
    # Run the application
    uvicorn.run(
        "src.api.main:app", 
        host=host, 
        port=port, 
        reload=reload,
        log_level=os.environ.get("LOG_LEVEL", "info").lower()
    )