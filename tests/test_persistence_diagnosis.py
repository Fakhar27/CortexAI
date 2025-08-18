"""
Diagnostic test to identify persistence issues with PostgreSQL
This test will help us understand why conversations aren't being retrieved
"""
import os
import sys
import time
import json
from cortex import Client
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
from psycopg.rows import dict_row

# PostgreSQL connection URL (Docker)
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"

def direct_db_check(connection_string):
    """Directly check what's in the database"""
    print("\n=== DIRECT DATABASE CHECK ===")
    try:
        with psycopg.connect(connection_string, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Check if checkpoints table exists
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                print(f"✓ Tables in database: {[t['table_name'] for t in tables]}")
                
                # Check checkpoints table
                if any(t['table_name'] == 'checkpoints' for t in tables):
                    cur.execute("SELECT COUNT(*) as count FROM checkpoints")
                    count = cur.fetchone()
                    print(f"✓ Checkpoints count: {count['count']}")
                    
                    # Get recent checkpoints
                    cur.execute("""
                        SELECT thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id
                        FROM checkpoints
                        ORDER BY checkpoint_id DESC
                        LIMIT 5
                    """)
                    checkpoints = cur.fetchall()
                    print(f"✓ Recent checkpoints:")
                    for cp in checkpoints:
                        print(f"  - Thread: {cp['thread_id']}, NS: {cp['checkpoint_ns']}, ID: {cp['checkpoint_id']}")
                
                # Check checkpoint_writes table
                if any(t['table_name'] == 'checkpoint_writes' for t in tables):
                    cur.execute("SELECT COUNT(*) as count FROM checkpoint_writes")
                    count = cur.fetchone()
                    print(f"✓ Checkpoint writes count: {count['count']}")
                    
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def test_persistence_mechanism():
    """Test the persistence mechanism step by step"""
    print("\n" + "="*60)
    print("PERSISTENCE DIAGNOSIS TEST")
    print("="*60)
    
    # First, check database directly
    direct_db_check(DOCKER_POSTGRES_URL)
    
    print("\n=== STEP 1: Create initial response ===")
    client1 = Client(db_url=DOCKER_POSTGRES_URL)
    
    response1 = client1.create(
        model="gpt-4o-mini",
        input="Test message: What is 2+2?",
        temperature=0.0
    )
    
    print(f"✓ Created response: {response1['id']}")
    print(f"  Status: {response1['status']}")
    print(f"  Thread ID: {response1.get('thread_id', 'NOT SET')}")
    print(f"  Content preview: {response1['content'][:100] if response1.get('content') else 'NO CONTENT'}")
    
    # Check database after creation
    print("\n=== Database state after first response ===")
    direct_db_check(DOCKER_POSTGRES_URL)
    
    print("\n=== STEP 2: Continue conversation (same client) ===")
    response2 = client1.create(
        model="gpt-4o-mini",
        input="Multiply that by 10",
        previous_response_id=response1["id"],
        temperature=0.0
    )
    
    print(f"✓ Created continuation: {response2['id']}")
    print(f"  Status: {response2['status']}")
    print(f"  Previous ID: {response2.get('previous_response_id', 'NOT SET')}")
    print(f"  Thread ID: {response2.get('thread_id', 'NOT SET')}")
    
    # Check if thread_ids match
    if response1.get('thread_id') == response2.get('thread_id'):
        print(f"✓ Thread IDs match: {response1.get('thread_id')}")
    else:
        print(f"❌ Thread ID mismatch! R1: {response1.get('thread_id')}, R2: {response2.get('thread_id')}")
    
    print("\n=== STEP 3: Test retrieval with new client ===")
    # Delete first client to ensure we're testing persistence
    del client1
    time.sleep(1)  # Give time for any pending writes
    
    # Check database before new client
    print("\n=== Database state before new client ===")
    direct_db_check(DOCKER_POSTGRES_URL)
    
    # Create new client
    client2 = Client(db_url=DOCKER_POSTGRES_URL)
    
    print(f"\nAttempting to continue from response: {response2['id']}")
    print(f"Expected thread_id: {response2.get('thread_id')}")
    
    try:
        response3 = client2.create(
            model="gpt-4o-mini",
            input="What was the original calculation?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        
        print(f"✓ Created response3: {response3['id']}")
        print(f"  Status: {response3['status']}")
        print(f"  Thread ID: {response3.get('thread_id')}")
        
        if response3["status"] == "completed":
            print("✅ PERSISTENCE WORKS!")
            print(f"  Content: {response3.get('content', '')[:200]}")
        else:
            print("❌ PERSISTENCE FAILED!")
            print(f"  Error: {response3.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during retrieval: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== STEP 4: Check thread continuity ===")
    # Try to manually check if we can load the thread
    try:
        from cortex.responses.persistence import get_checkpointer
        checkpointer = get_checkpointer(db_url=DOCKER_POSTGRES_URL)
        
        if hasattr(checkpointer, 'list'):
            # Try to list checkpoints for the thread
            thread_id = response2.get('thread_id')
            if thread_id:
                print(f"Checking thread: {thread_id}")
                checkpoints = list(checkpointer.list({"configurable": {"thread_id": thread_id}}))
                print(f"✓ Found {len(checkpoints)} checkpoints for thread")
                for i, cp in enumerate(checkpoints[:3]):
                    print(f"  Checkpoint {i}: {cp}")
        
    except Exception as e:
        print(f"❌ Failed to check thread: {e}")
    
    print("\n=== FINAL DATABASE STATE ===")
    direct_db_check(DOCKER_POSTGRES_URL)
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    # Ensure we have the PostgreSQL URL
    if not DOCKER_POSTGRES_URL:
        print("❌ No PostgreSQL URL configured")
        sys.exit(1)
    
    # Run the diagnosis
    try:
        test_persistence_mechanism()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()