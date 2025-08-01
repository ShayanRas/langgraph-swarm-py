# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two main components:
1. **langgraph-swarm**: A Python library for creating swarm-style multi-agent systems (root directory)
2. **tiktok-swarm**: A production application implementing TikTok analysis and video creation agents

## Development Commands

### Core Library (langgraph-swarm)

```bash
# Testing
make test                           # Run all tests with socket restrictions
make test TEST_FILE=tests/test_swarm.py::test_function_name  # Run specific test
make test_watch                     # Run tests in watch mode
uv run pytest --disable-socket --allow-unix-socket tests/  # Direct pytest

# Linting and Formatting
make lint                          # Run all linters (ruff, mypy)
make format                        # Auto-format code
make lint_diff                     # Check only changed files from master
make format_diff                   # Format only changed files from master

# Development
uv run ruff check langgraph_swarm/specific_file.py  # Check specific file
uv run ruff format langgraph_swarm/specific_file.py # Format specific file
uv run mypy langgraph_swarm/      # Type checking
```

### TikTok Swarm Application

```bash
# Local Development
cd tiktok-swarm
python run_local.py               # Run API server on port 7000

# Docker Development
docker-compose up                 # Run with all services
docker-compose down              # Stop all services
docker-compose up --build        # Rebuild and run

# LangGraph Studio
langgraph dev                    # Visual debugging interface

# API Testing
curl http://localhost:7000/      # Health check
curl -X POST http://localhost:7000/chat -H "Content-Type: application/json" -d '{"message": "test"}'
```

## Architecture Overview

### Core Swarm Library Architecture

The library implements a swarm-style multi-agent system where agents dynamically hand off control based on their specializations:

1. **SwarmState** (`langgraph_swarm/swarm.py:12-18`): 
   - Extends LangGraph's `MessagesState`
   - Tracks active agent via `active_agent` field
   - Maintains conversation history across all agents

2. **Handoff System** (`langgraph_swarm/handoff.py`):
   - `create_handoff_tool()` creates tools for agent-to-agent transfers
   - Uses LangGraph's `Command` system for state updates
   - Handoff destinations tracked via metadata

3. **Swarm Creation** (`langgraph_swarm/swarm.py`):
   - `create_swarm()` orchestrates multiple agents
   - `add_active_agent_router()` adds conditional routing
   - Automatically creates StateGraph with proper routing

### TikTok Swarm Architecture

The application demonstrates real-world usage with two specialized agents:

1. **Agent System** (`tiktok-swarm/src/agents/`):
   - **AnalysisAgent**: TikTok content analysis with stealth browser automation
   - **VideoCreationAgent**: Script and template generation
   - Automatic handoff based on task type

2. **TikTok Integration** (`tiktok-swarm/src/tiktok/`):
   - **SessionManager**: Manages browser sessions with anti-bot measures
   - **Stealth Features**: Playwright-stealth, browser rotation, proxy support
   - **Error Handling**: Comprehensive error classification and recovery

3. **API Layer** (`tiktok-swarm/src/api/`):
   - FastAPI with WebSocket support
   - Supabase authentication integration
   - Thread-based conversation management

## Key Implementation Patterns

### Agent Creation Pattern
```python
# 1. Create agents with handoff tools
alice = create_react_agent(model, [tool, create_handoff_tool("Bob")])
bob = create_react_agent(model, [create_handoff_tool("Alice")])

# 2. Create swarm
workflow = create_swarm([alice, bob], default_active_agent="Alice")

# 3. Compile with memory
app = workflow.compile(checkpointer=MemorySaver())
```

### Error Handling Pattern
All TikTok tools follow a consistent error handling pattern:
- Parse and classify errors (statusCode values)
- Preserve raw error messages
- Provide possible causes and suggestions
- Log with appropriate detail levels

### Stealth Configuration
TikTok operations support multiple stealth levels:
- `none`: No stealth features
- `moderate`: Basic anti-detection
- `aggressive`: Full stealth with human-like behavior
- `paranoid`: Maximum stealth with all features enabled

## Environment Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_key              # Required for all agents
```

### Optional TikTok Swarm Variables
```bash
# Supabase Authentication
SUPABASE_URL=https://project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# TikTok Configuration
TIKTOK_STEALTH_LEVEL=aggressive      # none|moderate|aggressive|paranoid
TIKTOK_HEADLESS=false               # Run browser in headed mode
TIKTOK_BROWSER=chromium             # chromium|firefox|webkit
MS_TOKEN_ENCRYPTION_KEY=your_key    # For token encryption

# Docker/Server
PORT=7000                           # API server port
```

## Docker Deployment

### Headed Browser Support
The Docker setup includes Xvfb for running headed browsers in containers:
- Automatically starts when `TIKTOK_HEADLESS=false`
- No GUI infrastructure needed on server
- Virtual display at :99

### Resource Requirements
- Memory: 2GB recommended (1GB minimum)
- CPU: 2 cores recommended
- Storage: ~2GB for browser binaries

## Testing Strategies

### Unit Tests
- Use `pytest` with socket restrictions for security
- Mock external services in tests
- Test files follow `test_*.py` naming convention

### Integration Testing
```bash
# Test authentication flow
cd tiktok-swarm
./test_auth_curl.sh

# Test TikTok endpoints
curl -X POST http://localhost:7000/api/tiktok/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cooking", "stealth_mode": true}'
```

## MCP Tool Integration

The swarm supports Model Context Protocol (MCP) tools:

```python
# Initialize MCP client
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "transport": "stdio"
    }
})

# Get tools and assign to agents
mcp_tools = await client.get_tools()
```

## Common Issues and Solutions

### Port Conflicts
- Default port changed to 7000 (from 8000)
- Configure via `PORT` environment variable
- Update docker-compose.yml port mappings

### TikTok Bot Detection
- Use aggressive or paranoid stealth mode
- Enable proxy support for IP rotation (see tiktok-swarm/PROXY_GUIDE.md)
- Implement retry logic with backoff
- Configure webshare or custom proxies via environment variables

### Memory Management
- Browser sessions auto-cleanup after timeout
- Configure `TIKTOK_MAX_SESSIONS_PER_USER`
- Monitor Docker container memory usage

## Extension Points

### Custom Agents
1. Create agent file in `src/agents/`
2. Implement with appropriate tools and handoffs
3. Add to swarm configuration in `src/swarm.py`

### Custom Tools
1. Inherit from `BaseTikTokTool` for TikTok operations
2. Implement `_execute` method with error handling
3. Register in agent tool list

### Authentication Providers
1. Implement provider in `src/auth/providers/`
2. Follow `BaseAuthProvider` interface
3. Add to auth configuration

## Code Style Guidelines

- Match existing patterns in the codebase
- Use type hints for all function signatures
- Follow error handling patterns (preserve details)
- Implement proper logging at appropriate levels
- Never commit secrets or API keys