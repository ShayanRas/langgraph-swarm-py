#!/usr/bin/env python3
"""Smoke test to verify all critical imports work correctly.

This script is run during Docker build to catch missing dependencies early.
"""
import sys
import os

def test_imports():
    """Test all critical imports to ensure dependencies are installed."""
    errors = []
    
    # Test core imports
    try:
        import langgraph
        print("✓ langgraph imported successfully")
    except ImportError as e:
        errors.append(f"✗ Failed to import langgraph: {e}")
    
    try:
        import langgraph_swarm
        print("✓ langgraph_swarm imported successfully")
    except ImportError as e:
        errors.append(f"✗ Failed to import langgraph_swarm: {e}")
    
    try:
        from langchain_openai import ChatOpenAI
        print("✓ langchain_openai imported successfully")
    except ImportError as e:
        errors.append(f"✗ Failed to import langchain_openai: {e}")
    
    # Test Pydantic email validation
    try:
        from pydantic import EmailStr
        # Try to actually use EmailStr to ensure email-validator is installed
        from pydantic import BaseModel
        class TestModel(BaseModel):
            email: EmailStr
        # This will fail if email-validator is not installed
        TestModel(email="test@example.com")
        print("✓ Pydantic EmailStr working correctly")
    except ImportError as e:
        errors.append(f"✗ Failed to import/use EmailStr: {e}")
    except Exception as e:
        errors.append(f"✗ EmailStr validation error: {e}")
    
    # Test auth models
    try:
        from src.auth.models import AuthRequest, AuthResponse, UserInfo, UserContext
        print("✓ Auth models imported successfully")
    except ImportError as e:
        errors.append(f"✗ Failed to import auth models: {e}")
    
    # Test API app (skip if no API key during build)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from src.api.main import app
            print("✓ FastAPI app imported successfully")
        except ImportError as e:
            errors.append(f"✗ Failed to import FastAPI app: {e}")
        
        # Test swarm
        try:
            from src.swarm import get_app
            print("✓ Swarm configuration imported successfully")
        except ImportError as e:
            errors.append(f"✗ Failed to import swarm: {e}")
    else:
        print("⚠ Skipping API/Swarm import tests (no OPENAI_API_KEY during build)")
        print("  These will be validated at runtime when the container starts")
    
    # Test Supabase
    try:
        from supabase import create_client
        print("✓ Supabase client imported successfully")
    except ImportError as e:
        errors.append(f"✗ Failed to import supabase: {e}")
    
    return errors

if __name__ == "__main__":
    print("Running smoke tests...\n")
    
    errors = test_imports()
    
    if errors:
        print("\n❌ Smoke tests failed with the following errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("\n✅ All smoke tests passed!")
        sys.exit(0)