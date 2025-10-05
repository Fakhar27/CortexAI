#!/usr/bin/env python3
"""
FastAPI web server example for CortexAI

Adds a streaming endpoint (`/chat/stream`) using Server‑Sent Events (SSE).
This streams the final response text back to the client in small chunks to
provide incremental rendering in web demos.
"""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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
            "GET /health": "Health check",
        },
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
        "cohere": ["command-r-08-2024", "command-r-plus-08-2024"],
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
            temperature=request.temperature,
        )

        # Extract message content from the response structure
        message_content = ""
        if "output" in response and len(response["output"]) > 0:
            message_content = response["output"][0]["content"][0]["text"]

        return ChatResponse(
            response_id=response["id"],
            message=message_content,
            model=response["model"],
            usage=response["usage"],
            conversation_id=response["id"],  # For continuing conversation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _sse(event: str, data: dict) -> bytes:
    """Format a single SSE frame."""
    try:
        payload = json.dumps(data, ensure_ascii=False)
    except Exception:
        payload = json.dumps({"error": "serialization_error"})
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream assistant response using Server‑Sent Events (SSE).

    This demo streams the generated response in small chunks (word‑based) so
    clients can render incrementally. It does not change core response logic.
    """
    try:
        prev_response_id = request.conversation_id or None

        # Generate full response via the existing API
        full = api.create(
            input=request.message,
            model=request.model,
            previous_response_id=prev_response_id,
            instructions=request.system_prompt,
            store=True,
            temperature=request.temperature,
        )

        response_id = full.get("id") if isinstance(full, dict) else None
        model_name = full.get("model") if isinstance(full, dict) else request.model
        usage = (
            full.get("usage")
            if isinstance(full, dict)
            else {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        )

        # server decides new conversation id as the response id
        conversation_id = response_id

        # Extract assistant content from Responses‑style output
        text = ""
        if (
            isinstance(full, dict)
            and isinstance(full.get("output"), list)
            and full["output"]
            and isinstance(full["output"][0], dict)
            and isinstance(full["output"][0].get("content"), list)
            and full["output"][0]["content"]
        ):
            text = full["output"][0]["content"][0].get("text", "")

        async def gen():
            # Start frame
            yield _sse(
                "start",
                {
                    "response_id": response_id,
                    "conversation_id": conversation_id,
                    "model": model_name,
                },
            )

            # Stream small chunks (space‑separated tokens)
            delay = 0.015
            for tok in text.split(" "):
                yield _sse("delta", {"text": tok + " "})
                await asyncio.sleep(delay)

            # End frame with usage
            yield _sse(
                "end",
                {
                    "response_id": response_id,
                    "conversation_id": conversation_id,
                    "model": model_name,
                    "usage": usage,
                },
            )

        return StreamingResponse(
            gen(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:  # noqa: BLE001
        error_msg = str(e)

        async def err():
            yield _sse("error", {"message": error_msg})
            yield _sse("end", {"error": True})

        return StreamingResponse(err(), media_type="text/event-stream")


if __name__ == "__main__":
    print("🚀 Starting CortexAI Web Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("\n🔑 Make sure to set your API keys:")
    print("   export OPENAI_API_KEY='your-key'")
    print("   export GOOGLE_API_KEY='your-key'")
    print("   export CO_API_KEY='your-key'")

    uvicorn.run(app, host="0.0.0.0", port=8000)
