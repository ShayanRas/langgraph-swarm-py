"""Main swarm configuration for TikTok Analysis and Video Creation"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.langgraph_swarm import create_swarm
from src.agents.analysis_agent import create_analysis_agent
from src.agents.video_creation_agent import create_video_creation_agent

# Load environment variables
load_dotenv()

# Initialize the language model
model = ChatOpenAI(
    model="gpt-4o-mini",  # Using a cost-effective model for development
    temperature=0.7
)

# Create the agents
analysis_agent = create_analysis_agent(model)
video_creation_agent = create_video_creation_agent(model)

# Create the swarm
builder = create_swarm(
    agents=[analysis_agent, video_creation_agent],
    default_active_agent="AnalysisAgent"
)

# Import database configuration
from src.database.config import get_database_url
import asyncio

# PostgreSQL-based memory components
async def create_app():
    """Create the swarm app with PostgreSQL persistence"""
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    
    # Create PostgreSQL checkpointer for short-term memory
    db_url = get_database_url()
    checkpointer = AsyncPostgresSaver.from_conn_string(db_url)
    
    # Note: PostgreSQL store is not yet available in langgraph
    # For now, we'll use checkpointer for persistence
    # Store functionality can be added when available
    
    # Compile the swarm with PostgreSQL checkpointer
    return builder.compile(checkpointer=checkpointer)

# Create the app
# Note: This is now an async operation
app = None

def get_app():
    """Get or create the swarm app"""
    global app
    if app is None:
        # Create event loop if needed and run async creation
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        app = loop.run_until_complete(create_app())
    return app

# This is what langgraph.json references
__all__ = ["app"]