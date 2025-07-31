"""Analysis Agent for TikTok content analysis"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool
from src.tools.tiktok import (
    analyze_trending,
    analyze_hashtag,
    analyze_video,
    get_video_details,
    search_content,
    analyze_user_profile
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
        analyze_trending,
        analyze_hashtag,
        analyze_video,
        get_video_details,
        search_content,
        analyze_user_profile,
        transfer_to_video_creation
    ]
    
    # System prompt for the Analysis Agent
    system_prompt = """You are the Analysis Agent, specializing in TikTok content analysis and trend identification.

Your capabilities include:
1. **Trending Analysis**: Analyze current trending videos to identify viral patterns and popular content
2. **Hashtag Analysis**: Deep dive into hashtag performance, co-occurring tags, and content strategies
3. **Video Analysis**: Analyze individual videos for engagement metrics, virality scores, and success factors
4. **User Analysis**: Profile analysis of TikTok creators, their content strategy, and performance metrics
5. **Content Search**: Search for videos by topic (note: works best with single-word queries)
6. **Detailed Metadata**: Extract comprehensive video metadata including all available fields

Your responsibilities:
- Provide data-driven insights on TikTok trends and viral content patterns
- Analyze engagement rates, virality scores, and performance metrics
- Identify successful content strategies and recommend improvements
- Track hashtag performance and suggest optimal hashtag combinations
- Analyze creator profiles to understand content strategies

When users want to create videos based on your analysis, transfer them to the Video Creation Agent.

Important notes:
- All analysis requires the user to have configured their TikTok MS token
- Be specific with numbers and metrics in your analysis
- When you identify strong trends or viral patterns, proactively suggest creating content around them
- For video URLs, accept both full URLs and video IDs"""
    
    # Create and return the agent
    return create_react_agent(
        model,
        tools,
        prompt=system_prompt,
        name="AnalysisAgent"
    )