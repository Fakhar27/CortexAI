"""Persistence and checkpointing for Responses API"""
import os
import sqlite3
from typing import Optional, Dict, Any
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
        path = db_path or os.getenv("CORTEX_DB_PATH", "conversations.db")
        conn = sqlite3.connect(path, check_same_thread=False)
        return SmartCheckpointer(conn)
    
    elif provider == "memory":
        return MemorySaver()
    
    else:
        raise ValueError(f"Unknown checkpointer provider: {provider}")


class SmartCheckpointer(SqliteSaver):
    """
    Smart checkpointer that handles store=True/False logic
    Always reads from DB, only saves when store=True
    Uses separate connection for response tracking to avoid transaction conflicts
    """
    
    def __init__(self, conn: sqlite3.Connection):
        """Initialize with SQLite connection"""
        super().__init__(conn)
        self.conn = conn
        
        # Get database path from connection
        cursor = conn.cursor()
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchone()
        self.db_path = db_info[2] if db_info else "conversations.db"
        
        # Create separate connection for response tracking (our own "key")
        self.tracking_conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._setup_response_tracking()
    
    def _setup_response_tracking(self):
        """
        Create response tracking table to map response_ids to thread_ids
        This solves the problem where continued responses aren't findable
        Uses our separate tracking connection
        """
        cursor = self.tracking_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_tracking (
                response_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                was_stored BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.tracking_conn.commit()
        
    def response_exists(self, response_id: str) -> bool:
        """
        Check if a response exists and was stored
        Uses our tracking connection for thread-safe access
        
        Args:
            response_id: The response_id to check
            
        Returns:
            True if exists and was stored, False otherwise
        """
        cursor = self.tracking_conn.cursor()
        
        # Check in our response tracking table
        cursor.execute(
            "SELECT was_stored FROM response_tracking WHERE response_id = ?",
            (response_id,)
        )
        
        result = cursor.fetchone()
        # Response must exist AND have been stored (store=True)
        return result is not None and result[0] == 1
    
    def get_thread_for_response(self, response_id: str) -> Optional[str]:
        """
        Get the thread_id that a response_id belongs to
        Uses our tracking connection for thread-safe access
        
        Args:
            response_id: The response_id to look up
            
        Returns:
            thread_id if found, None otherwise
        """
        cursor = self.tracking_conn.cursor()
        cursor.execute(
            "SELECT thread_id FROM response_tracking WHERE response_id = ?",
            (response_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any], new_versions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save checkpoint only if store=True
        Uses separate tracking connection to avoid transaction conflicts
        
        This is called by LangGraph after processing to save state
        """
        # Extract needed values
        store = config.get("configurable", {}).get("store", True)
        thread_id = config.get("configurable", {}).get("thread_id")
        response_id = config.get("configurable", {}).get("response_id")
        
        if store:
            # Save to database - let LangGraph handle its transaction
            result = super().put(config, checkpoint, metadata, new_versions)
            
            # Track this response_id -> thread_id mapping using our separate connection
            if response_id and thread_id:
                cursor = self.tracking_conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO response_tracking (response_id, thread_id, was_stored) VALUES (?, ?, ?)",
                    (response_id, thread_id, 1)
                )
                self.tracking_conn.commit()  # Safe - using our own connection/transaction
            
            return result
        else:
            # Don't save checkpoint, but track the response as unsaved
            if response_id and thread_id:
                cursor = self.tracking_conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO response_tracking (response_id, thread_id, was_stored) VALUES (?, ?, ?)",
                    (response_id, thread_id, 0)
                )
                self.tracking_conn.commit()  # Safe - using our own connection/transaction
            
            # Return a dummy response that prevents LangGraph from erroring
            return {
                "v": 1,
                "ts": checkpoint.get("ts", ""),
                "id": checkpoint.get("id", ""),
                "checkpoint": checkpoint,
                "metadata": metadata
            }
    
    def close(self):
        """
        Close both connections properly
        Important for cleanup and avoiding connection leaks
        """
        try:
            self.tracking_conn.close()
        except:
            pass  # Ignore errors during cleanup
        
        # Let parent class handle main connection
        if hasattr(super(), 'close'):
            super().close()


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None