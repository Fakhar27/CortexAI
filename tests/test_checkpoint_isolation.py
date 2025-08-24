#!/usr/bin/env python3
"""
Isolated test for checkpoint saving and cross-provider context
Uses hardcoded Supabase URL to avoid environment variable issues
"""

import os
import time
import psycopg2
from cortex import Client

# HARDCODED Supabase pooler URL - no environment variables!
SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

print("="*80)
print("ISOLATED CHECKPOINT TEST")
print("="*80)
print(f"Using hardcoded URL: {SUPABASE_URL[:60]}...")
print("="*80)

def check_checkpoint_state(thread_id):
    """Check if checkpoints exist for a thread"""
    try:
        conn = psycopg2.connect(SUPABASE_URL)
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
        
        return checkpoint_count, tracking_count
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return -1, -1

def test_single_provider_checkpoint():
    """Test 1: Single provider - are checkpoints being saved at all?"""
    print("\n" + "="*60)
    print("TEST 1: Single Provider Checkpoint")
    print("="*60)
    
    try:
        # Create client with hardcoded URL
        print("\nConnecting to Supabase...")
        client = Client(db_url=SUPABASE_URL)
        print("✅ Connected")
        
        # Create a simple message
        print("\nCreating first message...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="Remember this test phrase: CHECKPOINT-TEST-2024",
            store=True,  # Explicitly request storage
            temperature=0.0
        )
        
        if response1["status"] != "completed":
            print(f"❌ Response failed: {response1}")
            return False
        
        thread_id = response1["id"]
        print(f"✅ Created thread: {thread_id}")
        
        # Wait for database write
        print("\nWaiting for database write...")
        time.sleep(3)
        
        # Check database state
        checkpoint_count, tracking_count = check_checkpoint_state(thread_id)
        print(f"\nDatabase state:")
        print(f"  Checkpoints: {checkpoint_count}")
        print(f"  Response tracking: {tracking_count}")
        
        if checkpoint_count == 0:
            print("\n❌ CRITICAL: NO CHECKPOINTS SAVED!")
            print("   PostgresSaver.put() is not working!")
            return False
        else:
            print(f"\n✅ Checkpoints saved: {checkpoint_count}")
            
        # Test memory within same provider
        print("\nTesting memory (same provider)...")
        response2 = client.create(
            model="gpt-4o-mini",
            input="What was the test phrase I asked you to remember?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        
        content = response2["output"][0]["content"][0]["text"]
        print(f"Response: {content[:200]}")
        
        if "CHECKPOINT-TEST-2024" in content:
            print("✅ Memory works within same provider!")
            return True
        else:
            print("❌ Memory failed within same provider!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cross_provider_context():
    """Test 2: Cross-provider - is context maintained when switching?"""
    print("\n" + "="*60)
    print("TEST 2: Cross-Provider Context")
    print("="*60)
    
    try:
        # Create client
        print("\nConnecting to Supabase...")
        client = Client(db_url=SUPABASE_URL)
        print("✅ Connected")
        
        # GPT-4: Establish context
        print("\n1. GPT-4 establishing context...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="My secret number is 888. Remember this.",
            store=True,
            temperature=0.0
        )
        
        thread_id = response1["id"]
        print(f"   Thread: {thread_id}")
        
        # Wait for save
        time.sleep(2)
        
        # Check initial state
        cp1, tr1 = check_checkpoint_state(thread_id)
        print(f"   After GPT-4: {cp1} checkpoints, {tr1} tracking")
        
        if cp1 == 0:
            print("   ❌ No checkpoints after first message!")
            return False
        
        # Gemini: Test context
        print("\n2. Switching to Gemini...")
        response2 = client.create(
            model="gemini-1.5-flash",
            input="What's my secret number?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        
        content2 = response2["output"][0]["content"][0]["text"]
        print(f"   Gemini response: {content2[:150]}")
        
        # Check if Gemini remembers
        if "888" in content2:
            print("   ✅ Gemini remembers GPT-4's context!")
        else:
            print("   ❌ Gemini forgot! Context lost!")
            return False
        
        # Wait and check state
        time.sleep(2)
        cp2, tr2 = check_checkpoint_state(thread_id)
        print(f"   After Gemini: {cp2} checkpoints, {tr2} tracking")
        
        # GPT-4: Verify full context
        print("\n3. Back to GPT-4...")
        response3 = client.create(
            model="gpt-4o-mini",
            input="Remind me what we discussed - what was the number?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        
        content3 = response3["output"][0]["content"][0]["text"]
        print(f"   GPT-4 response: {content3[:150]}")
        
        if "888" in content3:
            print("   ✅ GPT-4 still remembers through Gemini!")
            
            # Final state
            time.sleep(2)
            cp3, tr3 = check_checkpoint_state(thread_id)
            print(f"\n   Final state: {cp3} checkpoints, {tr3} tracking")
            
            if cp3 > cp1:
                print("   ✅ Checkpoints incremented correctly!")
                return True
            else:
                print("   ⚠️ Checkpoints not incrementing properly")
                return False
        else:
            print("   ❌ Context lost on return to GPT-4!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_new_session_persistence():
    """Test 3: New session - can we retrieve saved conversation?"""
    print("\n" + "="*60)
    print("TEST 3: New Session Persistence")
    print("="*60)
    
    try:
        # First session
        print("\n--- First Session ---")
        client1 = Client(db_url=SUPABASE_URL)
        
        response1 = client1.create(
            model="gpt-4o-mini",
            input="My favorite color is purple. Remember this.",
            store=True,
            temperature=0.0
        )
        
        response_id = response1["id"]
        print(f"Created response: {response_id}")
        
        # Wait for save
        time.sleep(2)
        
        # Check it was saved
        cp, tr = check_checkpoint_state(response_id)
        print(f"Saved: {cp} checkpoints, {tr} tracking")
        
        if cp == 0:
            print("❌ Not saved to database!")
            return False
        
        # Delete client
        del client1
        print("✅ First session closed")
        
        # New session
        print("\n--- New Session ---")
        client2 = Client(db_url=SUPABASE_URL)
        
        print(f"Continuing from: {response_id}")
        response2 = client2.create(
            model="gpt-4o-mini",
            input="What's my favorite color?",
            previous_response_id=response_id,
            temperature=0.0
        )
        
        content = response2["output"][0]["content"][0]["text"].lower()
        print(f"Response: {content[:150]}")
        
        if "purple" in content:
            print("✅ Persistence works across sessions!")
            return True
        else:
            print("❌ Lost memory across sessions!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all isolated tests"""
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        return
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set")
        return
    
    results = []
    
    # Test 1: Basic checkpoint saving
    print("\n" + "🔍" * 40)
    result1 = test_single_provider_checkpoint()
    results.append(("Single Provider Checkpoint", result1))
    
    if not result1:
        print("\n⛔ Stopping - checkpoints not being saved at all!")
        print("   Fix this before testing cross-provider context")
    else:
        # Test 2: Cross-provider context
        result2 = test_cross_provider_context()
        results.append(("Cross-Provider Context", result2))
        
        # Test 3: New session persistence
        result3 = test_new_session_persistence()
        results.append(("New Session Persistence", result3))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    if all(r[1] for r in results):
        print("\n🎉 ALL TESTS PASSED - CHECKPOINTS WORKING!")
    else:
        print("\n❌ CHECKPOINT SYSTEM NOT WORKING PROPERLY")

if __name__ == "__main__":
    main()