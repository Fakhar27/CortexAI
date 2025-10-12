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

from fastapi import FastAPI, HTTPException, BackgroundTasks
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
            counter = 0
            for tok in text.split(" "):
                yield _sse_frame("delta", {"text": tok + " "})
                counter += 1
                # Send heartbeat every ~30 tokens to keep connections alive
                if counter % 30 == 0:
                    yield b": keep-alive\n\n"
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


def get_cached_title(thread_id: str) -> Optional[str]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_pg = is_postgres_connection(conn)
        ph = "%s" if is_pg else "?"
        cursor.execute(
            f"SELECT title FROM conversation_titles WHERE thread_id = {ph}",
            (thread_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def setup_titles_table():
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


def generate_title_for_conversation(thread_id: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    is_pg = is_postgres_connection(conn)
    ph = "%s" if is_pg else "?"

    cursor.execute(
        f"SELECT title FROM conversation_titles WHERE thread_id = {ph}",
        (thread_id,),
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    messages_text: list[str] = []
    if is_pg and msgpack is not None:
        cursor.execute(
            f"""
            SELECT channel, blob, type
            FROM checkpoint_writes
            WHERE thread_id = {ph} AND channel = 'messages'
            ORDER BY checkpoint_id, idx
            LIMIT 10
            """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        for row in rows:
            _channel, blob, blob_type = row
            if blob_type == "msgpack":
                msg_list = msgpack.unpackb(blob, raw=False)  # type: ignore
                for ext_msg in msg_list:
                    if isinstance(ext_msg, msgpack.ExtType):  # type: ignore
                        inner_data = msgpack.unpackb(ext_msg.data, raw=False)  # type: ignore
                        if isinstance(inner_data, list) and len(inner_data) >= 3:
                            msg_dict = inner_data[2]
                            if isinstance(msg_dict, dict):
                                content = msg_dict.get("content", "")
                                if content:
                                    messages_text.append(str(content)[:200])
                                    if len(messages_text) >= 4:
                                        break
            if len(messages_text) >= 4:
                break

    if not messages_text:
        title = "New conversation"
    else:
        conversation_snippet = "\n".join(messages_text[:4])
        try:
            title_response = api.create(
                input=(
                    "Generate a short, 3-5 word title for this conversation. "
                    "Just return the title, nothing else:\n\n" + conversation_snippet
                ),
                model="gpt-4o-mini",
                store=False,
                temperature=0.5,
            )
            if (
                "output" in title_response
                and isinstance(title_response["output"], list)
                and title_response["output"]
            ):
                title = title_response["output"][0]["content"][0].get(
                    "text", "New conversation"
                )
                title = title.strip().strip('"').strip("'")[:60]
            else:
                title = messages_text[0][:50]
        except Exception:
            title = messages_text[0][:50] if messages_text else "New conversation"

    try:
        cursor.execute(
            f"INSERT INTO conversation_titles (thread_id, title) VALUES ({ph}, {ph})",
            (thread_id, title),
        )
        conn.commit()
    except Exception:
        pass
    conn.close()
    return title


@app.get("/conversations")
async def list_conversations(background_tasks: BackgroundTasks):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                thread_id,
                MIN(checkpoint_id) as first_checkpoint,
                MAX(checkpoint_id) as last_checkpoint,
                COUNT(*) as checkpoint_count
            FROM checkpoints
            WHERE thread_id IS NOT NULL
            GROUP BY thread_id
            ORDER BY last_checkpoint DESC
            LIMIT 50
            """
        )

        conversations = []
        for row in cursor.fetchall():
            thread_id, first_checkpoint, last_checkpoint, checkpoint_count = row

            # Attempt to derive created_at from earliest checkpoint
            created_at = first_checkpoint
            title = get_cached_title(thread_id) or "New conversation"
            if title == "New conversation":
                background_tasks.add_task(generate_title_for_conversation, thread_id)

            conversations.append(
                {
                    "id": thread_id,
                    "created_at": str(created_at) if created_at else "Unknown",
                    "message_count": checkpoint_count,
                    "title": title,
                }
            )

        conn.close()
        return {"conversations": conversations}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list conversations: {e}"
        )


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_pg = is_postgres_connection(conn)

        messages: list[Dict[str, Any]] = []
        if is_pg and msgpack is not None:
            cursor.execute(
                """
                SELECT channel, blob, type, idx
                FROM checkpoint_writes
                WHERE thread_id = %s AND channel = 'messages'
                ORDER BY checkpoint_id, idx
                """,
                (conversation_id,),
            )
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                raise HTTPException(status_code=404, detail="Conversation not found")
            try:
                for row in rows:
                    _channel, blob, blob_type, _idx = row
                    if blob_type == "msgpack":
                        msg_list = msgpack.unpackb(blob, raw=False)  # type: ignore
                        for ext_msg in msg_list:
                            if isinstance(ext_msg, msgpack.ExtType):  # type: ignore
                                inner_data = msgpack.unpackb(ext_msg.data, raw=False)  # type: ignore
                                if (
                                    isinstance(inner_data, list)
                                    and len(inner_data) >= 3
                                ):
                                    msg_dict = inner_data[2]
                                    if isinstance(msg_dict, dict):
                                        content = msg_dict.get("content", "")
                                        msg_type = (
                                            msg_dict.get("type", "unknown")
                                            if not isinstance(inner_data[1], str)
                                            else inner_data[1]
                                            .replace("Message", "")
                                            .lower()
                                        )
                                        if content:
                                            messages.append(
                                                {
                                                    "role": msg_type,
                                                    "content": str(content),
                                                }
                                            )
            except Exception:
                pass
        else:
            cursor.execute(
                """
                SELECT checkpoint
                FROM checkpoints
                WHERE thread_id = ?
                ORDER BY checkpoint_id DESC
                LIMIT 1
                """,
                (conversation_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                raise HTTPException(status_code=404, detail="Conversation not found")
            try:
                import pickle

                checkpoint_blob = row[0]
                if isinstance(checkpoint_blob, memoryview):
                    checkpoint_blob = checkpoint_blob.tobytes()
                checkpoint_data = pickle.loads(checkpoint_blob)
                message_history = checkpoint_data.get("channel_values", {}).get(
                    "messages", []
                )
                for msg in message_history:
                    if hasattr(msg, "content") and hasattr(msg, "__class__"):
                        message_type = msg.__class__.__name__.replace(
                            "Message", ""
                        ).lower()
                        messages.append(
                            {"role": message_type, "content": str(msg.content)}
                        )
            except Exception:
                pass

        conn.close()
        return {"conversation_id": conversation_id, "messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve conversation: {e}"
        )


@app.on_event("startup")
async def _ensure_tables():
    # Conversation titles table (optional helper)
    try:
        setup_titles_table()
    except Exception:
        pass
