"""FastAPI server for TikTok Swarm"""
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Import the swarm app getter
from src.swarm import get_app

# Import auth components
from src.auth import (
    AuthRequest, AuthResponse, UserInfo, UserContext,
    get_current_user, get_user_context, get_supabase_client
)
from src.auth.supabase_client import sign_in_with_password, sign_up, sign_out, refresh_token

# Additional imports
from typing import Union
from fastapi.responses import JSONResponse, HTMLResponse

# Initialize FastAPI
app = FastAPI(
    title="TikTok Swarm API",
    description="API for TikTok Analysis and Video Creation Swarm with Multi-User Support",
    version="0.2.0"
)

# Add CORS middleware with proper auth header support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "authorization"],
    expose_headers=["*"]  # Expose headers for client access
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

class ThreadInfo(BaseModel):
    thread_id: str
    user_id: str
    created_at: datetime
    last_updated: datetime
    message_count: int
    active_agent: str

class ListThreadsResponse(BaseModel):
    user_id: str
    threads: List[ThreadInfo]
    total_count: int

class StatusResponse(BaseModel):
    status: str
    version: str
    agents: List[str]

# In-memory storage for threads organized by user
# Structure: {user_id: {thread_id: thread_data}}
threads_store = defaultdict(dict)
thread_metadata = defaultdict(dict)

# Helper function to create thread metadata
def create_thread_metadata(user_id: str, thread_id: str, active_agent: str = "AnalysisAgent") -> Dict:
    return {
        "thread_id": thread_id,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
        "message_count": 0,
        "active_agent": active_agent
    }

# Helper function to update thread metadata
def update_thread_metadata(user_id: str, thread_id: str, message_count_increment: int = 1, active_agent: Optional[str] = None):
    if user_id in thread_metadata and thread_id in thread_metadata[user_id]:
        thread_metadata[user_id][thread_id]["last_updated"] = datetime.utcnow()
        thread_metadata[user_id][thread_id]["message_count"] += message_count_increment
        if active_agent:
            thread_metadata[user_id][thread_id]["active_agent"] = active_agent

