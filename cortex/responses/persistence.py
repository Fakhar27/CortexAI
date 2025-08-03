"""Persistence and checkpointing for Responses API"""
import os
import sqlite3
from typing import Optional, Dict, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


class SmartCheckpointer(SqliteSaver):
    """
    Smart checkpointer that handles store=True/False logic
    Always reads from DB, only saves when store=True
    """
    
    def __init__(self, conn: sqlite3.Connection):
        """Initialize with SQLite connection"""
        super().__init__(conn)
        self.conn = conn
        self._setup_response_tracking()
    
    def _setup_response_tracking(self):
        """
        Create response tracking table to map response_ids to thread_ids
        This solves the problem where continued responses aren't findable
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_tracking (
                response_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                was_stored BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
    def response_exists(self, response_id: str) -> bool:
        """
        Check if a response exists and was stored
        
        Args:
            response_id: The response_id to check
            
        Returns:
            True if exists and was stored, False otherwise
        """
        cursor = self.conn.cursor()
        
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
        
        Args:
            response_id: The response_id to look up
            
        Returns:
            thread_id if found, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT thread_id FROM response_tracking WHERE response_id = ?",
            (response_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any], new_versions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save checkpoint only if store=True
        
        This is called by LangGraph after processing to save state
        """
        # Extract needed values
        store = config.get("configurable", {}).get("store", True)
        thread_id = config.get("configurable", {}).get("thread_id")
        response_id = config.get("configurable", {}).get("response_id")  # We'll pass this
        
        # Track this response_id -> thread_id mapping
        if response_id and thread_id:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO response_tracking (response_id, thread_id, was_stored) VALUES (?, ?, ?)",
                (response_id, thread_id, 1 if store else 0)
            )
            self.conn.commit()
        
        if store:
            # Save to database - pass all arguments to parent
            return super().put(config, checkpoint, metadata, new_versions)
        else:
            # Don't save checkpoint, but return a dummy response
            # This prevents LangGraph from erroring
            return {
                "v": 1,
                "ts": checkpoint.get("ts", ""),
                "id": checkpoint.get("id", ""),
                "checkpoint": checkpoint,
                "metadata": metadata
            }
    
    def get_tuple(self, config: Dict[str, Any]) -> Optional[Any]:
        """
        Always load history if it exists
        
        This is called by LangGraph before processing to load state
        """
        # Always try to load, regardless of store flag
        return super().get_tuple(config)


class MemorySmartCheckpointer(MemorySaver):
    """
    Memory version of smart checkpointer for testing
    """
    
    def response_exists(self, thread_id: str) -> bool:
        """Check if thread exists in memory"""
        # MemorySaver stores in self.storage dict
        for key in self.storage:
            if key.get("thread_id") == thread_id:
                return True
        return False
    
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any], new_versions: Dict[str, Any] = None) -> Dict[str, Any]:
        """Save only if store=True"""
        store = config.get("configurable", {}).get("store", True)
        
        if store:
            # Pass all arguments to parent
            return super().put(config, checkpoint, metadata, new_versions)
        else:
            # Return dummy response
            return {
                "v": 1,
                "ts": checkpoint.get("ts", ""),
                "id": checkpoint.get("id", ""),
                "checkpoint": checkpoint,
                "metadata": metadata
            }


def get_checkpointer(
    db_path: Optional[str] = None,
    provider: str = "sqlite"
):
    """
    Get a smart checkpointer instance for persisting conversations
    
    Args:
        db_path: Path to database file. If None, uses default
        provider: Type of checkpointer (sqlite, postgres, memory)
        
    Returns:
        SmartCheckpointer instance
    """
    if provider == "sqlite":
        # Use provided path or default
        path = db_path or os.getenv("CORTEX_DB_PATH", "conversations.db")
        
        # Create SQLite connection directly (as shown in LangGraph docs)
        # check_same_thread=False is OK as SqliteSaver uses locks for thread safety
        conn = sqlite3.connect(path, check_same_thread=False)
        
        # Return SmartCheckpointer with the connection
        return SmartCheckpointer(conn)
    
    elif provider == "memory":
        # For testing - in-memory smart checkpointer
        return MemorySmartCheckpointer()
    
    else:
        raise ValueError(f"Unknown checkpointer provider: {provider}")


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None