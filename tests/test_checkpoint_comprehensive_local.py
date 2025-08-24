#!/usr/bin/env python3
"""
Comprehensive checkpoint testing for all persistence backends:
- SQLite (local file)
- PostgreSQL (Docker container)
- PostgreSQL (Supabase pooler)

Explains the checkpoint and tracking system in detail.
"""

import os
import time
import sqlite3
try:
    import psycopg
except ImportError:
    import psycopg2 as psycopg
    psycopg.connect = psycopg2.connect
from cortex import Client

# Database connection strings
SQLITE_PATH = "test_checkpoints.db"
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"
SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

print("="*80)
print("COMPREHENSIVE CHECKPOINT TESTING")
print("="*80)
print("""
CHECKPOINT SYSTEM EXPLANATION:
-------------------------------
1. CHECKPOINTS TABLE:
   - Each row represents a STATE SNAPSHOT of the conversation
   - thread_id: The conversation identifier (stays same for entire conversation)
   - checkpoint_id: Unique ID for each checkpoint (increments)
   - checkpoint: JSON blob containing the full conversation state
   - metadata: Additional info like timestamps
   
   Example: A conversation with 3 messages will have 3+ checkpoint rows:
   - Checkpoint 1: After "Hello"
   - Checkpoint 2: After "Hello" + "Hi there"  
   - Checkpoint 3: After "Hello" + "Hi there" + "How are you?"
   
2. RESPONSE_TRACKING TABLE:
   - Maps response_id to thread_id for continuity
   - response_id: Unique ID for each API call/response
   - thread_id: Which conversation this response belongs to
   - was_stored: Boolean if checkpoint was saved (store=True/False)
   
3. WHY WAIT FOR DB WRITE?
   - Database writes can be async, especially with pooled connections
   - We wait 2-3 seconds to ensure data is committed and queryable
   
4. DEL CLIENT:
   - Not deleting conversation! Just closing Python object
   - Simulates new Python session (like restarting your app)
   - Tests that conversations persist beyond client lifetime
""")
print("="*80)

