"""
Persistence and checkpointing for Responses API
Supports SQLite (local) and PostgreSQL (production/serverless)
"""
import os
import sqlite3
import warnings
import threading
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
    
    if db_url is not None:
        connection_string = db_url if db_url != "" else None
    else:
        connection_string = os.getenv("DATABASE_URL")
    
    if connection_string:
        validate_postgresql_url(connection_string)
        
        if not POSTGRES_AVAILABLE:
            raise DatabaseError(
                "PostgreSQL support not installed.\n"
                "Install with: pip install 'cortex[postgres]'\n"
                "Or: pip install langgraph-checkpoint-postgres psycopg[binary]"
            )
        
        try:
            print(f"✅ Connecting to PostgreSQL database...")
            
            wrapper = PostgresCheckpointerWrapper(connection_string)
            
            print(f"✅ Successfully connected to PostgreSQL")
            return wrapper
        except Exception as e:
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
    
    else:
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
        
        else:
            try:
                print(f"✅ Using SQLite for local persistence (conversations.db)")
                db_path = os.getenv("CORTEX_DB_PATH", "conversations.db")
                conn = sqlite3.connect(db_path, check_same_thread=False)
                return SmartCheckpointer(conn)
            except Exception as e:
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
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchone()
        self.db_path = db_info[2] if db_info else "conversations.db"
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
        
        cursor.execute(
            "SELECT was_stored FROM response_tracking WHERE response_id = ?",
            (response_id,)
        )
        
        result = cursor.fetchone()
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
        if "checkpoint_ns" not in config.get("configurable", {}):
            config.setdefault("configurable", {})["checkpoint_ns"] = ""
        
        store = config.get("configurable", {}).get("store", True)
        thread_id = config.get("configurable", {}).get("thread_id")
        response_id = config.get("configurable", {}).get("response_id")
        
        if store:
            result = super().put(config, checkpoint, metadata, new_versions)
            
            if response_id and thread_id:
                cursor = self.tracking_conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO response_tracking (response_id, thread_id, was_stored) VALUES (?, ?, ?)",
                    (response_id, thread_id, 1)
                )
                self.tracking_conn.commit()  
            
            return result
        else:
            if response_id and thread_id:
                cursor = self.tracking_conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO response_tracking (response_id, thread_id, was_stored) VALUES (?, ?, ?)",
                    (response_id, thread_id, 0)
                )
                self.tracking_conn.commit() 
            
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
            pass 
        
        if hasattr(super(), 'close'):
            super().close()


