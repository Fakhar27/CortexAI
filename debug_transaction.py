#!/usr/bin/env python3
"""
Debug the transaction issue with Supabase pooler
"""

import os
import psycopg

# Your connection string
db_url = "postgresql://postgres.fzkfttgxsmigeeziexxc:BdnFsaQZulP5SLeu@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

def test_transaction_issue():
    """Test what's causing the transaction to fail"""
    
    print("Testing transaction issue...")
    
    try:
        # Test basic connection
        conn = psycopg.connect(db_url, gssencmode='disable')
        print("✅ Basic connection works")
        
        # Test creating the response_tracking table
        print("\nTesting table creation...")
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS response_tracking (
                    response_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    was_stored BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("✅ Table creation works")
        
        # Test PostgresSaver setup
        print("\nTesting PostgresSaver setup...")
        from langgraph.checkpoint.postgres import PostgresSaver
        
        with PostgresSaver.from_conn_string(db_url) as checkpointer:
            checkpointer.setup()
            print("✅ PostgresSaver setup works")
            
        print("\n✅ All tests passed - transaction issue not reproduced")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if it's a transaction error
        if "current transaction is aborted" in str(e):
            print("\n🔍 This is the transaction abort error!")
            print("The connection is in a failed transaction state")
            
            # Try to recover
            try:
                conn.rollback()
                print("✅ Rolled back transaction")
            except:
                print("❌ Could not rollback")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transaction_issue()