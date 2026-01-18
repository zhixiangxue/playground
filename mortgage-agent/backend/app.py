"""FastAPI application with WebSocket for mortgage agent"""
import json
import traceback
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agent import MortgageAgent


app = FastAPI(
    title="Mortgage Agent API",
    description="AI-powered mortgage advisory service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Store active agents per connection
agents: Dict[int, MortgageAgent] = {}


@app.get("/")
async def root():
    """Root endpoint - redirect to chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Mortgage Agent</title>
    </head>
    <body>
        <h1>🏠 Mortgage Agent</h1>
        <p><a href="/static/chat.html">Open Chat Interface</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for chat
    
    Message format:
    - type: "message" - Send user message
    - type: "reset" - Reset conversation
    """
    await websocket.accept()
    conn_id = id(websocket)
    
    # Create agent for this connection
    try:
        agent = MortgageAgent()
        agents[conn_id] = agent
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            
            if msg_type == "message":
                # Get user message
                user_msg = message.get("message", "")
                stream = message.get("stream", True)
                
                if not user_msg:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": "Empty message"
                    }))
                    continue
                
                # Stream response
                if stream:
                    async for event in await agent.send_message(user_msg, stream=True):
                        # Import event types
                        from chak.message import MessageChunk, ToolCallStartEvent, ToolCallSuccessEvent, ToolCallErrorEvent
                                        
                        # Handle different event types
                        if isinstance(event, ToolCallStartEvent):
                            # Tool call started
                            await websocket.send_text(json.dumps({
                                "type": "tool_start",
                                "tool_name": event.tool_name,
                                "arguments": event.arguments,
                                "call_id": event.call_id
                            }, ensure_ascii=False))
                                        
                        elif isinstance(event, ToolCallSuccessEvent):
                            # Tool call succeeded
                            await websocket.send_text(json.dumps({
                                "type": "tool_success",
                                "tool_name": event.tool_name,
                                "result": str(event.result),  # Send full result (no truncation)
                                "call_id": event.call_id
                            }, ensure_ascii=False))
                                        
                        elif isinstance(event, ToolCallErrorEvent):
                            # Tool call failed
                            await websocket.send_text(json.dumps({
                                "type": "tool_error",
                                "tool_name": event.tool_name,
                                "error": str(event.error),
                                "call_id": event.call_id
                            }, ensure_ascii=False))
                                        
                        elif isinstance(event, MessageChunk):
                            # Regular message chunk
                            chunk_data = {
                                "type": "chunk",
                                "content": event.content,
                                "is_final": event.is_final
                            }
                                            
                            # Add final message if available
                            if event.is_final and event.final_message:
                                chunk_data["final_message"] = {
                                    "role": event.final_message.role,
                                    "content": event.final_message.content
                                }
                                            
                            await websocket.send_text(json.dumps(chunk_data, ensure_ascii=False))
                            
                            # Add small delay for smooth frontend rendering
                            import asyncio
                            await asyncio.sleep(0.03)  # 30ms delay for smoother streaming
                else:
                    # Non-streaming
                    response = await agent.send_message(user_msg, stream=False)
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "content": response.content
                    }, ensure_ascii=False))
            
            elif msg_type == "reset":
                # Reset agent
                agent.reset()
                await websocket.send_text(json.dumps({
                    "type": "ok",
                    "action": "reset"
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"Unknown message type: {msg_type}"
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e),
            "detail": traceback.format_exc()
        }))
    finally:
        # Cleanup
        if conn_id in agents:
            del agents[conn_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
