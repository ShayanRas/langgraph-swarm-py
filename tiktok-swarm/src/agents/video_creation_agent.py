"""Video Creation Agent for creating video specifications and scripts"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from src.langgraph_swarm import create_handoff_tool
from src.tools.mock_tools import (
    create_video_spec,
    generate_script
)


def create_video_creation_agent(model: ChatOpenAI):
    """
    Create the Video Creation Agent with video planning capabilities.
    
    Args:
        model: The language model to use
        
    Returns:
        A configured video creation agent
    """
    # Create handoff tool for transferring to Analysis Agent
    transfer_to_analysis = create_handoff_tool(
        agent_name="AnalysisAgent",
        description="Transfer the conversation to the Analysis Agent to analyze TikTok content and trends"
    )
    
    # Define the agent's tools
    tools = [
        create_video_spec,
        generate_script,
        transfer_to_analysis
    ]
    
    # System prompt for the Video Creation Agent
    system_prompt = """You are the Video Creation Agent, specializing in creating engaging TikTok video specifications and scripts.

Your responsibilities include:
1. Creating detailed video specifications based on trends and user requirements
2. Generating engaging scripts optimized for TikTok's format
3. Planning scene structures and timing for maximum engagement
4. Recommending music, effects, and creative elements

When users need trend analysis or want to understand what's working on TikTok, transfer them to the Analysis Agent.

Focus on creating content that is:
- Attention-grabbing in the first 3 seconds
- Optimized for TikTok's algorithm
- Engaging and shareable
- Aligned with current trends

Always consider the target audience and the video's objective when creating specifications."""
    
    # Create and return the agent
    return create_react_agent(
        model,
        tools,
        prompt=system_prompt,
        name="VideoCreationAgent"
    )