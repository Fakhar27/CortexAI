"""Persistence and checkpointing for Responses API"""
import os
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver


def get_checkpointer(
    db_path: Optional[str] = None,
    provider: str = "sqlite"
) -> BaseCheckpointSaver:
    """
    Get a checkpointer instance for persisting conversations
    
    Args:
        db_path: Path to database file. If None, uses default
        provider: Type of checkpointer (sqlite, postgres, memory)
        
    Returns:
        Checkpointer instance
    """
    if provider == "sqlite":
        # Use provided path or default
        path = db_path or os.getenv("CORTEX_DB_PATH", "conversations.db")
        return SqliteSaver.from_conn_string(path)
    
    elif provider == "memory":
        # For testing - in-memory checkpointer
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()
    
    elif provider == "postgres":
        # Future implementation
        # from langgraph.checkpoint.postgres import PostgresSaver
        # connection_string = db_path or os.getenv("POSTGRES_URL")
        # return PostgresSaver.from_conn_string(connection_string)
        raise NotImplementedError("PostgreSQL checkpointer coming soon")
    
    else:
        raise ValueError(f"Unknown checkpointer provider: {provider}")


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None