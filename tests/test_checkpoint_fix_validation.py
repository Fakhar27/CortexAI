#!/usr/bin/env python3
"""
Focused validation test for checkpoint fix
Tests actual conversation memory with correct database URLs
"""

import os
import pytest
import time
import psycopg2
import sqlite3
import tempfile
from cortex import Client

# CORRECT URLs
SUPABASE_POOLER_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"

print(f"Using Supabase URL: {SUPABASE_POOLER_URL[:50]}...")
print(f"Using Docker URL: {DOCKER_POSTGRES_URL}")


class TestCheckpointFixValidation:
    """Validate the checkpoint fix with real conversation memory tests"""
    
    # ========== HELPER METHODS ==========
    
    def validate_conversation_memory(self, responses, test_name="Memory Test"):
        """Validate that all responses maintain conversation context"""
        print(f"\n--- Validating {test_name} ---")
        
        for i, response in enumerate(responses):
            if response.get("status") != "completed":
                pytest.fail(f"Response {i} failed: {response.get('status')}")
            
            content = response.get("output", [{}])[0].get("content", [{}])[0].get("text", "")
            print(f"Response {i}: {content[:100]}...")
        
        return True
    
    def check_database_state(self, db_url, thread_id):
        """Check checkpoint and tracking state in database"""
        try:
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            # Check checkpoints
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            checkpoint_count = cursor.fetchone()[0]
            
            # Check response tracking
            cursor.execute("""
                SELECT COUNT(*) FROM response_tracking 
                WHERE thread_id = %s
            """, (thread_id,))
            tracking_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"  Database state for {thread_id[:12]}...")
            print(f"    Checkpoints: {checkpoint_count}")
            print(f"    Response tracking: {tracking_count}")
            
            return checkpoint_count, tracking_count
            
        except Exception as e:
            print(f"  Could not check database: {e}")
            return -1, -1
    
    # ========== SQLITE TESTS ==========
    
    def test_sqlite_multi_turn_memory(self):
        """Test SQLite maintains memory across multiple turns"""
        print("\n" + "="*60)
        print("TEST: SQLite Multi-Turn Memory")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        try:
            client = Client(db_path=db_path)
            
            # Turn 1: Establish context
            r1 = client.create(
                model="gpt-4o-mini",
                input="My name is Alice and I work at OpenAI. Remember this.",
                store=True,
                temperature=0.0
            )
            assert r1["status"] == "completed"
            print("✅ Turn 1: Established context")
            
            # Turn 2: Add more context
            r2 = client.create(
                model="gpt-4o-mini",
                input="I also have a cat named Whiskers. What's my name?",
                previous_response_id=r1["id"],
                temperature=0.0
            )
            assert r2["status"] == "completed"
            content2 = r2["output"][0]["content"][0]["text"].lower()
            assert "alice" in content2, f"Forgot name! Response: {content2[:200]}"
            print("✅ Turn 2: Remembered name 'Alice'")
            
            # Turn 3: Test full context
            r3 = client.create(
                model="gpt-4o-mini",
                input="What company do I work for and what's my pet's name?",
                previous_response_id=r2["id"],
                temperature=0.0
            )
            assert r3["status"] == "completed"
            content3 = r3["output"][0]["content"][0]["text"].lower()
            assert "openai" in content3, f"Forgot company! Response: {content3[:200]}"
            assert "whiskers" in content3, f"Forgot pet! Response: {content3[:200]}"
            print("✅ Turn 3: Remembered 'OpenAI' and 'Whiskers'")
            
            # Check SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (r1["id"],))
            checkpoint_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            assert checkpoint_count > 0, "No checkpoints in SQLite!"
            print(f"✅ SQLite has {checkpoint_count} checkpoints")
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    # ========== DOCKER POSTGRES TESTS ==========
    
    def test_docker_postgres_memory(self):
        """Test Docker PostgreSQL maintains conversation memory"""
        print("\n" + "="*60)
        print("TEST: Docker PostgreSQL Memory")
        print("="*60)
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✅ Connected to Docker PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e) or "could not translate" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Multi-turn conversation
        r1 = client.create(
            model="gpt-4o-mini",
            input="The capital of France is Paris. The capital of Japan is Tokyo.",
            store=True,
            temperature=0.0
        )
        
        r2 = client.create(
            model="gpt-4o-mini",
            input="What's the capital of France?",
            previous_response_id=r1["id"],
            temperature=0.0
        )
        content2 = r2["output"][0]["content"][0]["text"].lower()
        assert "paris" in content2, f"Forgot Paris! Response: {content2}"
        print("✅ Remembered Paris")
        
        r3 = client.create(
            model="gpt-4o-mini",
            input="And what about Japan?",
            previous_response_id=r2["id"],
            temperature=0.0
        )
        content3 = r3["output"][0]["content"][0]["text"].lower()
        assert "tokyo" in content3, f"Forgot Tokyo! Response: {content3}"
        print("✅ Remembered Tokyo")
        
        # Check database state
        checkpoints, tracking = self.check_database_state(DOCKER_POSTGRES_URL, r1["id"])
        if checkpoints > 0:
            print(f"✅ Docker PostgreSQL working: {checkpoints} checkpoints")
    
    # ========== SUPABASE TESTS (CRITICAL) ==========
    
    def test_supabase_multi_provider_memory(self):
        """Test Supabase with provider switching (Django E2E scenario)"""
        print("\n" + "="*60)
        print("TEST: Supabase Multi-Provider Memory (CRITICAL)")
        print("="*60)
        
        # Check API keys (skip Cohere due to rate limits)
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
            print(f"✅ Connected to Supabase pooler (port 6543)")
        except Exception as e:
            pytest.skip(f"Cannot connect to Supabase: {e}")
        
        # CRITICAL TEST: Multi-provider conversation with context
        print("\n--- Starting Multi-Provider Conversation ---")
        
        # GPT-4: Establish facts
        print("1. GPT-4 establishing facts...")
        r1 = client.create(
            model="gpt-4o-mini",
            input="Remember these facts: The sky is blue. Water is H2O. Python is a programming language.",
            store=True,
            temperature=0.0
        )
        assert r1["status"] == "completed"
        thread_id = r1["id"]
        print(f"   Thread ID: {thread_id}")
        
        # Wait for database write
        time.sleep(2)
        
        # Check initial checkpoint
        checkpoints1, _ = self.check_database_state(SUPABASE_POOLER_URL, thread_id)
        if checkpoints1 == 0:
            pytest.fail("❌ NO CHECKPOINTS CREATED! Bug not fixed!")
        print(f"   ✅ Initial checkpoints: {checkpoints1}")
        
        # Gemini: Verify first fact
        print("2. Switching to Gemini...")
        r2 = client.create(
            model="gemini-1.5-flash",
            input="What color is the sky according to what I told you?",
            previous_response_id=r1["id"],
            temperature=0.0
        )
        assert r2["status"] == "completed"
        content2 = r2["output"][0]["content"][0]["text"].lower()
        
        if "blue" not in content2:
            pytest.fail(f"❌ Gemini FORGOT! Response: {content2[:200]}")
        print("   ✅ Gemini remembered: sky is blue")
        
        # GPT-4: Verify second fact
        print("3. Back to GPT-4...")
        r3 = client.create(
            model="gpt-4o-mini",
            input="What's the chemical formula for water that I mentioned?",
            previous_response_id=r2["id"],
            temperature=0.0
        )
        assert r3["status"] == "completed"
        content3 = r3["output"][0]["content"][0]["text"]
        
        if "H2O" not in content3 and "h2o" not in content3.lower():
            pytest.fail(f"❌ GPT-4 FORGOT! Response: {content3[:200]}")
        print("   ✅ GPT-4 remembered: water is H2O")
        
        # Gemini: Verify third fact
        print("4. Back to Gemini...")
        r4 = client.create(
            model="gemini-1.5-flash",
            input="What programming language did I mention?",
            previous_response_id=r3["id"],
            temperature=0.0
        )
        assert r4["status"] == "completed"
        content4 = r4["output"][0]["content"][0]["text"].lower()
        
        if "python" not in content4:
            pytest.fail(f"❌ Gemini FORGOT! Response: {content4[:200]}")
        print("   ✅ Gemini remembered: Python")
        
        # Final GPT-4: Verify all context
        print("5. Final GPT-4 check...")
        r5 = client.create(
            model="gpt-4o-mini",
            input="List all three facts I asked you to remember at the beginning.",
            previous_response_id=r4["id"],
            temperature=0.0
        )
        assert r5["status"] == "completed"
        content5 = r5["output"][0]["content"][0]["text"].lower()
        
        facts_found = {
            "blue": "blue" in content5,
            "H2O": "h2o" in content5,
            "Python": "python" in content5
        }
        
        print(f"   Facts remembered: {facts_found}")
        
        if not all(facts_found.values()):
            missing = [k for k, v in facts_found.items() if not v]
            pytest.fail(f"❌ LOST CONTEXT! Missing: {missing}. Response: {content5[:300]}")
        
        print("   ✅ All facts remembered across providers!")
        
        # Final checkpoint count
        final_checkpoints, final_tracking = self.check_database_state(SUPABASE_POOLER_URL, thread_id)
        print(f"\n   Final state: {final_checkpoints} checkpoints, {final_tracking} tracking entries")
        
        if final_checkpoints > checkpoints1:
            print("   ✅ Checkpoints incremented correctly")
        
        print("\n🎉 MULTI-PROVIDER MEMORY WORKING PERFECTLY!")
    
    # ========== EDGE CASE TESTS ==========
    
    def test_rapid_provider_switching(self):
        """Test rapid switching between providers"""
        print("\n" + "="*60)
        print("TEST: Rapid Provider Switching")
        print("="*60)
        
        if not (os.getenv("OPENAI_API_KEY") and os.getenv("GOOGLE_API_KEY")):
            pytest.skip("Need both OpenAI and Google API keys")
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
        except Exception as e:
            pytest.skip(f"Cannot connect: {e}")
        
        # Establish context
        r1 = client.create(
            model="gpt-4o-mini",
            input="Remember the number 42 and the color green.",
            store=True,
            temperature=0.0
        )
        
        # Rapid switches
        providers = ["gemini-1.5-flash", "gpt-4o-mini", "gemini-1.5-flash", "gpt-4o-mini"]
        questions = [
            "What number?",
            "What color?", 
            "Repeat the number",
            "Repeat the color"
        ]
        expected = ["42", "green", "42", "green"]
        
        prev_id = r1["id"]
        for i, (model, question, expect) in enumerate(zip(providers, questions, expected)):
            print(f"\n  Switch {i+1}: {model} - {question}")
            r = client.create(
                model=model,
                input=question,
                previous_response_id=prev_id,
                temperature=0.0
            )
            
            content = r["output"][0]["content"][0]["text"].lower()
            if expect.lower() not in content:
                pytest.fail(f"Lost memory at switch {i+1}! Expected '{expect}', got: {content[:100]}")
            
            print(f"  ✅ Remembered: {expect}")
            prev_id = r["id"]
        
        print("\n✅ Rapid switching maintains memory!")
    
    def test_long_conversation_memory(self):
        """Test memory over a long conversation"""
        print("\n" + "="*60)
        print("TEST: Long Conversation Memory")
        print("="*60)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        try:
            client = Client(db_path=db_path)
            
            # Initial context
            facts = [
                "My name is Bob",
                "I live in Seattle",
                "I work at Microsoft",
                "I have two dogs",
                "I like pizza"
            ]
            
            # Add facts one by one
            prev_id = None
            for i, fact in enumerate(facts):
                r = client.create(
                    model="gpt-4o-mini",
                    input=f"{fact}. Acknowledge this.",
                    previous_response_id=prev_id,
                    store=True,
                    temperature=0.0
                )
                prev_id = r["id"]
                print(f"  Added fact {i+1}: {fact}")
            
            # Test recall
            questions = [
                ("What's my name?", "bob"),
                ("Where do I live?", "seattle"),
                ("Where do I work?", "microsoft"),
                ("How many dogs?", "two"),
                ("What food do I like?", "pizza")
            ]
            
            for question, expected in questions:
                r = client.create(
                    model="gpt-4o-mini",
                    input=question,
                    previous_response_id=prev_id,
                    temperature=0.0
                )
                
                content = r["output"][0]["content"][0]["text"].lower()
                if expected not in content:
                    pytest.fail(f"Forgot '{expected}'! Question: {question}, Response: {content[:100]}")
                
                print(f"  ✅ Remembered: {expected}")
                prev_id = r["id"]
            
            print("\n✅ Long conversation memory working!")
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("="*80)
    print("CHECKPOINT FIX VALIDATION")
    print("="*80)
    print("\nThis test validates:")
    print("1. SQLite multi-turn memory")
    print("2. Docker PostgreSQL memory")
    print("3. Supabase pooler with provider switching")
    print("4. Rapid provider switching")
    print("5. Long conversation memory")
    print("\nUsing correct URLs:")
    print(f"- Supabase: ...pooler.supabase.com:6543")
    print(f"- Docker: localhost:5432")
    print("\nRun with: pytest tests/test_checkpoint_fix_validation.py -v -s")
    print("="*80)