"""Memory tools for agents to store and retrieve long-term memories"""
from typing import Dict, Any, List
from src.memory.manager import memory_manager


def store_user_preference(user_id: str, preference_key: str, preference_value: Any) -> str:
    """
    Store a user preference for future conversations.
    
    Args:
        user_id: Unique identifier for the user
        preference_key: Type of preference (e.g., 'content_style', 'favorite_topics')
        preference_value: The preference data to store
        
    Returns:
        Success or failure message
    """
    success = memory_manager.store_user_preference(user_id, preference_key, preference_value)
    if success:
        return f"Successfully stored {preference_key} preference for user {user_id}"
    return f"Failed to store preference"


def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Retrieve all stored preferences for a user.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Dictionary of user preferences
    """
    return memory_manager.get_user_preferences(user_id)


def remember_trend(trend_type: str, trend_data: Dict[str, Any]) -> str:
    """
    Store trending data for future analysis.
    
    Args:
        trend_type: Category of trend (e.g., 'viral_sounds', 'popular_hashtags')
        trend_data: Information about the trend
        
    Returns:
        Success message
    """
    success = memory_manager.store_trend_data(trend_type, trend_data)
    if success:
        return f"Successfully stored {trend_type} trend data"
    return "Failed to store trend data"


def recall_recent_trends(trend_type: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve recent trends of a specific type.
    
    Args:
        trend_type: Category of trend to retrieve
        limit: Maximum number of trends to return
        
    Returns:
        List of recent trends
    """
    return memory_manager.get_recent_trends(trend_type, limit)


def save_video_template(template_name: str, template_data: Dict[str, Any]) -> str:
    """
    Save a successful video template for reuse.
    
    Args:
        template_name: Unique name for the template
        template_data: Template specifications including structure, timing, etc.
        
    Returns:
        Success message
    """
    success = memory_manager.store_video_template(template_name, template_data)
    if success:
        return f"Successfully saved video template: {template_name}"
    return "Failed to save template"


def find_video_templates(category: str = None) -> List[Dict[str, Any]]:
    """
    Find saved video templates, optionally by category.
    
    Args:
        category: Optional category filter
        
    Returns:
        List of video templates
    """
    return memory_manager.get_video_templates(category)


def search_memories(memory_type: str, search_term: str) -> List[Dict[str, Any]]:
    """
    Search through stored memories.
    
    Args:
        memory_type: Type of memory ('user_preferences', 'trends', 'video_templates')
        search_term: Text to search for
        
    Returns:
        List of matching memories
    """
    namespace_map = {
        'user_preferences': ['user_preferences'],
        'trends': ['trends'],
        'video_templates': ['video_templates']
    }
    
    namespace = namespace_map.get(memory_type, ['general'])
    return memory_manager.search_memory(namespace, search_term)