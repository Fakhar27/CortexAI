"""Persistence and checkpointing for Responses API"""
import os
import sqlite3
from typing import Optional
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer(
    db_path: Optional[str] = None,
    provider: str = "sqlite"
):
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
        
        # Create SQLite connection directly (as shown in LangGraph docs)
        # check_same_thread=False is OK as SqliteSaver uses locks for thread safety
        conn = sqlite3.connect(path, check_same_thread=False)
        
        # Create SqliteSaver with the connection
        return SqliteSaver(conn)
    
    elif provider == "memory":
        # For testing - in-memory checkpointer
        return MemorySaver()
    
    else:
        raise ValueError(f"Unknown checkpointer provider: {provider}")


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None