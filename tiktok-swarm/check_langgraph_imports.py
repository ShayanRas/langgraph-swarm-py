"""Check what's actually available in langgraph modules"""
import sys
import os
# Fix Windows encoding issue
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
print(f"Python version: {sys.version}")

try:
    import langgraph
    try:
        print(f"\nLangGraph version: {langgraph.__version__}")
    except:
        print("\nLangGraph version: (no __version__ attribute)")
    
    print("\n1. Checking langgraph.prebuilt:")
    try:
        import langgraph.prebuilt
        print("[OK] langgraph.prebuilt exists")
        print("Available attributes:")
        for attr in dir(langgraph.prebuilt):
            if not attr.startswith('_'):
                print(f"  - {attr}")
    except Exception as e:
        print(f"[X] Error with langgraph.prebuilt: {e}")
    
    print("\n2. Checking specific imports:")
    # Check ToolNode
    locations = [
        "langgraph.prebuilt",
        "langgraph.prebuilt.tool_node", 
        "langgraph.prebuilt.tool",
        "langgraph.tools",
        "langgraph"
    ]
    
    for loc in locations:
        try:
            exec(f"from {loc} import ToolNode")
            print(f"[OK] Found ToolNode in {loc}")
            break
        except:
            print(f"[X] ToolNode not in {loc}")
    
    # Check create_react_agent
    for loc in locations:
        try:
            exec(f"from {loc} import create_react_agent")
            print(f"[OK] Found create_react_agent in {loc}")
            break
        except:
            print(f"[X] create_react_agent not in {loc}")
            
    # Try alternative imports
    print("\n3. Checking alternative locations:")
    try:
        from langgraph.prebuilt import create_react_agent
        print("[OK] create_react_agent is in langgraph.prebuilt")
    except:
        pass
        
    try:
        from langgraph.graph import MessagesState, StateGraph
        print("[OK] MessagesState and StateGraph are in langgraph.graph")
    except Exception as e:
        print(f"[X] Error importing from langgraph.graph: {e}")
        
    try:
        from langgraph.types import Command
        print("[OK] Command is in langgraph.types")
    except:
        print("[X] Command not in langgraph.types")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()