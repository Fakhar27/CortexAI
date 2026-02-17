"""Retrieve method for Responses API

Adds a Python-side utility to fetch a conversation's messages either by
response_id or the stable thread_id, without changing REST behavior.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import os
import sqlite3


try:
    import psycopg  # type: ignore
    import msgpack  # type: ignore

    POSTGRES_AVAILABLE = True
except Exception:
    POSTGRES_AVAILABLE = False
    msgpack = None  # type: ignore


def _get_db_connection():
    """Return a DB connection to either PostgreSQL or SQLite based on env."""
    db_url = os.getenv("DATABASE_URL")
    if db_url and POSTGRES_AVAILABLE:
        return psycopg.connect(db_url, gssencmode="disable")  # type: ignore
    db_path = os.getenv("CORTEX_DB_PATH", "conversations.db")
    return sqlite3.connect(db_path)


def _is_postgres_connection(conn) -> bool:
    return hasattr(conn, "cursor") and "psycopg" in str(type(conn))


def _retrieve_messages_postgres(thread_id: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    if not POSTGRES_AVAILABLE or msgpack is None:  # type: ignore
        return messages
    conn = _get_db_connection()
    try:
        with conn.cursor() as cursor:  # type: ignore[attr-defined]
            cursor.execute(
                """
                SELECT channel, blob, type, idx
                FROM checkpoint_writes
                WHERE thread_id = %s AND channel = 'messages'
                ORDER BY checkpoint_id, idx
                """,
                (thread_id,),
            )
            rows = cursor.fetchall()
            for row in rows:
                _channel, blob, blob_type, _idx = row
                if blob_type == "msgpack":
                    try:
                        msg_list = msgpack.unpackb(blob, raw=False)  # type: ignore
                    except Exception:
                        continue
                    for ext_msg in msg_list:
                        try:
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
                            continue
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return messages


def _retrieve_messages_sqlite(thread_id: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT checkpoint
            FROM checkpoints
            WHERE thread_id = ?
            ORDER BY checkpoint_id DESC
            LIMIT 1
            """,
            (thread_id,),
        )
        row = cursor.fetchone()
        if not row:
            return messages
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
                    message_type = msg.__class__.__name__.replace("Message", "").lower()
                    messages.append(
                        {
                            "role": message_type,
                            "content": str(getattr(msg, "content", "")),
                        }
                    )
        except Exception:
            return messages
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return messages


def retrieve_response(
    api_instance,
    response_id: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a conversation's messages by response_id or thread_id.

    Returns a dictionary with keys:
      - conversation_id: stable thread ID
      - messages: list of {role, content}
    """

    # Resolve thread_id from response_id if needed using the checkpointer
    resolved_thread_id = thread_id
    if not resolved_thread_id and response_id:
        try:
            cp = getattr(api_instance, "checkpointer", None)
            if cp and hasattr(cp, "get_thread_for_response"):
                resolved_thread_id = cp.get_thread_for_response(response_id)
        except Exception:
            resolved_thread_id = None

    if not resolved_thread_id:
        # As a last resort, assume provided response_id is the thread_id
        resolved_thread_id = response_id

    if not resolved_thread_id:
        return {"conversation_id": None, "messages": []}

    # Choose decoding path based on DB in use
    conn = _get_db_connection()
    try:
        if _is_postgres_connection(conn):
            messages = _retrieve_messages_postgres(resolved_thread_id)
        else:
            messages = _retrieve_messages_sqlite(resolved_thread_id)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {
        "conversation_id": resolved_thread_id,
        "messages": messages,
    }
