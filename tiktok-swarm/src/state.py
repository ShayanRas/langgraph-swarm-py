"""Custom state schema for TikTok Swarm with user context"""
from langgraph_swarm import SwarmState
from typing import Dict, Any, Optional


class TikTokSwarmState(SwarmState):
    """Extended state that includes user context for authentication."""
    user_context: Optional[Dict[str, Any]] = None