class PostgresCheckpointerWrapper:
    """
    Wrapper that maintains a PostgreSQL connection pool.
    This solves the context manager closing issue and adds custom methods.
    
    IMPORTANT: Automatically detects and handles pooled connections (Supabase, PgBouncer)
    by disabling prepared statements to avoid conflicts.
    """
    
    def __init__(self, connection_string: str):
        """Initialize and open the connection"""
        self.connection_string = connection_string
        
        self.is_pooled = ('pooler.supabase.com:6543' in connection_string or 
                         'pooler.supabase.com:5432' in connection_string or
                         ':6543' in connection_string)
        
        if self.is_pooled:
            print("📌 Detected connection pooler - disabling prepared statements")
            print(f"   Using exact URL: {connection_string[:60]}...")
        
        self._save_lock = threading.Lock() if self.is_pooled else None
        
        import psycopg
        
        self.connect_kwargs = {}
        if self.is_pooled:
            self.connect_kwargs['prepare_threshold'] = None  
            self.connect_kwargs['options'] = '-c statement_timeout=30000'  
        
        self._initialize_connection()
        
        try:
            self._checkpointer.setup()
        except Exception:
            pass
        
        import psycopg
        with psycopg.connect(connection_string, **self.connect_kwargs) as temp_conn:
            with temp_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS response_tracking (
                        response_id TEXT PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        was_stored BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            temp_conn.commit()
    
    def _initialize_connection(self):
        """Initialize or reinitialize the database connection"""
        import psycopg
        
        if self.is_pooled:
            conn = psycopg.connect(self.connection_string, **self.connect_kwargs)
            
            class PoolerSafePostgresSaver(PostgresSaver):
                """PostgresSaver that doesn't use pipeline mode (incompatible with poolers)"""
                
                def _cursor(self, *, pipeline: bool = False):
                    """Override to disable pipeline mode for pooled connections"""
                    return super()._cursor(pipeline=False)
            
            self._context_manager = PoolerSafePostgresSaver(conn)
            self._checkpointer = self._context_manager
            self._conn = conn
        else:
            self._context_manager = PostgresSaver.from_conn_string(self.connection_string)
            self._checkpointer = self._context_manager.__enter__()
            self._conn = None  
    
    def _ensure_connection_healthy(self):
        """Check connection health and reconnect if needed (for pooled connections)"""
        if not self.is_pooled:
            return 
        
        try:
            if self._conn and not self._conn.closed:
                with self._conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            else:
                raise Exception("Connection is closed")
        except Exception as e:
            print(f"   ⚠️ Connection lost ({str(e)[:50]}...), reconnecting...")
            try:
                if hasattr(self, '_conn') and self._conn:
                    try:
                        self._conn.close()
                    except:
                        pass
                
                self._initialize_connection()
                
                try:
                    self._checkpointer.setup()
                except:
                    pass
                
                print(f"   ✅ Reconnected successfully")
            except Exception as reconnect_error:
                print(f"   ❌ Reconnection failed: {reconnect_error}")
                raise
    
    def response_exists(self, response_id: str) -> bool:
        """
        Check if a response exists and was stored
        Uses fresh connection for pooler compatibility
        
        Args:
            response_id: The response_id to check
            
        Returns:
            True if exists and was stored, False otherwise
        """
        import psycopg
        
        with psycopg.connect(self.connection_string, **self.connect_kwargs) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT was_stored FROM response_tracking WHERE response_id = %s",
                    (response_id,)
                )
                
                result = cursor.fetchone()
                return result is not None and result[0] == True
    
    def track_response(self, response_id: str, thread_id: str, was_stored: bool = False):
        """
        Pre-emptively track a response for continuity (Option C)
        This ensures conversations can continue even if checkpoint save fails
        
        Args:
            response_id: The response ID to track
            thread_id: The thread ID this response belongs to  
            was_stored: Whether the checkpoint was successfully stored
        """
        import psycopg
        
        try:
            with psycopg.connect(self.connection_string, **self.connect_kwargs) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO response_tracking (response_id, thread_id, was_stored) "
                        "VALUES (%s, %s, %s) "
                        "ON CONFLICT (response_id) DO UPDATE SET "
                        "thread_id = EXCLUDED.thread_id, was_stored = EXCLUDED.was_stored",
                        (response_id, thread_id, was_stored)
                    )
                conn.commit()
        except Exception as e:
            print(f"   ⚠️ Failed to pre-track response: {e}")
    
    def get_thread_for_response(self, response_id: str) -> Optional[str]:
        """
        Get the thread_id that a response_id belongs to
        Uses fresh connection for pooler compatibility
        
        Args:
            response_id: The response_id to look up
            
        Returns:
            thread_id if found, None otherwise
        """
        import psycopg
        
        with psycopg.connect(self.connection_string, **self.connect_kwargs) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT thread_id FROM response_tracking WHERE response_id = %s",
                    (response_id,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
    
    def put(self, config, checkpoint, metadata, new_versions):
        """
        Override put to track response IDs in our tracking table
        Uses fresh connections for pooler compatibility
        """
        import psycopg
        
        if "checkpoint_ns" not in config.get("configurable", {}):
            config.setdefault("configurable", {})["checkpoint_ns"] = ""
        
        store = config.get("configurable", {}).get("store", True)
        thread_id = config.get("configurable", {}).get("thread_id")
        response_id = config.get("configurable", {}).get("response_id")
        
        if store:
            print(f"\n🔍 DEBUG: Attempting to save checkpoint:")
            print(f"   Thread ID: {thread_id}")
            print(f"   Response ID: {response_id}")
            print(f"   Config has checkpoint_ns: {'checkpoint_ns' in config.get('configurable', {})}")
            
            if self._save_lock:
                print(f"   🔒 Acquiring lock for pooled connection save...")
                self._save_lock.acquire()
                try:
                    self._ensure_connection_healthy()
                    
                    result = self._checkpointer.put(config, checkpoint, metadata, new_versions)
                    print(f"   ✅ PostgresSaver.put() returned successfully")
                    if self.is_pooled and hasattr(self._checkpointer, 'conn'):
                        self._checkpointer.conn.commit()
                        print(f"   ✅ Explicitly committed transaction for pooled connection")
                except Exception as e:
                    if self.is_pooled and ("SSL" in str(e) or "connection" in str(e).lower() or "closed" in str(e)):
                        print(f"   ⚠️ Connection error detected, attempting reconnection...")
                        self._ensure_connection_healthy()
                        try:
                            result = self._checkpointer.put(config, checkpoint, metadata, new_versions)
                            print(f"   ✅ PostgresSaver.put() succeeded after reconnection")
                            if self.is_pooled and hasattr(self._checkpointer, 'conn'):
                                self._checkpointer.conn.commit()
                                print(f"   ✅ Committed after reconnection")
                        except Exception as retry_error:
                            print(f"   ❌ PostgresSaver.put() failed even after reconnection: {retry_error}")
                            raise
                    else:
                        print(f"   ❌ PostgresSaver.put() failed: {e}")
                        raise
                finally:
                    self._save_lock.release()
                    print(f"   🔓 Released lock for pooled connection")
            else:
                self._ensure_connection_healthy()
                
                try:
                    result = self._checkpointer.put(config, checkpoint, metadata, new_versions)
                    print(f"   ✅ PostgresSaver.put() returned successfully")
                    
                    if self.is_pooled and hasattr(self._checkpointer, 'conn'):
                        self._checkpointer.conn.commit()
                        print(f"   ✅ Explicitly committed transaction for pooled connection")
                except Exception as e:
                    if self.is_pooled and ("SSL" in str(e) or "connection" in str(e).lower() or "closed" in str(e)):
                        print(f"   ⚠️ Connection error detected, attempting reconnection...")
                        self._ensure_connection_healthy()
                        try:
                            result = self._checkpointer.put(config, checkpoint, metadata, new_versions)
                            print(f"   ✅ PostgresSaver.put() succeeded after reconnection")
                            if self.is_pooled and hasattr(self._checkpointer, 'conn'):
                                self._checkpointer.conn.commit()
                                print(f"   ✅ Committed after reconnection")
                        except Exception as retry_error:
                            print(f"   ❌ PostgresSaver.put() failed even after reconnection: {retry_error}")
                            raise
                    else:
                        print(f"   ❌ PostgresSaver.put() failed: {e}")
                        raise
            
            if response_id and thread_id:
                with psycopg.connect(self.connection_string, **self.connect_kwargs) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO response_tracking (response_id, thread_id, was_stored) VALUES (%s, %s, %s) ON CONFLICT (response_id) DO UPDATE SET thread_id = EXCLUDED.thread_id, was_stored = EXCLUDED.was_stored",
                            (response_id, thread_id, True)
                        )
                    conn.commit()
            
            return result
        else:
            if response_id and thread_id:
                with psycopg.connect(self.connection_string, **self.connect_kwargs) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO response_tracking (response_id, thread_id, was_stored) VALUES (%s, %s, %s) ON CONFLICT (response_id) DO UPDATE SET thread_id = EXCLUDED.thread_id, was_stored = EXCLUDED.was_stored",
                            (response_id, thread_id, False)
                        )
                    conn.commit()
            
            return {
                "v": 1,
                "ts": checkpoint.get("ts", ""),
                "id": checkpoint.get("id", ""),
                "checkpoint": checkpoint,
                "metadata": metadata
            }
    
    def close(self):
        """
        No tracking connection to close anymore (using fresh connections)
        Main checkpointer cleanup handled in __del__
        """
        pass
    
    def __getattr__(self, name):
        """Delegate all other methods to the real checkpointer"""
        return getattr(self._checkpointer, name)
    
    def __del__(self):
        """Clean up the connection when the wrapper is destroyed"""
        try:
            self.close()
        except:
            pass
        
        try:
            if hasattr(self, '_conn') and self._conn:
                try:
                    self._conn.close()
                except:
                    pass
            
            if hasattr(self, '_context_manager'):
                if not self.is_pooled:
                    self._context_manager.__exit__(None, None, None)
                else:
                    if hasattr(self._checkpointer, 'conn'):
                        try:
                            self._checkpointer.conn.close()
                        except:
                            pass
        except:
            pass


def get_no_op_checkpointer() -> None:
    """
    Returns None - used when store=False
    Graph compiled without checkpointer won't persist
    """
    return None