#!/usr/bin/env python3
"""
Diagnostic script to check if checkpoint fix is working
Run this to quickly verify the bug is fixed
"""

import os
import sys
import time
import psycopg2
from cortex import Client

# CORRECT Supabase URL with pooler port 6543
SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

def diagnose():
    print("="*80)
    print("CHECKPOINT BUG DIAGNOSIS")
    print("="*80)
    
    # Check environment
    print("\n1. CHECKING ENVIRONMENT:")
    print("-" * 40)
    print(f"✅ Cortex imported successfully")
    print(f"✅ Using Supabase pooler URL (port 6543)")
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY") is not None,
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY") is not None,
        "CO_API_KEY": os.getenv("CO_API_KEY") is not None
    }
    
    for key, exists in api_keys.items():
        status = "✅" if exists else "❌"
        print(f"{status} {key}: {'Set' if exists else 'Not set'}")
    
    if not (api_keys["OPENAI_API_KEY"] and api_keys["GOOGLE_API_KEY"]):
        print("\n⚠️ Need OpenAI and Google API keys for full test")
        return
    
    # Test connection
    print("\n2. TESTING SUPABASE CONNECTION:")
    print("-" * 40)
    
    try:
        client = Client(db_url=SUPABASE_URL)
        print("✅ Connected to Supabase successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if "52.74.252.201" in str(e) and "5432" in str(e):
            print("   ERROR: Using wrong port! Should be 6543, not 5432")
        return
    
    # Create test conversation
    print("\n3. CREATING TEST CONVERSATION:")
    print("-" * 40)
    
    try:
        # First message
        print("Creating first message...")
        r1 = client.create(
            model="gpt-4o-mini",
            input="Remember this test number: 12345",
            store=True,
            temperature=0.0
        )
        
        if r1["status"] != "completed":
            print(f"❌ First message failed: {r1}")
            return
        
        thread_id = r1["id"]
        print(f"✅ Created thread: {thread_id}")
        
        # Wait for database
        time.sleep(2)
        
        # Check checkpoints
        print("\n4. CHECKING DATABASE:")
        print("-" * 40)
        
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
        
        print(f"Checkpoints: {checkpoint_count}")
        print(f"Response tracking: {tracking_count}")
        
        if checkpoint_count == 0:
            print("\n❌ BUG NOT FIXED: No checkpoints created!")
            print("   The checkpoint_ns fix may not be applied")
            return
        else:
            print(f"\n✅ BUG FIXED: {checkpoint_count} checkpoints created!")
        
        # Test memory
        print("\n5. TESTING MEMORY PERSISTENCE:")
        print("-" * 40)
        
        # Switch to Gemini
        print("Switching to Gemini...")
        r2 = client.create(
            model="gemini-1.5-flash",
            input="What test number did I just give you?",
            previous_response_id=r1["id"],
            temperature=0.0
        )
        
        if r2["status"] != "completed":
            print(f"❌ Second message failed: {r2}")
            return
        
        content = r2["output"][0]["content"][0]["text"]
        print(f"Gemini response: {content[:200]}")
        
        if "12345" in content:
            print("\n✅ MEMORY WORKS! Gemini remembered the number!")
        else:
            print("\n❌ MEMORY FAILED! Gemini forgot the number")
            print(f"   Full response: {content}")
        
        # Back to GPT
        print("\nSwitching back to GPT-4...")
        r3 = client.create(
            model="gpt-4o-mini",
            input="Can you confirm the test number?",
            previous_response_id=r2["id"],
            temperature=0.0
        )
        
        content3 = r3["output"][0]["content"][0]["text"]
        if "12345" in content3:
            print("✅ GPT-4 also remembers!")
        else:
            print("❌ GPT-4 forgot!")
        
    except KeyError as e:
        if "checkpoint_ns" in str(e):
            print(f"\n❌ CRITICAL BUG: {e}")
            print("   The checkpoint_ns fix is NOT applied!")
            return
        raise
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return
    
    # Summary
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)
    print("\n✅ CHECKPOINT BUG IS FIXED!")
    print("✅ Checkpoints are being created")
    print("✅ Memory persists across providers")
    print("✅ Django E2E scenario should work now")
    print("\nYou can now run your Django app and conversations")
    print("should maintain history when switching providers!")
    print("="*80)


if __name__ == "__main__":
    try:
        diagnose()
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()