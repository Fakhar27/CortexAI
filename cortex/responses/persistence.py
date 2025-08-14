"""
Persistence and checkpointing for Responses API
Supports SQLite (local) and PostgreSQL (production/serverless)
"""
import os
import sqlite3
import warnings
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# PostgreSQL support (optional import)
try:
    from langgraph.checkpoint.postgres import PostgresSaver
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class DatabaseError(Exception):
    """Custom exception for database configuration errors"""
    pass


def is_serverless_environment() -> bool:
    """
    Detect if running in a serverless environment
    Used only for warnings, not for logic
    """
    serverless_indicators = [
        "VERCEL",
        "AWS_LAMBDA_FUNCTION_NAME", 
        "FUNCTIONS_WORKER_RUNTIME",  # GCP
        "AZURE_FUNCTIONS_ENVIRONMENT",
        "NETLIFY",
        "RENDER",
    ]
    return any(os.getenv(indicator) for indicator in serverless_indicators)


def validate_postgresql_url(db_url: str) -> None:
    """
    Validate that the URL is a valid PostgreSQL connection string
    
    Args:
        db_url: Connection string to validate
        
    Raises:
        DatabaseError: If URL is not valid PostgreSQL
    """
    if not db_url:
        raise DatabaseError("Database URL cannot be empty")
    
    # Accept both postgresql:// and postgres://
    valid_schemes = ['postgresql', 'postgres']
    
    try:
        parsed = urlparse(db_url)
        if parsed.scheme not in valid_schemes:
            raise DatabaseError(
                f"Only PostgreSQL is supported. Got: {parsed.scheme}://...\n"
                f"Expected: postgresql://user:pass@host:port/database"
            )
    except Exception as e:
        raise DatabaseError(f"Invalid database URL: {e}")


def get_checkpointer(
    db_url: Optional[str] = None,
    fallback_memory: bool = True
) -> Optional[Any]:
    """
    Get appropriate checkpointer based on configuration
    
    Args:
        db_url: PostgreSQL connection string or None for SQLite
                Can also be set via DATABASE_URL environment variable
        fallback_memory: If True, use MemorySaver in serverless without db_url
        
    Returns:
        Checkpointer instance (PostgresSaver, SmartCheckpointer, or MemorySaver)
        
    Raises:
        DatabaseError: For invalid configurations
    """
    
    # Check for db_url from parameter or environment
    connection_string = db_url or os.getenv("DATABASE_URL")
    
    # Check for empty string - treat as "use default SQLite" for graceful handling
    # This handles both db_url="" and DATABASE_URL=""  
    if connection_string == "":
        connection_string = None  # Treat empty string as None (use default)
    
    # Case 1: PostgreSQL explicitly requested
    if connection_string:
        # Validate it's PostgreSQL
        validate_postgresql_url(connection_string)
        
        # Check if PostgreSQL support is available
        if not POSTGRES_AVAILABLE:
            raise DatabaseError(
                "PostgreSQL support not installed.\n"
                "Install with: pip install 'cortex[postgres]'\n"
                "Or: pip install langgraph-checkpoint-postgres psycopg[binary]"
            )
        
        try:
            # Works for local PostgreSQL, Supabase, RDS, CloudSQL, etc.
            print(f"✅ Connecting to PostgreSQL database...")
            
            # Create a wrapper that maintains the connection
            wrapper = PostgresCheckpointerWrapper(connection_string)
            
            print(f"✅ Successfully connected to PostgreSQL")
            return wrapper
        except Exception as e:
            # Provide helpful error message
            if "could not translate host name" in str(e):
                raise DatabaseError(
                    f"Could not connect to database host.\n"
                    f"Check your connection string: {connection_string[:30]}...\n"
                    f"Format: postgresql://user:pass@host:port/database"
                )
            elif "password authentication failed" in str(e):
                raise DatabaseError(
                    f"Database authentication failed.\n"
                    f"Check your username and password in the connection string."
                )
            else:
                raise DatabaseError(
                    f"Failed to connect to PostgreSQL: {e}\n"
                    f"Connection string: {connection_string[:30]}...\n"
                    f"Format: postgresql://user:pass@host:port/database"
                )
    
    # Case 2: No db_url provided - use SQLite or memory
    else:
        # Check if we're in serverless
        if is_serverless_environment():
            if fallback_memory:
                warnings.warn(
                    "\n⚠️  Running in serverless without database URL!\n"
                    "Conversations will NOT persist between requests.\n"
                    "For persistence, use: Client(db_url='postgresql://...') or set DATABASE_URL env variable\n"
                    "Get free PostgreSQL from: https://supabase.com or https://neon.tech",
                    UserWarning,
                    stacklevel=2
                )
                return MemorySaver()
            else:
                raise DatabaseError(
                    "Serverless environment requires a database URL for persistence.\n"
                    "Options:\n"
                    "1. Pass db_url: Client(db_url='postgresql://...')\n"
                    "2. Set DATABASE_URL environment variable\n"
                    "Get free PostgreSQL from:\n"
                    "  • Supabase: https://supabase.com (500MB free)\n"
                    "  • Neon: https://neon.tech (3GB free)\n"
                    "  • Railway: https://railway.app ($5 credits)"
                )
        
        # Local environment - use SQLite
        else:
            try:
                print(f"✅ Using SQLite for local persistence (conversations.db)")
                # Use the enhanced SmartCheckpointer for SQLite
                db_path = os.getenv("CORTEX_DB_PATH", "conversations.db")
                conn = sqlite3.connect(db_path, check_same_thread=False)
                return SmartCheckpointer(conn)
            except Exception as e:
                # Fallback to basic SqliteSaver if SmartCheckpointer fails
                warnings.warn(f"Using basic SqliteSaver: {e}")
                return SqliteSaver.from_conn_string("conversations.db")


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


class PostgresCheckpointerWrapper:
    """
    Wrapper that maintains a PostgreSQL connection pool.
    This solves the context manager closing issue and adds custom methods.
    """
    
    def __init__(self, connection_string: str):
        """Initialize and open the connection"""
        self.connection_string = connection_string
        
        # Create and enter the context manager, keeping it alive
        self._context_manager = PostgresSaver.from_conn_string(connection_string)
        self._checkpointer = self._context_manager.__enter__()
        
        # Setup tables
        try:
            self._checkpointer.setup()
        except Exception:
            # Tables might already exist
            pass
    
    def response_exists(self, response_id: str) -> bool:
        """
        Check if a response exists by checking if its thread has checkpoints.
        For PostgreSQL, we check if we can find a checkpoint for this thread.
        """
        try:
            # Try to get checkpoint using response_id as thread_id
            config = {"configurable": {"thread_id": response_id}}
            result = self._checkpointer.get_tuple(config)
            return result is not None
        except Exception:
            return False
    
    def get_thread_for_response(self, response_id: str) -> Optional[str]:
        """
        Get the thread_id for a response.
        For PostgreSQL, we assume response_id IS the thread_id for backward compatibility.
        """
        # Check if a checkpoint exists with this response_id as thread_id
        if self.response_exists(response_id):
            return response_id
        return None
    
    def __getattr__(self, name):
        """Delegate all other methods to the real checkpointer"""
        return getattr(self._checkpointer, name)
    
    def __del__(self):
        """Clean up the connection when the wrapper is destroyed"""
        try:
            if hasattr(self, '_context_manager'):
                self._context_manager.__exit__(None, None, None)
        except:
            pass


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None