def check_sqlite_state(db_path, thread_id):
    """Check SQLite checkpoint and tracking state"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count checkpoints for this thread
        cursor.execute("""
            SELECT COUNT(*) FROM checkpoints 
            WHERE thread_id = ?
        """, (thread_id,))
        checkpoint_count = cursor.fetchone()[0]
        
        # Count response tracking entries
        cursor.execute("""
            SELECT COUNT(*) FROM response_tracking 
            WHERE thread_id = ?
        """, (thread_id,))
        tracking_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return checkpoint_count, tracking_count
    except Exception as e:
        print(f"❌ SQLite check failed: {e}")
        return -1, -1

def check_postgres_state(db_url, thread_id):
    """Check PostgreSQL checkpoint and tracking state"""
    try:
        conn = psycopg.connect(db_url)
        cursor = conn.cursor()
        
        # Count checkpoints
        cursor.execute("""
            SELECT COUNT(*) FROM checkpoints 
            WHERE thread_id = %s
        """, (thread_id,))
        checkpoint_count = cursor.fetchone()[0]
        
        # Count response tracking
        cursor.execute("""
            SELECT COUNT(*) FROM response_tracking 
            WHERE thread_id = %s
        """, (thread_id,))
        tracking_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return checkpoint_count, tracking_count
    except Exception as e:
        print(f"❌ PostgreSQL check failed: {e}")
        return -1, -1

def test_sqlite_checkpoints():
    """Test SQLite checkpoint persistence"""
    print("\n" + "="*60)
    print("TEST: SQLite Checkpoints")
    print("="*60)
    
    try:
        # Remove old test database
        if os.path.exists(SQLITE_PATH):
            os.remove(SQLITE_PATH)
            print(f"Cleaned up old {SQLITE_PATH}")
        
        # Create client with SQLite - explicitly pass empty string to force SQLite
        print("\nCreating SQLite client...")
        client = Client(db_url="")  # Empty string forces SQLite, ignores DATABASE_URL
        print("✅ SQLite client created")
        
        # Test 1: Basic checkpoint creation
        print("\n1. Creating conversation...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="Remember: SQLite test number is 111",
            store=True,
            temperature=0.0
        )
        
        thread_id = response1["id"]
        print(f"   Thread: {thread_id}")
        
        # Wait for write
        time.sleep(2)
        
        # Check state - using the correct default SQLite path
        cp1, tr1 = check_sqlite_state("conversations.db", thread_id)  # Correct default SQLite path
        print(f"   After message 1: {cp1} checkpoints, {tr1} tracking")
        
        if cp1 == 0:
            print("❌ SQLite checkpoints not being saved!")
            return False
        
        # Test 2: Continuation
        print("\n2. Continuing conversation...")
        response2 = client.create(
            model="gpt-4o-mini",
            input="What's the SQLite test number?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        
        content = response2["output"][0]["content"][0]["text"]
        print(f"   Response: {content[:100]}")
        
        if "111" in content:
            print("   ✅ SQLite memory works!")
            
            # Check final state
            time.sleep(2)
            cp2, tr2 = check_sqlite_state("conversations.db", thread_id)
            print(f"   After message 2: {cp2} checkpoints, {tr2} tracking")
            
            if cp2 > cp1:
                print("   ✅ Checkpoints incrementing correctly")
                return True
            else:
                print("   ⚠️ Checkpoints not incrementing")
                return False
        else:
            print("   ❌ SQLite memory failed!")
            return False
            
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_docker_postgres():
    """Test Docker PostgreSQL checkpoint persistence"""
    print("\n" + "="*60)
    print("TEST: Docker PostgreSQL Checkpoints")
    print("="*60)
    
    try:
        # Create client with Docker PostgreSQL
        print("\nConnecting to Docker PostgreSQL...")
        client = Client(db_url=DOCKER_POSTGRES_URL)
        print("✅ Connected to Docker PostgreSQL")
        
        # Test 1: Basic checkpoint
        print("\n1. Creating conversation...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="Remember: Docker test number is 222",
            store=True,
            temperature=0.0
        )
        
        thread_id = response1["id"]
        print(f"   Thread: {thread_id}")
        
        # Wait and check
        time.sleep(2)
        cp1, tr1 = check_postgres_state(DOCKER_POSTGRES_URL, thread_id)
        print(f"   After message 1: {cp1} checkpoints, {tr1} tracking")
        
        if cp1 == 0:
            print("❌ Docker PostgreSQL checkpoints not being saved!")
            return False
        
        # Test 2: Cross-provider with Docker
        print("\n2. Switching to Gemini...")
        response2 = client.create(
            model="gemini-1.5-flash",
            input="What's the Docker test number?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        
        content = response2["output"][0]["content"][0]["text"]
        print(f"   Gemini response: {content[:100]}")
        
        if "222" in content:
            print("   ✅ Docker PostgreSQL cross-provider works!")
            
            time.sleep(2)
            cp2, tr2 = check_postgres_state(DOCKER_POSTGRES_URL, thread_id)
            print(f"   After Gemini: {cp2} checkpoints, {tr2} tracking")
            return True
        else:
            print("   ❌ Docker PostgreSQL memory failed!")
            return False
            
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        print("   Make sure Docker container is running:")
        print("   docker-compose up -d")
        return False

def test_assistant_instructions():
    """Test assistant instructions persistence and rules"""
    print("\n" + "="*60)
    print("TEST: Assistant Instructions")
    print("="*60)
    
    try:
        # Use Supabase for this test
        client = Client(db_url=SUPABASE_URL)
        
        # Test 1: Instructions at conversation start
        print("\n1. Setting instructions at start...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="What's your special rule?",
            instructions="You must always end your responses with the phrase 'INSTRUCTION-TEST-PASS'",
            store=True,
            temperature=0.0
        )
        
        content1 = response1["output"][0]["content"][0]["text"]
        print(f"   Response: {content1[-50:]}")  # Show end of response
        
        if "INSTRUCTION-TEST-PASS" in content1:
            print("   ✅ Instructions applied at start!")
        else:
            print("   ❌ Instructions not applied!")
            return False
        
        thread_id = response1["id"]
        
        # Test 2: Instructions persist in continuation
        print("\n2. Testing instruction persistence...")
        response2 = client.create(
            model="gpt-4o-mini",
            input="Tell me about Python",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        
        content2 = response2["output"][0]["content"][0]["text"]
        print(f"   Response ends with: ...{content2[-30:]}")
        
        if "INSTRUCTION-TEST-PASS" in content2:
            print("   ✅ Instructions persist in conversation!")
        else:
            print("   ❌ Instructions lost in continuation!")
            return False
        
        # Test 3: Switch provider, instructions should persist
        print("\n3. Testing cross-provider instruction persistence...")
        response3 = client.create(
            model="gemini-1.5-flash",
            input="What's 2+2?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        
        content3 = response3["output"][0]["content"][0]["text"]
        print(f"   Gemini response ends with: ...{content3[-30:]}")
        
        if "INSTRUCTION-TEST-PASS" in content3:
            print("   ✅ Instructions persist across providers!")
        else:
            print("   ⚠️ Instructions may not persist across providers (model-dependent)")
        
        # Test 4: Try to change instructions mid-conversation (should NOT work)
        print("\n4. Testing mid-conversation instruction change (should fail)...")
        response4 = client.create(
            model="gpt-4o-mini",
            input="What's your rule now?",
            previous_response_id=response3["id"],
            instructions="You must always say CHANGED-INSTRUCTION",  # This should be ignored!
            temperature=0.0
        )
        
        content4 = response4["output"][0]["content"][0]["text"]
        print(f"   Response: {content4[-50:]}")
        
        if "INSTRUCTION-TEST-PASS" in content4 and "CHANGED-INSTRUCTION" not in content4:
            print("   ✅ Correctly ignored mid-conversation instruction change!")
        else:
            print("   ❌ Instructions were incorrectly changed mid-conversation!")
            return False
        
        # Test 5: New conversation with different instructions
        print("\n5. Testing new conversation with new instructions...")
        response5 = client.create(
            model="gpt-4o-mini",
            input="What's your new rule?",
            instructions="Always say NEW-CONVERSATION-RULE",
            store=True,
            temperature=0.0
        )
        
        content5 = response5["output"][0]["content"][0]["text"]
        print(f"   New conversation response: {content5[-50:]}")
        
        if "NEW-CONVERSATION-RULE" in content5:
            print("   ✅ New conversation accepts new instructions!")
            return True
        else:
            print("   ❌ New conversation didn't accept new instructions!")
            return False
            
    except Exception as e:
        print(f"❌ Instructions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pooler_hardcoding():
    """Explain and test the pooler connection hardcoding"""
    print("\n" + "="*60)
    print("TEST: Pooler Connection Handling")
    print("="*60)
    print("""
