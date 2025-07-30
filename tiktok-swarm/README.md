# TikTok Swarm - Analysis & Video Creation System

A two-agent swarm system that combines TikTok content analysis with automated video creation planning.

## Features

- **Analysis Agent**: Analyzes TikTok videos, trends, and engagement metrics
- **Video Creation Agent**: Creates video specifications and scripts based on insights
- **Agent Handoff**: Seamless transfer between agents based on task requirements
- **LangGraph Studio Support**: Visual debugging and interaction through LangGraph Studio
- **FastAPI Backend**: REST API and WebSocket support for real-time communication

## Setup

1. **Install Dependencies**
```bash
cd tiktok-swarm
pip install -e .
```

2. **Set Environment Variables**
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Run in LangGraph Studio Mode**
```bash
langgraph dev
```
Then open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

4. **Run the API Server**
```bash
uvicorn src.api.main:app --reload
```
The API will be available at http://localhost:8000

## API Endpoints

- `GET /` - Health check and system status
- `POST /chat` - Main chat endpoint
- `GET /threads/{thread_id}` - Get thread state
- `WebSocket /ws` - Real-time chat interface

## Testing the Swarm

### Using LangGraph Studio
1. Run `langgraph dev`
2. Open the Studio URL
3. Start a conversation with either agent
4. Test handoffs between agents

### Using the API
```bash
# Chat with the Analysis Agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Analyze this TikTok video: https://tiktok.com/example"}'

# Switch to Video Creation Agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create a video based on trending dance content", "active_agent": "VideoCreationAgent"}'
```

## Project Structure
```
tiktok-swarm/
├── src/
│   ├── agents/          # Agent definitions
│   ├── tools/           # Mock tools (to be replaced with real implementations)
│   ├── api/             # FastAPI server
│   └── swarm.py         # Main swarm configuration
├── langgraph.json       # LangGraph Studio configuration
└── pyproject.toml       # Project dependencies
```

## Next Steps
- Replace mock tools with real TikTok API integration
- Add database persistence
- Implement video rendering queue
- Add authentication and user management
- Create frontend interface