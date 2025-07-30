# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
- Run all tests: `uv run pytest --disable-socket --allow-unix-socket tests/`
- Run specific test file: `uv run pytest --disable-socket --allow-unix-socket tests/test_swarm.py`
- Run tests in watch mode: `uv run ptw . -- tests/`
- Run a single test: `uv run pytest --disable-socket --allow-unix-socket tests/test_swarm.py::test_function_name`

### Linting and Formatting
- Run linters: `make lint`
- Format code: `make format`
- Check specific files: `uv run ruff check langgraph_swarm/file.py`
- Format specific files: `uv run ruff format langgraph_swarm/file.py`
- Type checking: `uv run mypy langgraph_swarm/`

### Development Setup
This project uses `uv` as the package manager. Key dependencies:
- Python >=3.10
- langgraph >=0.6.0,<0.7.0
- langchain-core >=0.3.40,<0.4.0

## Architecture Overview

### Core Components

The library implements a swarm-style multi-agent system where agents dynamically hand off control based on their specializations. The architecture consists of:

1. **SwarmState** (`langgraph_swarm/swarm.py:12-18`): 
   - Extends `MessagesState` from LangGraph
   - Tracks the currently active agent via `active_agent` field
   - Maintains conversation history across all agents

2. **Handoff Tools** (`langgraph_swarm/handoff.py`):
   - `create_handoff_tool()` creates tools that allow agents to transfer control
   - Uses LangGraph's `Command` system to update both message history and active agent
   - Tool names follow pattern: `transfer_to_<agent_name>`
   - Handoff destinations are tracked via metadata

3. **Swarm Creation** (`langgraph_swarm/swarm.py`):
   - `create_swarm()` orchestrates multiple agents into a unified system
   - `add_active_agent_router()` adds conditional routing based on active agent
   - Automatically creates a `StateGraph` with proper routing between agents

### Key Design Patterns

1. **Dynamic Agent Routing**: The swarm uses conditional edges from START to route to the active agent. If no agent is active, it defaults to the specified `default_active_agent`.

2. **State Preservation**: When agents hand off control, they:
   - Pass the full message history
   - Update the active agent in the state
   - Add a tool message confirming the handoff

3. **Flexible Agent Support**: Agents can be:
   - LangGraph `CompiledStateGraph` instances
   - Functional API workflows
   - Any `Pregel` object

4. **Memory Integration**: The swarm supports both short-term (checkpointer) and long-term (store) memory through LangGraph's compilation step.

### Example Usage Pattern
```python
# 1. Create agents with handoff tools
alice = create_react_agent(model, [tool, create_handoff_tool("Bob")], ...)
bob = create_react_agent(model, [create_handoff_tool("Alice")], ...)

# 2. Create swarm
workflow = create_swarm([alice, bob], default_active_agent="Alice")

# 3. Compile with memory
app = workflow.compile(checkpointer=InMemorySaver())
```

### Extension Points

1. **Custom Handoff Tools**: Override `create_handoff_tool()` to:
   - Add task descriptions for the next agent
   - Filter which messages to pass
   - Customize tool names/descriptions

2. **Custom Agent State**: Use different message keys per agent by:
   - Creating custom state schemas
   - Implementing state transformation wrappers
   - Using `add_active_agent_router()` manually

3. **Agent Discovery**: The `get_handoff_destinations()` function automatically discovers handoff connections by inspecting agent tool nodes.

## MCP (Model Context Protocol) Tool Integration

### Background
MCP (Model Context Protocol) is a standard for creating tool servers that can be consumed by AI agents. It allows you to:
- Create language-agnostic tool servers
- Run tools in isolated processes for security
- Dynamically load/unload tools at runtime
- Share tools across different AI systems

### Setting Up MCP Tools with Swarm Agents

#### 1. Install Required Dependencies
```bash
pip install langchain-mcp-adapters
```

#### 2. Basic MCP Integration
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

# Initialize MCP client with servers
async def setup_mcp_tools():
    client = MultiServerMCPClient({
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            "transport": "stdio"
        },
        "github": {
            "command": "npx", 
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "transport": "stdio",
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
        }
    })
    return await client.get_tools()

# Create agents with MCP tools
async def create_mcp_swarm():
    mcp_tools = await setup_mcp_tools()
    
    # Filter tools for each agent
    alice_tools = [t for t in mcp_tools if t.name.startswith("filesystem.")]
    alice_tools.append(create_handoff_tool("Bob"))
    
    alice = create_react_agent(
        model, alice_tools, 
        prompt="You are Alice with file system access.",
        name="Alice"
    )
    
    # Similar setup for other agents...
```

#### 3. Creating Custom MCP Servers
```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CustomTools")

@mcp.tool()
def custom_operation(param: str) -> str:
    """Perform a custom operation"""
    return f"Processed: {param}"

if __name__ == "__main__":
    mcp.run()
```

Then add to your MCP client configuration:
```python
"custom": {
    "command": "python",
    "args": ["./mcp_server.py"],
    "transport": "stdio"
}
```

#### 4. Advanced Pattern: Role-Based Tool Assignment
```python
class MCPToolRouter:
    """Assigns MCP tools based on agent roles"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.tool_categories = {
            "technical": ["filesystem", "code", "shell"],
            "data": ["database", "analytics"],
            "external": ["github", "slack", "web"]
        }
    
    async def get_tools_for_role(self, role: str):
        all_tools = await self.mcp_client.get_tools()
        if role in self.tool_categories:
            prefixes = self.tool_categories[role]
            return [t for t in all_tools 
                   if any(t.name.startswith(f"{p}.") for p in prefixes)]
        return []
```

### Common MCP Servers
- **Filesystem**: `@modelcontextprotocol/server-filesystem`
- **GitHub**: `@modelcontextprotocol/server-github`
- **PostgreSQL**: `@modelcontextprotocol/server-postgres`
- **Slack**: `@modelcontextprotocol/server-slack`
- **Google Drive**: `@modelcontextprotocol/server-gdrive`

### Best Practices
1. **Security**: Run MCP servers with minimal required permissions
2. **Error Handling**: Wrap MCP tool calls in try-catch blocks
3. **Tool Naming**: Use clear, descriptive names for custom MCP tools
4. **Documentation**: Document each MCP tool's purpose and parameters
5. **Testing**: Test MCP servers independently before integration