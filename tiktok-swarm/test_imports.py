"""Test if all imports work correctly"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("\n1. Testing basic imports...")
    import fastapi
    print("✓ FastAPI imported")
    
    import uvicorn
    print("✓ Uvicorn imported")
    
    import langchain_openai
    print("✓ LangChain OpenAI imported")
    
    import dotenv
    print("✓ Dotenv imported")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

try:
    print("\n2. Testing LangGraph imports...")
    import langgraph
    print("✓ LangGraph imported")
    
    from langgraph.prebuilt import create_react_agent
    print("✓ create_react_agent imported")
    
except ImportError as e:
    print(f"✗ LangGraph import error: {e}")
    print("This might be a version issue with Python 3.13")

try:
    print("\n3. Testing local imports...")
    from src.tools.mock_tools import analyze_tiktok_url
    print("✓ Mock tools imported")
    
    from src.agents.analysis_agent import create_analysis_agent
    print("✓ Analysis agent imported")
    
    from src.agents.video_creation_agent import create_video_creation_agent
    print("✓ Video creation agent imported")
    
except ImportError as e:
    print(f"✗ Local import error: {e}")
    
print("\n4. Testing API imports...")
try:
    from src.api.main import app
    print("✓ FastAPI app imported successfully!")
    print("\nYou can run the API server with: python run_local.py")
except ImportError as e:
    print(f"✗ API import error: {e}")

print("\nImport test complete!")