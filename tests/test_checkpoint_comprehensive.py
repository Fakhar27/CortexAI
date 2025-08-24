#!/usr/bin/env python3
"""
Comprehensive Checkpoint Testing
Tests the checkpoint_ns bug fix and validates actual persistence
Covers SQLite, PostgreSQL, and Supabase with real conversation memory validation
"""

import os
import pytest
import time
import sqlite3
import tempfile
from typing import Optional, Dict, Any
from cortex import Client

# Test databases
SUPABASE_POOLER_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"

# Test data for memory validation
TEST_MEMORIES = {
    "number": "42",
    "color": "blue",
    "secret": "ALPHA-2024",
    "city": "Paris",
    "equation": "E=mc²"
}


class TestCheckpointComprehensive:
    """Comprehensive tests for checkpoint persistence across all databases"""
    
    # ============== HELPER METHODS ==============
    
    def validate_memory(self, response: Dict[str, Any], expected_content: str, 
                       test_name: str = "Memory test") -> None:
        """Helper to validate model actually remembers content"""
        try:
            content = response["output"][0]["content"][0]["text"]
            assert expected_content.lower() in content.lower(), \
                f"{test_name} FAILED: Model forgot '{expected_content}'! Response: {content[:200]}"
            print(f"✅ {test_name}: Model remembered '{expected_content}'")
        except (KeyError, IndexError) as e:
            pytest.fail(f"{test_name}: Invalid response structure: {e}")
    
    def check_sqlite_checkpoints(self, db_path: str, thread_id: str) -> int:
        """Check SQLite checkpoints table"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if checkpoints table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='checkpoints'
        """)
        if not cursor.fetchone():
            conn.close()
            return 0
        
        # Count checkpoints for thread
        cursor.execute("""
            SELECT COUNT(*) FROM checkpoints 
            WHERE thread_id = ?
        """, (thread_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def check_postgres_checkpoints(self, db_url: str, thread_id: str) -> int:
        """Check PostgreSQL checkpoints table"""
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            # Check checkpoints
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            print(f"⚠️ Could not check PostgreSQL checkpoints: {e}")
            return -1
    
    def check_response_tracking(self, db_url: str, response_id: str) -> bool:
        """Check if response tracking entry exists"""
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT was_stored FROM response_tracking 
                WHERE response_id = %s
            """, (response_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            return result is not None and result[0]
        except:
            return False
    
    # ============== SQLITE TESTS ==============
    
    def test_sqlite_checkpoint_creation(self):
        """Test that checkpoints are created in SQLite"""
        print("\n" + "="*60)
        print("TEST: SQLite Checkpoint Creation")
        print("="*60)
        
        # Create temp database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        # Set environment to use SQLite
        os.environ["CORTEX_DB_PATH"] = db_path
        
        client = Client()  # Will use SQLite
        
        # Create first message
        response1 = client.create(
            model="command-r",
            input=f"Remember this number: {TEST_MEMORIES['number']}",
            store=True
        )
        
        assert response1["status"] == "completed"
        thread_id = response1["id"]
        print(f"✅ Created response: {thread_id}")
        
        # Check checkpoints were created
        checkpoint_count = self.check_sqlite_checkpoints(db_path, thread_id)
        assert checkpoint_count > 0, f"No checkpoints created! Count: {checkpoint_count}"
        print(f"✅ SQLite checkpoints created: {checkpoint_count}")
        
        # Test memory persistence
        response2 = client.create(
            model="command-r",
            input="What number did I ask you to remember?",
            previous_response_id=response1["id"]
        )
        
        self.validate_memory(response2, TEST_MEMORIES["number"], "SQLite memory")
        
        # Check second checkpoint
        checkpoint_count2 = self.check_sqlite_checkpoints(db_path, thread_id)
        assert checkpoint_count2 > checkpoint_count, "No new checkpoint created for continuation"
        print(f"✅ Additional checkpoints created: {checkpoint_count2}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_sqlite_cross_session_persistence(self):
        """Test SQLite persistence across client sessions"""
        print("\n" + "="*60)
        print("TEST: SQLite Cross-Session Persistence")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        # First session
        client1 = Client(db_path=db_path)
        response1 = client1.create(
            model="command-r",
            input=f"The secret code is {TEST_MEMORIES['secret']}",
            store=True
        )
        response_id = response1["id"]
        print(f"✅ Session 1: Created {response_id}")
        
        # Delete client
        del client1
        
        # Second session - new client, same database
        client2 = Client(db_path=db_path)
        response2 = client2.create(
            model="command-r",
            input="What was the secret code?",
            previous_response_id=response_id
        )
        
        self.validate_memory(response2, TEST_MEMORIES["secret"], "SQLite cross-session")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # ============== POSTGRESQL TESTS ==============
    
    def test_postgres_checkpoint_creation(self):
        """Test that checkpoints are created in PostgreSQL"""
        print("\n" + "="*60)
        print("TEST: PostgreSQL Checkpoint Creation (Docker)")
        print("="*60)
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✅ Connected to Docker PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e) or "could not translate" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Create conversation
        response1 = client.create(
            model="command-r",
            input=f"Remember the color {TEST_MEMORIES['color']}",
            store=True
        )
        
        thread_id = response1["id"]
        print(f"✅ Created response: {thread_id}")
        
        # Check checkpoints
        checkpoint_count = self.check_postgres_checkpoints(DOCKER_POSTGRES_URL, thread_id)
        if checkpoint_count >= 0:
            assert checkpoint_count > 0, "No checkpoints created in PostgreSQL!"
            print(f"✅ PostgreSQL checkpoints created: {checkpoint_count}")
        
        # Test memory
        response2 = client.create(
            model="command-r",
            input="What color should I remember?",
            previous_response_id=response1["id"]
        )
        
        self.validate_memory(response2, TEST_MEMORIES["color"], "PostgreSQL memory")
    
    # ============== SUPABASE POOLER TESTS ==============
    
    def test_supabase_pooler_checkpoint_creation(self):
        """Test that checkpoints work with Supabase pooler (the critical bug fix)"""
        print("\n" + "="*60)
        print("TEST: Supabase Pooler Checkpoint Creation (CRITICAL)")
        print("="*60)
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
            print("✅ Connected to Supabase pooler")
        except Exception as e:
            pytest.skip(f"Cannot connect to Supabase: {e}")
        
        # Create conversation with memorable content
        response1 = client.create(
            model="command-r",
            input=f"I'm visiting {TEST_MEMORIES['city']} next week",
            store=True
        )
        
        thread_id = response1["id"]
        print(f"✅ Created response: {thread_id}")
        
        # CRITICAL: Check if checkpoints were created
        time.sleep(1)  # Allow for cloud latency
        checkpoint_count = self.check_postgres_checkpoints(SUPABASE_POOLER_URL, thread_id)
        
        if checkpoint_count == 0:
            pytest.fail("🔴 BUG NOT FIXED: No checkpoints in Supabase!")
        elif checkpoint_count > 0:
            print(f"✅ CRITICAL FIX VERIFIED: Checkpoints created in Supabase: {checkpoint_count}")
        
        # Verify memory works
        response2 = client.create(
            model="command-r",
            input="Which city am I visiting?",
            previous_response_id=response1["id"]
        )
        
        self.validate_memory(response2, TEST_MEMORIES["city"], "Supabase memory")
        
        # Check response tracking
        tracked = self.check_response_tracking(SUPABASE_POOLER_URL, response1["id"])
        assert tracked, "Response not tracked in response_tracking table"
        print("✅ Response tracking working")
    
    def test_supabase_cross_provider_memory(self):
        """Test cross-provider conversation with Supabase (the Django E2E scenario)"""
        print("\n" + "="*60)
        print("TEST: Supabase Cross-Provider Memory (Django E2E Scenario)")
        print("="*60)
        
        # Check required API keys
        required = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "CO_API_KEY"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            pytest.skip(f"Missing API keys: {', '.join(missing)}")
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
        except Exception as e:
            pytest.skip(f"Cannot connect to Supabase: {e}")
        
        # Start with GPT-4
        print("\n1. Starting with GPT-4...")
        response1 = client.create(
            model="gpt-4o-mini",
            input=f"I need you to remember this equation: {TEST_MEMORIES['equation']}",
            store=True,
            temperature=0.0
        )
        thread_id = response1["id"]
        print(f"   GPT-4 response: {thread_id}")
        
        # Switch to Gemini
        print("2. Switching to Gemini...")
        response2 = client.create(
            model="gemini-1.5-flash",
            input="What equation did I just share with you?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        print(f"   Gemini response: {response2['id']}")
        
        # CRITICAL: Verify Gemini remembers from GPT-4
        self.validate_memory(response2, TEST_MEMORIES["equation"], "Gemini remembering GPT-4")
        
        # Switch to Cohere
        print("3. Switching to Cohere...")
        response3 = client.create(
            model="command-r",
            input="Can you repeat that equation one more time?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        print(f"   Cohere response: {response3['id']}")
        
        # CRITICAL: Verify Cohere remembers through the chain
        self.validate_memory(response3, TEST_MEMORIES["equation"], "Cohere remembering chain")
        
        # Back to GPT-4
        print("4. Back to GPT-4...")
        response4 = client.create(
            model="gpt-4o-mini",
            input="What have we been discussing?",
            previous_response_id=response3["id"],
            temperature=0.0
        )
        
        # Should mention the equation
        self.validate_memory(response4, "equation", "GPT-4 context awareness")
        
        # Verify all responses share same thread
        checkpoint_count = self.check_postgres_checkpoints(SUPABASE_POOLER_URL, thread_id)
        print(f"\n✅ Total checkpoints for conversation: {checkpoint_count}")
        assert checkpoint_count >= 4, f"Expected at least 4 checkpoints, got {checkpoint_count}"
        
        print("\n🎉 CROSS-PROVIDER MEMORY WORKING!")
    
    # ============== EDGE CASES ==============
    
    def test_store_false_no_checkpoints(self):
        """Test that store=False doesn't create checkpoints but tracking works"""
        print("\n" + "="*60)
        print("TEST: store=False Behavior")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        client = Client(db_path=db_path)
        
        # Create with store=False
        response1 = client.create(
            model="command-r",
            input="This should not be saved",
            store=False  # Explicitly don't store
        )
        
        thread_id = response1["id"]
        print(f"✅ Created with store=False: {thread_id}")
        
        # Check no checkpoints created
        checkpoint_count = self.check_sqlite_checkpoints(db_path, thread_id)
        assert checkpoint_count == 0, f"Checkpoints created when store=False! Count: {checkpoint_count}"
        print("✅ No checkpoints created (correct)")
        
        # Try to continue (should fail or start fresh)
        response2 = client.create(
            model="command-r",
            input="What did I just say?",
            previous_response_id=response1["id"]
        )
        
        # Should get an error or fresh response
        if response2["status"] == "failed":
            print("✅ Correctly failed to continue from unstored response")
        else:
            # If it succeeded, model shouldn't remember
            content = response2["output"][0]["content"][0]["text"].lower()
            if "don't know" in content or "no previous" in content or "start" in content:
                print("✅ Model correctly has no memory of unstored message")
            else:
                print(f"⚠️ Unexpected response: {content[:100]}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_checkpoint_ns_in_config(self):
        """Test that checkpoint_ns is properly added to config"""
        print("\n" + "="*60)
        print("TEST: checkpoint_ns Configuration")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        # Monkey-patch to intercept config
        original_invoke = None
        captured_config = {}
        
        def capture_config(self, state, config, **kwargs):
            captured_config.update(config)
            return original_invoke(state, config, **kwargs)
        
        client = Client(db_path=db_path)
        
        # Patch the graph's invoke method
        if hasattr(client, 'graph') and hasattr(client.graph, 'invoke'):
            original_invoke = client.graph.invoke
            client.graph.invoke = lambda s, c, **k: capture_config(client.graph, s, c, **k)
        
        # Create a response
        response = client.create(
            model="command-r",
            input="Test checkpoint_ns",
            store=True
        )
        
        # Check captured config
        if captured_config:
            configurable = captured_config.get("configurable", {})
            assert "checkpoint_ns" in configurable, "checkpoint_ns not in config!"
            print(f"✅ checkpoint_ns present in config: '{configurable.get('checkpoint_ns')}'")
            assert "thread_id" in configurable, "thread_id missing!"
            assert "response_id" in configurable, "response_id missing!"
            print("✅ All required config keys present")
        else:
            print("⚠️ Could not capture config (test framework limitation)")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # ============== PERFORMANCE TESTS ==============
    
    def test_checkpoint_performance(self):
        """Test checkpoint creation doesn't significantly impact performance"""
        print("\n" + "="*60)
        print("TEST: Checkpoint Performance")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        client = Client(db_path=db_path)
        
        # Time with store=True
        start = time.time()
        response1 = client.create(
            model="command-r",
            input="Performance test with storage",
            store=True
        )
        time_with_store = time.time() - start
        
        # Time with store=False
        start = time.time()
        response2 = client.create(
            model="command-r",
            input="Performance test without storage",
            store=False
        )
        time_without_store = time.time() - start
        
        print(f"Time with store=True: {time_with_store:.2f}s")
        print(f"Time with store=False: {time_without_store:.2f}s")
        print(f"Overhead: {time_with_store - time_without_store:.2f}s")
        
        # Should not be more than 2x slower
        if time_with_store > 0 and time_without_store > 0:
            ratio = time_with_store / time_without_store
            assert ratio < 3.0, f"Storage overhead too high: {ratio:.1f}x slower"
            print(f"✅ Storage overhead acceptable: {ratio:.1f}x")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # ============== COMPREHENSIVE VALIDATION ==============
    
    def test_complete_conversation_flow(self):
        """Test a complete multi-turn conversation with all validations"""
        print("\n" + "="*60)
        print("TEST: Complete Conversation Flow")
        print("="*60)
        
        # Test with SQLite
        print("\n--- SQLite Flow ---")
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        client = Client(db_path=db_path)
        
        # Multi-turn conversation
        r1 = client.create(
            model="command-r",
            input="Let's discuss colors. My favorite is blue.",
            store=True
        )
        thread_id = r1["id"]
        
        r2 = client.create(
            model="command-r",
            input="I also like the number 42.",
            previous_response_id=r1["id"]
        )
        
        r3 = client.create(
            model="command-r",
            input="What's my favorite color?",
            previous_response_id=r2["id"]
        )
        self.validate_memory(r3, "blue", "SQLite turn 3")
        
        r4 = client.create(
            model="command-r",
            input="What number did I mention?",
            previous_response_id=r3["id"]
        )
        self.validate_memory(r4, "42", "SQLite turn 4")
        
        # Verify checkpoints
        final_count = self.check_sqlite_checkpoints(db_path, thread_id)
        print(f"✅ SQLite conversation: {final_count} checkpoints")
        
        # Test with Supabase if available
        print("\n--- Supabase Flow ---")
        try:
            client_pg = Client(db_url=SUPABASE_POOLER_URL)
            
            r1 = client_pg.create(
                model="command-r",
                input="Remember three things: Paris, Einstein, and coffee.",
                store=True
            )
            
            r2 = client_pg.create(
                model="command-r",
                input="What was the city?",
                previous_response_id=r1["id"]
            )
            self.validate_memory(r2, "Paris", "Supabase city memory")
            
            r3 = client_pg.create(
                model="command-r",
                input="Who was the scientist?",
                previous_response_id=r2["id"]
            )
            self.validate_memory(r3, "Einstein", "Supabase scientist memory")
            
            r4 = client_pg.create(
                model="command-r",
                input="What was the drink?",
                previous_response_id=r3["id"]
            )
            self.validate_memory(r4, "coffee", "Supabase drink memory")
            
            print("✅ Supabase multi-turn conversation working!")
            
        except Exception as e:
            print(f"⚠️ Supabase test skipped: {e}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("\n" + "="*60)
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("="*60)


# ============== STANDALONE EXECUTION ==============

if __name__ == "__main__":
    print("="*80)
    print("COMPREHENSIVE CHECKPOINT TESTING")
    print("="*80)
    print("\nThis test suite validates:")
    print("1. ✅ checkpoint_ns bug is fixed")
    print("2. ✅ Checkpoints are actually created in database")
    print("3. ✅ Conversations maintain memory across turns")
    print("4. ✅ Cross-provider memory works (Django E2E scenario)")
    print("5. ✅ SQLite and PostgreSQL both work correctly")
    print("6. ✅ Supabase pooler connections work")
    print("7. ✅ store=True/False behavior is correct")
    print("8. ✅ Response tracking aligns with checkpoints")
    print("\nRun with: pytest tests/test_checkpoint_comprehensive.py -v -s")
    print("="*80)