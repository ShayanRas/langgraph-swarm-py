"""Analysis Agent for TikTok content analysis"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from src.langgraph_swarm import create_handoff_tool
from src.tools.mock_tools import (
    analyze_tiktok_url,
    analyze_trend,
    search_trending_sounds
)


def create_analysis_agent(model: ChatOpenAI):
    """
    Create the Analysis Agent with TikTok analysis capabilities.
    
    Args:
        model: The language model to use
        
    Returns:
        A configured analysis agent
    """
    # Create handoff tool for transferring to Video Creation Agent
    transfer_to_video_creation = create_handoff_tool(
        agent_name="VideoCreationAgent",
        description="Transfer the conversation to the Video Creation Agent to create video specifications based on the analysis"
    )
    
    # Define the agent's tools
    tools = [
        analyze_tiktok_url,
        analyze_trend,
        search_trending_sounds,
        transfer_to_video_creation
    ]
    
    # System prompt for the Analysis Agent
    system_prompt = """You are the Analysis Agent, specializing in TikTok content analysis and trend identification.

Your responsibilities include:
1. Analyzing TikTok videos to extract performance metrics and engagement data
2. Identifying trending hashtags, sounds, and content patterns
3. Providing insights on what makes content viral
4. Recommending content strategies based on data

When users want to create videos based on your analysis, transfer them to the Video Creation Agent.

Be data-driven in your responses and provide actionable insights. When you identify strong trends or viral patterns, proactively suggest creating content around them."""
    
    # Create and return the agent
    return create_react_agent(
        model,
        tools,
        prompt=system_prompt,
        name="AnalysisAgent"
    )