"""Main swarm configuration for TikTok Analysis and Video Creation"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph_swarm import create_swarm
from src.agents.analysis_agent import create_analysis_agent
from src.agents.video_creation_agent import create_video_creation_agent

# Load environment variables
load_dotenv()

# Lazy initialization of components
model = None
analysis_agent = None
video_creation_agent = None
builder = None

def get_model():
    """Get or create the language model"""
    global model
    if model is None:
        # Check for API key before initialization
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment."
            )
        model = ChatOpenAI(
            model="gpt-4o-mini",  # Using a cost-effective model for development
            temperature=0.7
        )
    return model

def get_agents():
    """Get or create the agents"""
    global analysis_agent, video_creation_agent
    if analysis_agent is None or video_creation_agent is None:
        llm = get_model()
        analysis_agent = create_analysis_agent(llm)
        video_creation_agent = create_video_creation_agent(llm)
    return analysis_agent, video_creation_agent

def get_builder():
    """Get or create the swarm builder"""
    global builder
    if builder is None:
        agents = get_agents()
        builder = create_swarm(
            agents=list(agents),
            default_active_agent="AnalysisAgent"
        )
    return builder

# Import memory components
from langgraph.checkpoint.memory import MemorySaver
import asyncio

# In-memory components
async def create_app():
    """Create the swarm app with memory persistence"""
    # Create standard checkpointer (user isolation is handled via thread_id)
    checkpointer = MemorySaver()
    
    # Get the builder lazily
    swarm_builder = get_builder()
    
    # Compile the swarm with user-scoped checkpointer
    return swarm_builder.compile(checkpointer=checkpointer)

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