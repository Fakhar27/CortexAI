#!/usr/bin/env python3
"""
FastAPI web server example for CortexAI
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cortex import Client
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="CortexAI API", version="1.0.0")

# Initialize CortexAI client
api = Client()

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"
    conversation_id: str = None
    system_prompt: str = None
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response_id: str
    message: str
    model: str
    usage: dict
    conversation_id: str = None

@app.get("/")
async def root():
    return {
        "message": "CortexAI API Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a chat message",
            "GET /models": "List available models",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CortexAI"}

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "google": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro"],
        "cohere": ["command-r-08-2024", "command-r-plus-08-2024"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get AI response"""
    try:
        response = api.create(
            input=request.message,
            model=request.model,
            previous_response_id=request.conversation_id,
            instructions=request.system_prompt,
            store=True,
            temperature=request.temperature
        )
        
        # Extract message content from the response structure
        message_content = ""
        if 'output' in response and len(response['output']) > 0:
            message_content = response['output'][0]['content'][0]['text']
        
        return ChatResponse(
            response_id=response["id"],
            message=message_content,
            model=response["model"],
            usage=response["usage"],
            conversation_id=response["id"]  # For continuing conversation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting CortexAI Web Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("\n🔑 Make sure to set your API keys:")
    print("   export OPENAI_API_KEY='your-key'")
    print("   export GOOGLE_API_KEY='your-key'")
    print("   export CO_API_KEY='your-key'")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

