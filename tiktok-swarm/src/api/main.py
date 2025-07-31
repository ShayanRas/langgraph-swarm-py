"""FastAPI server for TikTok Swarm"""
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Import the swarm app getter
from src.swarm import get_app

# Initialize FastAPI
app = FastAPI(
    title="TikTok Swarm API",
    description="API for TikTok Analysis and Video Creation Swarm",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    active_agent: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    active_agent: str
    messages: List[Dict]

class StatusResponse(BaseModel):
    status: str
    version: str
    agents: List[str]

# In-memory storage for threads (replace with database later)
threads_store = {}

# Removed database setup for now - using in-memory storage
# @app.on_event("startup")
# async def startup_event():
#     """Initialize database on startup"""
#     await setup_database()

@app.get("/", response_model=StatusResponse)
async def root():
    """Health check and system status"""
    return StatusResponse(
        status="healthy",
        version="0.1.0",
        agents=["AnalysisAgent", "VideoCreationAgent"]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for interacting with the swarm"""
    try:
        # Generate or use existing thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Prepare the input
        swarm_input = {
            "messages": [{"role": "user", "content": request.message}]
        }
        
        # If active agent is specified, set it
        if request.active_agent:
            swarm_input["active_agent"] = request.active_agent
        
        # Create config with thread ID
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get the swarm app
        swarm_app = await get_app()
        
        # Invoke the swarm
        result = await asyncio.to_thread(
            swarm_app.invoke,
            swarm_input,
            config
        )
        
        # Store thread state
        threads_store[thread_id] = result
        
        # Extract the response
        messages = result.get("messages", [])
        
        # Convert message objects to dictionaries
        message_dicts = []
        for msg in messages:
            if hasattr(msg, 'content'):
                # It's a message object
                message_dicts.append({
                    "role": getattr(msg, 'type', 'assistant'),
                    "content": msg.content
                })
            else:
                # It's already a dictionary
                message_dicts.append(msg)
        
        # Get the last message content
        last_content = ""
        if message_dicts:
            last_content = message_dicts[-1].get("content", "No response")
        
        active_agent = result.get("active_agent", "AnalysisAgent")
        
        return ChatResponse(
            response=last_content,
            thread_id=thread_id,
            active_agent=active_agent,
            messages=message_dicts
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Get the state of a specific thread"""
    if thread_id not in threads_store:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return threads_store[thread_id]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    thread_id = str(uuid.uuid4())
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process the message
            swarm_input = {
                "messages": [{"role": "user", "content": data.get("message", "")}]
            }
            
            if data.get("active_agent"):
                swarm_input["active_agent"] = data["active_agent"]
            
            config = {"configurable": {"thread_id": thread_id}}
            
            # Get the swarm app
            swarm_app = await get_app()
            
            # Invoke the swarm
            result = await asyncio.to_thread(
                swarm_app.invoke,
                swarm_input,
                config
            )
            
            # Send response
            await websocket.send_json({
                "response": result.get("messages", [])[-1].get("content", ""),
                "active_agent": result.get("active_agent", "AnalysisAgent"),
                "thread_id": thread_id
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread {thread_id}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)