@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation and usage examples"""
    return """
    <html>
    <head>
        <title>TikTok Swarm API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            h1 { color: #333; }
            h2 { color: #666; }
            h3 { color: #888; }
            .endpoint { margin: 20px 0; }
            .note { color: #ff6b6b; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>🚀 TikTok Swarm API</h1>
        <p>Multi-agent system for TikTok analysis and video creation</p>
        
        <h2>📚 Quick Links</h2>
        <ul>
            <li><a href="/docs">Interactive API Documentation (Swagger UI)</a></li>
            <li><a href="/redoc">Alternative API Documentation (ReDoc)</a></li>
        </ul>
        
        <h2>🔐 Authentication</h2>
        
        <div class="endpoint">
            <h3>1. Sign Up</h3>
            <pre>
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "redirect_to": "http://localhost:8000/auth/confirm"  // Optional
}

Response (Email Confirmation Required):
{
  "status": "pending_confirmation",
  "message": "Success! Please check your email to confirm your account.",
  "user_id": "uuid",
  "email": "user@example.com",
  "requires_email_confirmation": true
}

Response (Immediate Login - if email confirmation disabled):
{
  "status": "confirmed",
  "access_token": "eyJ...",
  "refresh_token": "...",
  "expires_in": 3600,
  "user": {...}
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>2. Email Confirmation</h3>
            <pre>
GET /auth/confirm?token_hash={token}&type=signup&next=/

This endpoint handles email confirmation links from Supabase.
Users are automatically redirected here when they click the confirmation link.
</pre>
        </div>
        
        <div class="endpoint">
            <h3>3. Resend Confirmation</h3>
            <pre>
GET /auth/resend-confirmation  // Shows form page

POST /auth/resend-confirmation
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "dummy"  // Required by API but not used
}

Response:
{
  "message": "Confirmation email sent! Please check your inbox.",
  "email": "user@example.com"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>4. Sign In</h3>
            <pre>
POST /auth/signin
Content-Type: application/json

{
  "email": "user@example.com", 
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "expires_in": 3600,
  "user": {...}
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>5. Use Protected Endpoints</h3>
            <pre>
POST /chat
Authorization: Bearer eyJ...your-access-token...
Content-Type: application/json

{
  "message": "Analyze trending cooking videos",
  "thread_id": "optional-thread-id",
  "active_agent": "AnalysisAgent"
}</pre>
        </div>
        
        <h2>🧪 Test Endpoints</h2>
        <ul>
            <li><a href="/test/health">Health Check (No Auth Required)</a></li>
            <li><a href="/test/protected">Protected Endpoint (Auth Required)</a></li>
        </ul>
        
        <h2>📝 Notes</h2>
        <p class="note">⚠️ Email confirmation may be required depending on Supabase configuration</p>
        <p class="note">⚠️ Access tokens expire after 1 hour by default</p>
        
        <h2>🚀 Status</h2>
        <p>API Status: <strong>Healthy</strong></p>
        <p>Version: <strong>0.2.0</strong></p>
        <p>Available Agents: <strong>AnalysisAgent, VideoCreationAgent</strong></p>
    </body>
    </html>
    """

@app.get("/status", response_model=StatusResponse)
async def status():
    """Health check and system status (JSON)"""
    return StatusResponse(
        status="healthy",
        version="0.2.0",
        agents=["AnalysisAgent", "VideoCreationAgent"]
    )

# Extended auth request for signup with redirect
class SignupRequest(AuthRequest):
    redirect_to: Optional[str] = None

# Authentication endpoints
@app.post("/auth/signup", response_model=Union[AuthResponse, Dict])
async def signup(request: SignupRequest):
    """Sign up a new user"""
    try:
        result = await sign_up(
            email=request.email, 
            password=request.password,
            redirect_to=request.redirect_to
        )
        
        # Handle email confirmation case
        if result.get("status") == "pending_confirmation":
            return JSONResponse(
                status_code=201,
                content=result
            )
        
        # Handle immediate login case
        if result.get("status") == "confirmed":
            # Remove status field for AuthResponse compatibility
            result.pop("status", None)
            return AuthResponse(**result)
        
        # Fallback
        return JSONResponse(status_code=201, content=result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during signup")

@app.post("/auth/signin", response_model=AuthResponse)
async def signin(request: AuthRequest):
    """Sign in an existing user"""
    try:
        result = await sign_in_with_password(request.email, request.password)
        return AuthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/signout")
async def signout(user: UserInfo = Depends(get_current_user)):
    """Sign out the current user"""
    try:
        # Note: In a real app, you might want to invalidate the token server-side
        return {"message": "Successfully signed out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/refresh", response_model=AuthResponse)
async def refresh_access_token(refresh_token_str: str):
    """Refresh access token using refresh token"""
    try:
        result = await refresh_token(refresh_token_str)
        return AuthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/auth/me", response_model=UserInfo)
async def get_me(user: UserInfo = Depends(get_current_user)):
    """Get current user information"""
    return user

@app.get("/auth/confirm")
async def confirm_email(
    token_hash: str = Query(..., description="Confirmation token from email"),
    type: str = Query("signup", description="Confirmation type"), 
    next: str = Query("/", description="Redirect URL after confirmation")
):
    """Handle email confirmation links from Supabase"""
    try:
        client = get_supabase_client()
        
        # Exchange the token_hash for a session
        response = client.auth.verify_otp({
            "token_hash": token_hash,
            "type": type
        })
        
        if response.session:
            # Email confirmed successfully
            return HTMLResponse(f"""
            <html>
            <head>
                <title>Email Confirmed - TikTok Swarm</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                    .success {{ color: #4CAF50; }}
                    .redirect {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <h1 class="success">✅ Email Confirmed!</h1>
                <p>Your email has been successfully verified.</p>
                <p>You can now sign in to your account.</p>
                <div class="redirect">
                    <p>Redirecting to: <a href="{next}">{next}</a></p>
                    <script>
                        setTimeout(() => window.location.href = '{next}', 3000);
                    </script>
                </div>
            </body>
            </html>
            """)
        else:
            raise ValueError("Invalid or expired confirmation token")
            
    except Exception as e:
        # Error page
        return HTMLResponse(f"""
        <html>
        <head>
            <title>Confirmation Error - TikTok Swarm</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .error {{ color: #f44336; }}
                .retry {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1 class="error">❌ Confirmation Failed</h1>
            <p>We couldn't confirm your email address.</p>
            <p>Error: {str(e)}</p>
            <div class="retry">
                <p>This could happen if:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>The confirmation link has expired</li>
                    <li>The link has already been used</li>
                    <li>The link is invalid</li>
                </ul>
                <p><a href="/auth/resend-confirmation">Request a new confirmation email</a></p>
            </div>
        </body>
        </html>
        """, status_code=400)

@app.get("/auth/resend-confirmation", response_class=HTMLResponse)
async def resend_confirmation_page():
    """Display resend confirmation form"""
    return HTMLResponse("""
    <html>
    <head>
        <title>Resend Confirmation - TikTok Swarm</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px auto; max-width: 500px; }
            form { display: flex; flex-direction: column; gap: 15px; }
            input { padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; }
            button { padding: 10px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .error { color: #dc3545; margin-top: 10px; display: none; }
            .success { color: #28a745; margin-top: 10px; display: none; }
        </style>
    </head>
    <body>
        <h1>Resend Email Confirmation</h1>
        <p>Enter your email address to receive a new confirmation link.</p>
        
        <form id="resendForm">
            <input type="email" id="email" placeholder="your@email.com" required>
            <button type="submit">Send Confirmation Email</button>
        </form>
        
        <div id="error" class="error"></div>
        <div id="success" class="success"></div>
        
        <script>
            document.getElementById('resendForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const errorDiv = document.getElementById('error');
                const successDiv = document.getElementById('success');
                
                // Hide previous messages
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/auth/resend-confirmation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: email, password: 'dummy' })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        successDiv.textContent = data.message || 'Confirmation email sent!';
                        successDiv.style.display = 'block';
                        document.getElementById('resendForm').reset();
                    } else {
                        errorDiv.textContent = data.detail || 'Failed to send confirmation email';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Network error. Please try again.';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """)

@app.post("/auth/resend-confirmation")
async def resend_confirmation(request: AuthRequest):
    """Resend email confirmation link"""
    try:
        client = get_supabase_client()
        
        # Resend confirmation email
        response = client.auth.resend({
            "type": "signup",
            "email": request.email,
            "options": {
                "emailRedirectTo": f"{os.getenv('APP_URL', 'http://localhost:8000')}/auth/confirm"
            }
        })
        
        return JSONResponse({
            "message": "Confirmation email sent! Please check your inbox.",
            "email": request.email
        })
        
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="Email not found. Please sign up first.")
        elif "already confirmed" in error_msg:
            raise HTTPException(status_code=400, detail="Email is already confirmed. Please sign in.")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to resend confirmation: {str(e)}")

# Test endpoints
@app.get("/test/health")
async def test_health():
    """Test endpoint - no auth required"""
    return {
        "status": "ok", 
        "auth_required": False,
        "timestamp": datetime.utcnow().isoformat(),
        "supabase_configured": bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"))
    }

@app.get("/test/protected")
async def test_protected(user: UserInfo = Depends(get_current_user)):
    """Test endpoint - auth required"""
    return {
        "status": "ok", 
        "auth_required": True,
        "user_id": user.id, 
        "email": user.email,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_context: UserContext = Depends(get_user_context)
):
    """Main chat endpoint for interacting with the swarm"""
    try:
        user_id = user_context.user_id
        
        # Generate thread_id with user context if not provided
        if request.thread_id:
            thread_id = request.thread_id
        else:
            thread_id = f"user_{user_id}_thread_{uuid.uuid4().hex[:8]}"
        
        # Create thread metadata if this is a new thread
        if user_id not in thread_metadata or thread_id not in thread_metadata[user_id]:
            thread_metadata[user_id][thread_id] = create_thread_metadata(
                user_id, 
                thread_id, 
                request.active_agent or "AnalysisAgent"
            )
        
        # Prepare the input
        swarm_input = {
            "messages": [{"role": "user", "content": request.message}]
        }
        
        # If active agent is specified, set it
        if request.active_agent:
            swarm_input["active_agent"] = request.active_agent
        
        # Create config with thread ID and user context
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            },
            "user_context": user_context.to_config_dict()
        }
        
        # Get the swarm app
        swarm_app = await get_app()
        
        # Invoke the swarm
        result = await asyncio.to_thread(
            swarm_app.invoke,
            swarm_input,
            config
        )
        
        # Store thread state organized by user
        threads_store[user_id][thread_id] = result
        
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
        
        # Update thread metadata
        update_thread_metadata(user_id, thread_id, 1, active_agent)
        
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

@app.get("/threads", response_model=ListThreadsResponse)
async def list_user_threads(
    limit: int = 50, 
    offset: int = 0,
    user_context: UserContext = Depends(get_user_context)
):
    """List all threads for the authenticated user"""
    try:
        user_id = user_context.user_id
        # Get all threads for the user
        user_threads = thread_metadata.get(user_id, {})
        
        # Convert to list and sort by last_updated (most recent first)
        threads_list = list(user_threads.values())
        threads_list.sort(key=lambda x: x["last_updated"], reverse=True)
        
        # Apply pagination
        total_count = len(threads_list)
        paginated_threads = threads_list[offset:offset + limit]
        
        # Convert to ThreadInfo objects
        thread_infos = [ThreadInfo(**thread) for thread in paginated_threads]
        
        return ListThreadsResponse(
            user_id=user_id,
            threads=thread_infos,
            total_count=total_count
        )
    except Exception as e:
        print(f"Error listing threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    user_context: UserContext = Depends(get_user_context)
):
    """Get the state of a specific thread for the authenticated user"""
    user_id = user_context.user_id
    # Check if user has access to this thread
    if user_id not in threads_store or thread_id not in threads_store[user_id]:
        raise HTTPException(status_code=404, detail="Thread not found or access denied")
    
    # Get thread data
    thread_data = threads_store[user_id][thread_id]
    metadata = thread_metadata.get(user_id, {}).get(thread_id, {})
    
    # Combine thread data with metadata
    return {
        "thread_data": thread_data,
        "metadata": metadata
    }

@app.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    user_context: UserContext = Depends(get_user_context)
):
    """Delete a specific thread for the authenticated user"""
    user_id = user_context.user_id
    # Check if thread exists
    if user_id not in threads_store or thread_id not in threads_store[user_id]:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Delete thread data
    del threads_store[user_id][thread_id]
    if user_id in thread_metadata and thread_id in thread_metadata[user_id]:
        del thread_metadata[user_id][thread_id]
    
    # Clean up empty user entries
    if not threads_store[user_id]:
        del threads_store[user_id]
    if user_id in thread_metadata and not thread_metadata[user_id]:
        del thread_metadata[user_id]
    
    return {"message": "Thread deleted successfully"}

class WebSocketRequest(BaseModel):
    message: str
    active_agent: Optional[str] = None
    token: Optional[str] = None  # JWT token for auth

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    thread_id = None
    user_context = None
    
    try:
        # First message should contain authentication token
        initial_data = await websocket.receive_json()
        token = initial_data.get("token")
        
        if not token:
            await websocket.send_json({"error": "Authentication token is required"})
            await websocket.close()
            return
        
        # Verify token and get user context
        try:
            from src.auth.supabase_client import verify_jwt_token, create_user_info
            user = await verify_jwt_token(token)
            user_info = create_user_info(user)
            user_context = UserContext(
                user_id=user_info.id,
                email=user_info.email,
                permissions=user_info.app_metadata.get("permissions", []),
                metadata=user_info.user_metadata
            )
        except Exception as e:
            await websocket.send_json({"error": "Invalid authentication token"})
            await websocket.close()
            return
        
        user_id = user_context.user_id
        
        # Generate thread_id for this session
        thread_id = f"user_{user_id}_thread_{uuid.uuid4().hex[:8]}"
        
        # Create thread metadata
        thread_metadata[user_id][thread_id] = create_thread_metadata(
            user_id, 
            thread_id, 
            initial_data.get("active_agent", "AnalysisAgent")
        )
        
        # Send initial acknowledgment
        await websocket.send_json({
            "type": "connection_established",
            "thread_id": thread_id,
            "user_id": user_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process the message
            swarm_input = {
                "messages": [{"role": "user", "content": data.get("message", "")}]
            }
            
            if data.get("active_agent"):
                swarm_input["active_agent"] = data["active_agent"]
            
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_id": user_id
                },
                "user_context": user_context.to_config_dict()
            }
            
            # Get the swarm app
            swarm_app = await get_app()
            
            # Invoke the swarm
            result = await asyncio.to_thread(
                swarm_app.invoke,
                swarm_input,
                config
            )
            
            # Store thread state
            threads_store[user_id][thread_id] = result
            
            # Update metadata
            active_agent = result.get("active_agent", "AnalysisAgent")
            update_thread_metadata(user_id, thread_id, 1, active_agent)
            
            # Send response
            messages = result.get("messages", [])
            last_message = messages[-1] if messages else {"content": "No response"}
            
            await websocket.send_json({
                "response": last_message.get("content", "") if isinstance(last_message, dict) else getattr(last_message, 'content', ''),
                "active_agent": active_agent,
                "thread_id": thread_id,
                "user_id": user_id
            })
            
    except WebSocketDisconnect:
        if user_id and thread_id:
            print(f"WebSocket disconnected for user {user_id}, thread {thread_id}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)