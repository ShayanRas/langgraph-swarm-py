"""Context management for TikTok tools in LangGraph"""
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variable to store user context during tool execution
_user_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('user_context', default=None)


def set_tool_context(context: Dict[str, Any]):
    """Set the user context for tool execution"""
    _user_context.set(context)


def get_tool_context() -> Dict[str, Any]:
    """Get the current user context"""
    context = _user_context.get()
    if context is None:
        # Try to get from thread-local storage as fallback
        return {}
    return context


class ToolContextManager:
    """Context manager for setting tool context"""
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.token = None
    
    def __enter__(self):
        self.token = _user_context.set(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            _user_context.reset(self.token)