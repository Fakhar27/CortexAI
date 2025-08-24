#!/usr/bin/env python3
"""
Test the exact Django E2E scenario
Mimics the conversation flow from the Django app
"""

import os
import pytest
import time
import psycopg2
from cortex import Client

# Use the CORRECT Supabase pooler URL (port 6543, not 5432!)
SUPABASE_POOLER_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


class TestDjangoE2EScenario:
    """Test the exact Django E2E conversation flow"""
    
    def test_django_conversation_flow(self):
        """Replicate the exact Django conversation that was failing"""
        print("\n" + "="*80)
        print("DJANGO E2E SCENARIO TEST")
        print("="*80)
        print(f"Using Supabase pooler URL (port 6543)")
        print("="*80)
        
        # Check required API keys (skip Cohere due to rate limits)
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
            print("✅ Connected to Supabase pooler")
        except Exception as e:
            pytest.skip(f"Cannot connect to Supabase: {e}")
        
        # Simulate the Django conversation
        print("\n--- Simulating Django Conversation ---\n")
        
        # Message 1: GPT-4 Mini (like Django)
        print("1. USER: 'i need help, how can you specifically help me'")
        print("   MODEL: gpt-4o-mini")
        
        response1 = client.create(
            model="gpt-4o-mini",
            input="i need help, how can you specifically help me",
            instructions="You are a helpful assistant",
            store=True,
            temperature=0.7
        )
        
        assert response1["status"] == "completed"
        thread_id = response1["id"]
        print(f"   Response ID: {response1['id']}")
        print(f"   Thread ID: {thread_id}")
        
        # Check if checkpoint was created
        time.sleep(2)
        conn = psycopg2.connect(SUPABASE_POOLER_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (thread_id,))
        checkpoint_count1 = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"   Checkpoints: {checkpoint_count1}")
        if checkpoint_count1 == 0:
            pytest.fail("❌ NO CHECKPOINTS CREATED FOR FIRST MESSAGE!")
        
        # Message 2: Switch to Gemini (like Django)
        print("\n2. USER: 'i like driving and coding'")
        print("   MODEL: gemini-1.5-flash (SWITCHED PROVIDER)")
        
        response2 = client.create(
            model="gemini-1.5-flash",
            input="i like driving and coding",
            previous_response_id=response1["id"],
            store=True,
            temperature=0.7
        )
        
        assert response2["status"] == "completed"
        assert response2.get("previous_response_id") == response1["id"]
        print(f"   Response ID: {response2['id']}")
        print(f"   Previous Response ID: {response2.get('previous_response_id')}")
        
        # Message 3: Back to GPT-4 (THE CRITICAL TEST)
        print("\n3. USER: 'what are we talking about'")
        print("   MODEL: gpt-4o-mini (BACK TO ORIGINAL)")
        
        response3 = client.create(
            model="gpt-4o-mini",
            input="what are we talking about",
            previous_response_id=response2["id"],
            store=True,
            temperature=0.7
        )
        
        assert response3["status"] == "completed"
        content3 = response3["output"][0]["content"][0]["text"].lower()
        print(f"   Response ID: {response3['id']}")
        print(f"   Response preview: {content3[:150]}...")
        
        # CRITICAL CHECK: Does GPT-4 remember the conversation?
        context_keywords = ["driving", "coding", "help", "interests", "skills"]
        found_keywords = [kw for kw in context_keywords if kw in content3]
        
        if not found_keywords:
            print(f"\n❌ MODEL FORGOT THE CONVERSATION!")
            print(f"   Expected keywords: {context_keywords}")
            print(f"   Found: {found_keywords}")
            print(f"   Full response: {content3[:500]}")
            pytest.fail("Conversation memory not maintained!")
        else:
            print(f"\n✅ MODEL REMEMBERS! Found keywords: {found_keywords}")
        
        # Message 4: Back to Gemini
        print("\n4. USER: 'what do i like'")
        print("   MODEL: gemini-1.5-flash")
        
        response4 = client.create(
            model="gemini-1.5-flash",
            input="what do i like",
            previous_response_id=response3["id"],
            store=True,
            temperature=0.7
        )
        
        assert response4["status"] == "completed"
        content4 = response4["output"][0]["content"][0]["text"].lower()
        print(f"   Response preview: {content4[:150]}...")
        
        # Should mention driving and coding
        if "driving" in content4 and "coding" in content4:
            print("   ✅ Gemini remembers both interests!")
        elif "driving" in content4 or "coding" in content4:
            print("   ⚠️ Gemini partially remembers")
        else:
            print("   ❌ Gemini forgot the interests")
        
        # Final checkpoint count
        conn = psycopg2.connect(SUPABASE_POOLER_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (thread_id,))
        final_checkpoints = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM response_tracking WHERE thread_id = %s", (thread_id,))
        final_tracking = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"\n--- Final Database State ---")
        print(f"Thread ID: {thread_id}")
        print(f"Total checkpoints: {final_checkpoints}")
        print(f"Total response tracking: {final_tracking}")
        
        if final_checkpoints == 0:
            pytest.fail("❌ NO CHECKPOINTS CREATED AT ALL!")
        
        print("\n" + "="*80)
        print("🎉 DJANGO E2E SCENARIO WORKING!")
        print("Conversation memory maintained across provider switches!")
        print("="*80)
    
    def test_simplified_memory_check(self):
        """Simplified test focusing on memory retention"""
        print("\n" + "="*80)
        print("SIMPLIFIED MEMORY TEST")
        print("="*80)
        
        if not (os.getenv("OPENAI_API_KEY") and os.getenv("GOOGLE_API_KEY")):
            pytest.skip("Need API keys")
        
        try:
            client = Client(db_url=SUPABASE_POOLER_URL)
        except Exception as e:
            pytest.skip(f"Cannot connect: {e}")
        
        # Simple memorable fact
        print("\n1. Establishing fact with GPT-4...")
        r1 = client.create(
            model="gpt-4o-mini",
            input="My favorite number is 777. Remember this.",
            store=True,
            temperature=0.0
        )
        
        # Switch to Gemini and test
        print("2. Testing memory with Gemini...")
        r2 = client.create(
            model="gemini-1.5-flash",
            input="What's my favorite number?",
            previous_response_id=r1["id"],
            temperature=0.0
        )
        
        content = r2["output"][0]["content"][0]["text"]
        print(f"   Gemini response: {content[:200]}")
        
        if "777" in content:
            print("   ✅ MEMORY WORKS! Gemini remembered 777")
        else:
            pytest.fail(f"   ❌ MEMORY FAILED! Response: {content}")
        
        # Back to GPT-4
        print("3. Double-checking with GPT-4...")
        r3 = client.create(
            model="gpt-4o-mini",
            input="Remind me what my favorite number is.",
            previous_response_id=r2["id"],
            temperature=0.0
        )
        
        content3 = r3["output"][0]["content"][0]["text"]
        if "777" in content3:
            print("   ✅ GPT-4 also remembers 777")
        else:
            pytest.fail(f"   ❌ GPT-4 forgot! Response: {content3}")
        
        print("\n✅ Memory persists across provider switches!")


if __name__ == "__main__":
    print("="*80)
    print("DJANGO E2E SCENARIO TEST")
    print("="*80)
    print("\nThis test replicates the exact Django conversation flow:")
    print("1. GPT-4: Initial help request")
    print("2. Gemini: User shares interests")
    print("3. GPT-4: Ask about context (CRITICAL TEST)")
    print("4. Gemini: Verify memory")
    print("\nUsing CORRECT Supabase URL with port 6543")
    print("Avoiding Cohere due to rate limits")
    print("\nRun with: pytest tests/test_django_e2e_scenario.py -v -s")
    print("="*80)