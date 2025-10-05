"""
ASGI application for the CortexAI REST API (unified in responses package).

Provides non‑streaming and streaming chat endpoints used by the demos.
The example server script simply imports and runs this app to keep the
demo wrapper thin — all functionality lives here.
"""

from __future__ import annotations

import os
import json
import uuid
import sqlite3
import asyncio
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .api import ResponsesAPI

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    import psycopg  # type: ignore
    import msgpack  # type: ignore

    POSTGRES_AVAILABLE = True
except Exception:
    POSTGRES_AVAILABLE = False
    msgpack = None  # type: ignore


app = FastAPI(title="CortexAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = ResponsesAPI()


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response_id: str
    message: str
    model: str
    usage: Dict[str, Any]
    conversation_id: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "CortexAI API Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a chat message",
            "POST /chat/stream": "SSE streaming chat",
            "GET /models": "List available models",
            "GET /conversations": "List all conversations",
            "GET /conversations/{conversation_id}": "Get conversation details",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CortexAI"}


@app.get("/models")
async def list_models():
    """List models grouped by provider based on the registry (non‑deprecated)."""
    try:
        from cortex.models.registry import list_available_models

        items = list_available_models()
        grouped: Dict[str, list] = {}
        for entry in items:
            provider = entry.get("provider")
            model_id = entry.get("model")
            if not provider or not model_id:
                continue
            grouped.setdefault(provider, []).append(model_id)
        for key in grouped:
            grouped[key] = sorted(grouped[key])
        return grouped
    except Exception:
        return {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "google": ["gemini-2.0-flash", "gemini-2.5-flash"],
            "cohere": ["command-r-08-2024", "command-r-plus-08-2024"],
        }


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url and POSTGRES_AVAILABLE:
        return psycopg.connect(db_url, gssencmode="disable")  # type: ignore
    db_path = os.getenv("CORTEX_DB_PATH", "conversations.db")
    return sqlite3.connect(db_path)


def is_postgres_connection(conn) -> bool:
    return hasattr(conn, "cursor") and "psycopg" in str(type(conn))


def get_latest_response_id_for_thread(thread_id: str) -> Optional[str]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_pg = is_postgres_connection(conn)
        ph = "%s" if is_pg else "?"
        cursor.execute(
            f"SELECT response_id FROM response_tracking WHERE thread_id = {ph} ORDER BY created_at DESC LIMIT 1",
            (thread_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        prev_response_id: Optional[str] = None
        thread_id: Optional[str] = None

        if request.conversation_id:
            latest = get_latest_response_id_for_thread(request.conversation_id)
            if latest:
                prev_response_id = latest
                thread_id = request.conversation_id
            else:
                prev_response_id = request.conversation_id
                try:
                    thread_id = getattr(
                        api, "checkpointer", None
                    ).get_thread_for_response(
                        prev_response_id
                    )  # type: ignore[attr-defined]
                except Exception:
                    thread_id = request.conversation_id

        result = api.create(
            input=request.message,
            model=request.model,
            previous_response_id=prev_response_id,
            instructions=request.system_prompt,
            store=True,
            temperature=request.temperature,
        )

        message_content = ""
        if (
            isinstance(result, dict)
            and isinstance(result.get("output"), list)
            and result["output"]
        ):
            content_list = result["output"][0].get("content", [])
            if content_list:
                message_content = content_list[0].get("text", "")

        response_id = result.get("id") or str(uuid.uuid4())
        model_name = result.get("model") or request.model
        usage_data = result.get("usage") or {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
        }

        if thread_id is None:
            thread_id = response_id

        return ChatResponse(
            response_id=response_id,
            message=message_content,
            model=model_name,
            usage=usage_data,
            conversation_id=thread_id,
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


def _sse_frame(event: str, data: Dict[str, Any]) -> bytes:
    try:
        payload = json.dumps(data, ensure_ascii=False)
    except Exception:
        payload = json.dumps({"error": "serialization_error"})
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream assistant response using Server‑Sent Events (SSE).
    For now, stream the generated message in small chunks for interactivity.
    """
    try:
        prev_response_id: Optional[str] = None
        thread_id: Optional[str] = None

        if request.conversation_id:
            latest = get_latest_response_id_for_thread(request.conversation_id)
            if latest:
                prev_response_id = latest
                thread_id = request.conversation_id
            else:
                prev_response_id = request.conversation_id
                try:
                    thread_id = getattr(
                        api, "checkpointer", None
                    ).get_thread_for_response(
                        prev_response_id
                    )  # type: ignore[attr-defined]
                except Exception:
                    thread_id = request.conversation_id

        full = api.create(
            input=request.message,
            model=request.model,
            previous_response_id=prev_response_id,
            instructions=request.system_prompt,
            store=True,
            temperature=request.temperature,
        )

        text = ""
        if (
            isinstance(full, dict)
            and isinstance(full.get("output"), list)
            and full["output"]
        ):
            content_list = full["output"][0].get("content", [])
            if content_list:
                text = content_list[0].get("text", "")

        response_id = full.get("id") if isinstance(full, dict) else None
        model_name = full.get("model") if isinstance(full, dict) else request.model
        usage = full.get("usage") if isinstance(full, dict) else None
        if thread_id is None:
            thread_id = response_id

        async def gen():
            yield _sse_frame(
                "start",
                {
                    "response_id": response_id,
                    "conversation_id": thread_id,
                    "model": model_name,
                },
            )

            delay = 0.015
            for tok in text.split(" "):
                yield _sse_frame("delta", {"text": tok + " "})
                await asyncio.sleep(delay)

            yield _sse_frame(
                "end",
                {
                    "response_id": response_id,
                    "conversation_id": thread_id,
                    "model": model_name,
                    "usage": usage
                    or {
                        "total_tokens": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                    },
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
            yield _sse_frame("error", {"message": error_msg})
            yield _sse_frame("end", {"error": True})

        return StreamingResponse(err(), media_type="text/event-stream")


@app.on_event("startup")
async def _ensure_tables():
    # Conversation titles table (optional helper)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_titles (
                thread_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()
    except Exception:
        # Optional — best effort only
        pass
