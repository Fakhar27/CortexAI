"""
ASGI application for the CortexAI REST API (unified in responses package).

This centralizes server-side logic under `cortex.responses` so demo scripts
remain thin and communicate purely over REST.
"""

import os
import uuid
import sqlite3
import traceback
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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
    msgpack = None


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
    conversation_id: str | None = None
    system_prompt: str | None = None
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response_id: str
    message: str
    model: str
    usage: Dict[str, Any]
    # conversation_id is the stable thread/conversation ID (not per-message id)
    conversation_id: str | None = None


@app.get("/")
async def root():
    return {
        "message": "CortexAI API Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a chat message",
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
    """List available models grouped by provider, based on the registry.

    This reflects current non-deprecated entries from `cortex.models.registry`.
    """
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
        # Sort models within each provider for stable output
        for key in grouped:
            grouped[key] = sorted(grouped[key])
        return grouped
    except Exception:
        # Fallback to a minimal static set if registry import fails for any reason
        return {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "google": ["gemini-2.0-flash", "gemini-2.5-flash"],
            "cohere": ["command-r-08-2024", "command-r-plus-08-2024"],
        }


def get_latest_response_id_for_thread(thread_id: str) -> str | None:
    """Return the most recent response_id for a given thread_id, if any."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_postgres = is_postgres_connection(conn)
        ph = "%s" if is_postgres else "?"
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
    """
    Handle chat requests. The request.conversation_id is treated as the stable
    thread/conversation ID. For continuation, we resolve the latest response_id
    for that thread and pass it to the core API. We return conversation_id as
    the thread ID so clients can use a stable identifier.
    """
    try:
        prev_response_id: str | None = None
        thread_id: str | None = None

        if request.conversation_id:
            # Prefer treating provided value as a thread id for stable semantics
            latest_for_thread = get_latest_response_id_for_thread(
                request.conversation_id
            )
            if latest_for_thread:
                prev_response_id = latest_for_thread
                thread_id = request.conversation_id
            else:
                # Back-compat: if client sent a response_id, try to resolve its thread
                prev_response_id = request.conversation_id
                try:
                    thread_id = getattr(api, "checkpointer", None).get_thread_for_response(prev_response_id)  # type: ignore[attr-defined]
                except Exception:
                    thread_id = request.conversation_id

        response = api.create(
            input=request.message,
            model=request.model,
            previous_response_id=prev_response_id,
            instructions=request.system_prompt,
            store=True,
            temperature=request.temperature,
        )

        message_content = ""
        if (
            "output" in response
            and isinstance(response["output"], list)
            and response["output"]
        ):
            output_item = response["output"][0]
            if (
                "content" in output_item
                and isinstance(output_item["content"], list)
                and output_item["content"]
            ):
                message_content = output_item["content"][0].get("text", "")

        response_id = response.get("id") or str(uuid.uuid4())
        model_name = response.get("model") or request.model
        usage_data = response.get("usage") or {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
        }

        # If this was a brand new conversation, the thread id equals the first response id
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


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url and POSTGRES_AVAILABLE:
        return psycopg.connect(db_url, gssencmode="disable")  # type: ignore
    db_path = os.getenv("CORTEX_DB_PATH", "conversations.db")
    return sqlite3.connect(db_path)


def is_postgres_connection(conn) -> bool:
    return hasattr(conn, "cursor") and "psycopg" in str(type(conn))


def get_cached_title(thread_id: str) -> str | None:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_postgres = is_postgres_connection(conn)
        ph = "%s" if is_postgres else "?"
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
    is_postgres = is_postgres_connection(conn)
    param_placeholder = "%s" if is_postgres else "?"

    cursor.execute(
        f"SELECT title FROM conversation_titles WHERE thread_id = {param_placeholder}",
        (thread_id,),
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    messages_text: List[str] = []
    if is_postgres and msgpack is not None:  # type: ignore
        cursor.execute(
            f"""
            SELECT channel, blob, type
            FROM checkpoint_writes
            WHERE thread_id = {param_placeholder} AND channel = 'messages'
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
            f"INSERT INTO conversation_titles (thread_id, title) VALUES ({param_placeholder}, {param_placeholder})",
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
        is_postgres = is_postgres_connection(conn)
        param_placeholder = "%s" if is_postgres else "?"

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

            cursor.execute(
                f"""
                SELECT checkpoint
                FROM checkpoints
                WHERE thread_id = {param_placeholder}
                ORDER BY checkpoint_id ASC
                LIMIT 1
                """,
                (thread_id,),
            )

            created_at = None
            checkpoint_row = cursor.fetchone()
            if checkpoint_row:
                try:
                    import pickle

                    checkpoint_blob = checkpoint_row[0]
                    if isinstance(checkpoint_blob, dict):
                        checkpoint_data = checkpoint_blob
                    else:
                        if isinstance(checkpoint_blob, memoryview):
                            checkpoint_blob = checkpoint_blob.tobytes()
                        checkpoint_data = pickle.loads(checkpoint_blob)
                    created_at = checkpoint_data.get("ts")
                except Exception:
                    pass

            if not created_at:
                cursor.execute(
                    f"""
                    SELECT MIN(created_at)
                    FROM response_tracking
                    WHERE thread_id = {param_placeholder}
                    """,
                    (thread_id,),
                )
                tracking_row = cursor.fetchone()
                if tracking_row and tracking_row[0]:
                    created_at = tracking_row[0]

            if not created_at:
                created_at = first_checkpoint

            title = get_cached_title(thread_id)
            if title is None:
                title = "New conversation"
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
    except Exception as e:
        error_detail = (
            f"Failed to retrieve conversations: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/conversations/{conversation_id}/generate-title")
async def generate_conversation_title(conversation_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_postgres = is_postgres_connection(conn)
        param_placeholder = "%s" if is_postgres else "?"

        messages_text: List[str] = []
        if is_postgres and msgpack is not None:  # type: ignore
            cursor.execute(
                f"""
                SELECT channel, blob, type
                FROM checkpoint_writes
                WHERE thread_id = {param_placeholder} AND channel = 'messages'
                ORDER BY checkpoint_id, idx
                LIMIT 10
                """,
                (conversation_id,),
            )
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                raise HTTPException(status_code=404, detail="Conversation not found")
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

        conn.close()

        if not messages_text:
            return {"title": "New conversation"}

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
                title = "New conversation"
        except Exception:
            title = (
                messages_text[0][:50] + "..." if messages_text else "New conversation"
            )

        return {"title": title}
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Failed to generate title: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_postgres = is_postgres_connection(conn)
        param_placeholder = "%s" if is_postgres else "?"

        messages: List[Dict[str, Any]] = []
        if is_postgres and msgpack is not None:  # type: ignore
            cursor.execute(
                f"""
                SELECT channel, blob, type, idx
                FROM checkpoint_writes
                WHERE thread_id = {param_placeholder} AND channel = 'messages'
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
                f"""
                SELECT checkpoint
                FROM checkpoints
                WHERE thread_id = {param_placeholder}
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
        error_detail = (
            f"Failed to retrieve conversation: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail=error_detail)


@app.on_event("startup")
async def _ensure_tables():
    setup_titles_table()
