"""Test what's available in langgraph.prebuilt"""
try:
    import langgraph
    print(f"LangGraph version: {langgraph.__version__}")
    
    import langgraph.prebuilt
    print("\nAvailable in langgraph.prebuilt:")
    for attr in dir(langgraph.prebuilt):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    # Try to find InjectedState
    print("\nSearching for InjectedState...")
    
    # Check if it's in langgraph.prebuilt.tool_node
    try:
        from langgraph.prebuilt.tool_node import InjectedState
        print("✓ Found InjectedState in langgraph.prebuilt.tool_node")
    except ImportError as e:
        print(f"✗ Not in langgraph.prebuilt.tool_node: {e}")
    
    # Check if it's directly in langgraph.prebuilt
    try:
        from langgraph.prebuilt import InjectedState
        print("✓ Found InjectedState in langgraph.prebuilt")
    except ImportError as e:
        print(f"✗ Not in langgraph.prebuilt: {e}")
        
    # Check the actual module structure
    print("\nChecking langgraph.prebuilt.__all__:")
    if hasattr(langgraph.prebuilt, '__all__'):
        print(langgraph.prebuilt.__all__)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()