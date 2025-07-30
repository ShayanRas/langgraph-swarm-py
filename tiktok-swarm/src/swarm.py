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

# Compile the swarm into an app
app = builder.compile()

# This is what langgraph.json references
__all__ = ["app"]