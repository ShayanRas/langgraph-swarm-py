"""State-aware tool wrapper for LangGraph integration"""
from functools import wraps
from typing import Callable, Any, Dict
import inspect
import logging

logger = logging.getLogger(__name__)


def state_aware_tool(func: Callable) -> Callable:
    """
    Wrapper to ensure tools receive state as first parameter.
    
    This handles the case where LangGraph might not automatically
    pass state to tool functions.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if function is async
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Tool {func.__name__} must be async")
        
        # Check if first argument looks like state
        if args and isinstance(args[0], dict):
            # Check for state indicators
            if any(key in args[0] for key in ["messages", "user_context", "active_agent"]):
                # Looks like state is already passed
                logger.debug(f"Tool {func.__name__} received state")
                return await func(*args, **kwargs)
        
        # State not passed, create minimal state
        logger.warning(
            f"Tool {func.__name__} called without state. "
            "This may indicate LangGraph integration issue."
        )
        
        # Create minimal state with empty context
        minimal_state = {
            "user_context": {},
            "messages": [],
            "active_agent": "Unknown"
        }
        
        # Call with minimal state prepended
        return await func(minimal_state, *args, **kwargs)
    
    # Preserve the original function's metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__
    
    return wrapper


def create_state_injected_tool(tool_func: Callable, state: Dict[str, Any]) -> Callable:
    """
    Create a version of a tool with state pre-injected.
    
    This is useful when you need to bind state at agent creation time.
    """
    @wraps(tool_func)
    async def injected_wrapper(*args, **kwargs):
        # Always inject our bound state as first argument
        return await tool_func(state, *args, **kwargs)
    
    # Update wrapper metadata
    injected_wrapper.__name__ = tool_func.__name__
    injected_wrapper.__doc__ = tool_func.__doc__
    
    # Update annotations to remove state parameter
    if hasattr(tool_func, '__annotations__'):
        new_annotations = tool_func.__annotations__.copy()
        # Remove 'state' from parameters if it exists
        new_annotations.pop('state', None)
        injected_wrapper.__annotations__ = new_annotations
    
    return injected_wrapper