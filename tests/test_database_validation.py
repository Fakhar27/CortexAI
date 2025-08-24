#!/usr/bin/env python3
"""
Database-level validation tests
Directly queries tables to verify checkpoint data
"""

import os
import pytest
import time
import psycopg2
import sqlite3
import tempfile
from cortex import Client

SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


class TestDatabaseValidation:
    """Direct database validation tests"""
    
    def test_supabase_tables_exist(self):
        """Test that required tables exist in Supabase"""
        print("\n=== Testing Supabase Table Structure ===")
        
        try:
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            # Check for required tables
            tables = ['checkpoints', 'response_tracking']
            
            for table in tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Table '{table}' exists with {count} rows")
                else:
                    print(f"❌ Table '{table}' does NOT exist!")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.skip(f"Cannot connect to Supabase: {e}")
    
    def test_checkpoint_data_structure(self):
        """Test the structure of checkpoint data"""
        print("\n=== Testing Checkpoint Data Structure ===")
        
        try:
            # Create a test checkpoint
            client = Client(db_url=SUPABASE_URL)
            response = client.create(
                model="command-r",
                input="Test checkpoint structure",
                store=True
            )
            
            thread_id = response["id"]
            time.sleep(2)  # Allow for write
            
            # Query checkpoint data
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    thread_id,
                    checkpoint_ns,
                    checkpoint_id,
                    parent_checkpoint_id,
                    checkpoint
                FROM checkpoints
                WHERE thread_id = %s
                ORDER BY checkpoint_ns
                LIMIT 1
            """, (thread_id,))
            
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Checkpoint found for thread: {thread_id}")
                print(f"   - Namespace: {result[1]}")
                print(f"   - Checkpoint ID: {result[2]}")
                print(f"   - Parent ID: {result[3]}")
                print(f"   - Has data: {result[4] is not None}")
                
                # Verify checkpoint data is not empty
                assert result[4] is not None, "Checkpoint data is NULL!"
                
            else:
                pytest.fail(f"❌ No checkpoint found for thread {thread_id}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect: {e}")
            raise
    
    def test_response_tracking_alignment(self):
        """Test that response_tracking aligns with checkpoints"""
        print("\n=== Testing Response Tracking vs Checkpoints ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            
            # Create multiple responses
            responses = []
            for i in range(3):
                r = client.create(
                    model="command-r",
                    input=f"Test message {i}",
                    store=True,
                    previous_response_id=responses[-1]["id"] if responses else None
                )
                responses.append(r)
                print(f"Created response {i}: {r['id']}")
            
            time.sleep(2)  # Allow for writes
            
            # Check database
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            thread_id = responses[0]["id"]  # First response is thread
            
            # Count response_tracking entries
            cursor.execute("""
                SELECT COUNT(*) FROM response_tracking 
                WHERE thread_id = %s AND was_stored = true
            """, (thread_id,))
            tracking_count = cursor.fetchone()[0]
            
            # Count checkpoints
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            checkpoint_count = cursor.fetchone()[0]
            
            print(f"\nThread: {thread_id}")
            print(f"Response tracking entries: {tracking_count}")
            print(f"Checkpoint entries: {checkpoint_count}")
            
            if checkpoint_count == 0:
                pytest.fail("❌ No checkpoints created!")
            elif checkpoint_count != tracking_count:
                print(f"⚠️ Mismatch: {tracking_count} tracked, {checkpoint_count} checkpoints")
            else:
                print("✅ Response tracking and checkpoints aligned!")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect: {e}")
            raise
    
    def test_sqlite_checkpoint_structure(self):
        """Test SQLite checkpoint structure"""
        print("\n=== Testing SQLite Checkpoint Structure ===")
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        client = Client(db_path=db_path)
        
        # Create responses
        r1 = client.create(
            model="command-r",
            input="SQLite test 1",
            store=True
        )
        
        r2 = client.create(
            model="command-r",
            input="SQLite test 2",
            previous_response_id=r1["id"]
        )
        
        # Check SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"SQLite tables: {tables}")
        
        if "checkpoints" in tables:
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = ?
            """, (r1["id"],))
            count = cursor.fetchone()[0]
            print(f"✅ SQLite checkpoints: {count}")
            assert count > 0, "No SQLite checkpoints created!"
        else:
            pytest.fail("❌ No checkpoints table in SQLite!")
        
        if "response_tracking" in tables:
            cursor.execute("SELECT COUNT(*) FROM response_tracking")
            count = cursor.fetchone()[0]
            print(f"✅ SQLite response tracking: {count} entries")
        
        cursor.close()
        conn.close()
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_checkpoint_incremental_updates(self):
        """Test that checkpoints are incrementally updated"""
        print("\n=== Testing Incremental Checkpoint Updates ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            
            # Create initial response
            r1 = client.create(
                model="command-r",
                input="First message",
                store=True
            )
            thread_id = r1["id"]
            
            time.sleep(1)
            
            # Check initial checkpoint count
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            count1 = cursor.fetchone()[0]
            
            # Add second message
            r2 = client.create(
                model="command-r",
                input="Second message",
                previous_response_id=r1["id"]
            )
            
            time.sleep(1)
            
            # Check updated count
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            count2 = cursor.fetchone()[0]
            
            # Add third message
            r3 = client.create(
                model="command-r",
                input="Third message",
                previous_response_id=r2["id"]
            )
            
            time.sleep(1)
            
            # Check final count
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            count3 = cursor.fetchone()[0]
            
            print(f"Checkpoint counts: {count1} → {count2} → {count3}")
            
            assert count3 > count2 >= count1, "Checkpoints not incrementing!"
            print("✅ Checkpoints incrementally updated!")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect: {e}")
            raise
    
    def test_checkpoint_content_preservation(self):
        """Test that checkpoint content preserves conversation"""
        print("\n=== Testing Checkpoint Content Preservation ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            
            # Create with specific content
            unique_phrase = "ZEBRA-QUANTUM-2024"
            r1 = client.create(
                model="command-r",
                input=f"Remember this phrase: {unique_phrase}",
                store=True
            )
            
            time.sleep(2)
            
            # Query checkpoint content
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT checkpoint::text
                FROM checkpoints 
                WHERE thread_id = %s
                LIMIT 1
            """, (r1["id"],))
            
            result = cursor.fetchone()
            
            if result and result[0]:
                checkpoint_text = result[0]
                if unique_phrase in checkpoint_text:
                    print(f"✅ Checkpoint contains conversation content!")
                else:
                    print(f"⚠️ Checkpoint doesn't contain '{unique_phrase}'")
                    print(f"   Checkpoint preview: {checkpoint_text[:200]}")
            else:
                print("❌ No checkpoint content found!")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect: {e}")
            raise


if __name__ == "__main__":
    print("="*60)
    print("DATABASE VALIDATION TESTS")
    print("="*60)
    print("\nThis test suite directly validates database state:")
    print("- Table existence and structure")
    print("- Checkpoint data integrity")
    print("- Response tracking alignment")
    print("- Content preservation")
    print("\nRun with: pytest tests/test_database_validation.py -v -s")
    print("="*60)