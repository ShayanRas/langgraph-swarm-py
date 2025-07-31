"""Fix for InjectedState import issue"""
from typing import Annotated, Any, TypeVar

# Create a dummy InjectedState type if it's not available
try:
    from langgraph.prebuilt import InjectedState
    print("InjectedState found in langgraph.prebuilt")
except ImportError:
    try:
        from langgraph.prebuilt.tool_node import InjectedState
        print("InjectedState found in langgraph.prebuilt.tool_node")
    except ImportError:
        # Create a type alias as a workaround
        # This is just a marker type for dependency injection
        InjectedState = TypeVar("InjectedState")
        print("Created InjectedState as TypeVar workaround")

# Export for use
__all__ = ["InjectedState"]