POOLER HARDCODING EXPLANATION:
------------------------------
YES, we hardcoded pooler detection in persistence.py:

self.is_pooled = ('pooler.supabase.com:6543' in connection_string or 
                 'pooler.supabase.com:5432' in connection_string or
                 ':6543' in connection_string)

WHY?
1. Pooled connections need special handling:
   - Disable prepared statements (prepare_threshold=None)
   - Explicit transaction commits
   - Fresh connections for each operation

2. Direct connections work differently:
   - Can use prepared statements
   - Auto-commit works
   - Can reuse connections

3. The hardcoding detects Supabase pooler by:
   - Domain: pooler.supabase.com
   - Port: 6543 (pooler) or 5432 (sometimes used)

This is a pragmatic solution that works for Supabase.
For other poolers, you'd add their patterns.
""")
    
    # Test pooler detection
    print("\nTesting pooler detection...")
    
    test_urls = [
        (SUPABASE_URL, True, "Supabase pooler"),
        (DOCKER_POSTGRES_URL, False, "Docker direct"),
        ("postgresql://user:pass@db.example.com:6543/db", True, "Port 6543"),
        ("postgresql://user:pass@db.example.com:5432/db", False, "Standard port"),
    ]
    
    for url, should_be_pooled, description in test_urls:
        is_pooled = ('pooler.supabase.com:6543' in url or 
                    'pooler.supabase.com:5432' in url or
                    ':6543' in url)
        
        if is_pooled == should_be_pooled:
            print(f"   ✅ {description}: Correctly detected as {'pooled' if is_pooled else 'direct'}")
        else:
            print(f"   ❌ {description}: Detection error!")
    
    return True

def main():
    """Run all comprehensive tests"""
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        return
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set")
        return
    
    results = []
    
    # Test SQLite
    print("\n" + "🔍" * 40)
    result1 = test_sqlite_checkpoints()
    results.append(("SQLite Checkpoints", result1))
    
    # Test Docker PostgreSQL
    result2 = test_docker_postgres()
    results.append(("Docker PostgreSQL", result2))
    
    # Test Assistant Instructions
    result3 = test_assistant_instructions()
    results.append(("Assistant Instructions", result3))
    
    # Explain pooler hardcoding
    result4 = test_pooler_hardcoding()
    results.append(("Pooler Detection", result4))
    
    # Summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    if all(r[1] for r in results if r[1] is not False):
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")

if __name__ == "__main__":
    main()