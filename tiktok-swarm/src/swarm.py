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

# Import memory components
from langgraph.checkpoint.memory import MemorySaver
import asyncio

# In-memory components
async def create_app():
    """Create the swarm app with in-memory persistence"""
    # Create in-memory checkpointer for short-term memory
    checkpointer = MemorySaver()
    
    # Compile the swarm with in-memory checkpointer
    return builder.compile(checkpointer=checkpointer)

# Create the app
# Note: This is now an async operation
app = None

async def get_app():
    """Get or create the swarm app (async version)"""
    global app
    if app is None:
        app = await create_app()
    return app

# This is what langgraph.json references
__all__ = ["app"]