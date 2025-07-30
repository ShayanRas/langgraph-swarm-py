#!/usr/bin/env python3
"""Setup script to initialize PostgreSQL database for TikTok Swarm"""
import asyncio
import sys
from src.database.config import initialize_database

async def main():
    """Main setup function"""
    print("=== TikTok Swarm Database Setup ===")
    print()
    
    try:
        await initialize_database()
        print("\n✅ Database setup completed successfully!")
        print("\nYou can now run the application with:")
        print("  python run_local.py")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. The DATABASE_URL in .env is correct")
        print("3. You have the necessary database permissions")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())