"""Database configuration and setup utilities"""
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def get_database_url() -> str:
    """Get database URL from environment or use default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/tiktok_swarm"
    )

def get_base_connection_params() -> dict:
    """Extract connection parameters from DATABASE_URL"""
    url = get_database_url()
    # Parse PostgreSQL URL
    # Format: postgresql://user:password@host:port/database
    
    # Remove postgresql:// prefix
    conn_str = url.replace("postgresql://", "").replace("postgres://", "")
    
    # Split user:password@host:port/database
    if "@" in conn_str:
        auth, location = conn_str.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
        else:
            user, password = auth, ""
            
        if "/" in location:
            netloc, database = location.rsplit("/", 1)
        else:
            netloc, database = location, "tiktok_swarm"
            
        if ":" in netloc:
            host, port = netloc.rsplit(":", 1)
        else:
            host, port = netloc, "5432"
    else:
        # Handle local connections
        user = "postgres"
        password = ""
        host = "localhost"
        port = "5432"
        database = "tiktok_swarm"
    
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database
    }

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    params = get_base_connection_params()
    database_name = params.pop("database")
    
    try:
        # Connect to postgres database to create our database
        conn = psycopg2.connect(**params, database="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            print(f"Created database: {database_name}")
        else:
            print(f"Database already exists: {database_name}")
            
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        raise

async def setup_checkpointer_tables():
    """Setup tables required by AsyncPostgresSaver"""
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    
    try:
        checkpointer = AsyncPostgresSaver.from_conn_string(get_database_url())
        async with checkpointer:
            await checkpointer.setup()
        print("Checkpointer tables created successfully")
    except Exception as e:
        print(f"Error setting up checkpointer tables: {e}")
        raise

def setup_store_tables():
    """Setup tables required by PostgreSQL store"""
    import psycopg2
    
    conn_params = get_base_connection_params()
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    try:
        # Create store table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS langgraph_store (
                namespace TEXT[],
                key TEXT,
                value JSONB,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (namespace, key)
            );
            
            CREATE INDEX IF NOT EXISTS idx_store_namespace ON langgraph_store USING GIN(namespace);
            CREATE INDEX IF NOT EXISTS idx_store_updated_at ON langgraph_store(updated_at);
        """)
        
        conn.commit()
        print("Store tables created successfully")
        
    except Exception as e:
        print(f"Error setting up store tables: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

async def initialize_database():
    """Initialize all database components"""
    print("Initializing database...")
    
    # Create database if needed
    create_database_if_not_exists()
    
    # Setup checkpointer tables
    await setup_checkpointer_tables()
    
    # Setup store tables
    setup_store_tables()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    # Run initialization
    asyncio.run(initialize_database())