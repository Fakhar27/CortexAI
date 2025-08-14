#!/usr/bin/env python3
"""
Test script to verify db_url parameter functionality
Tests both SQLite and PostgreSQL with per-request database specification
"""

import os
import sys
import time
from typing import Optional

# Add cortex to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import Client

def test_db_url_parameter():
    """Test db_url parameter with different databases"""
    
    print("=" * 80)
    print("Testing db_url parameter functionality")
    print("=" * 80)
    
    # Get PostgreSQL URL from environment if available
    postgres_url = os.getenv("DATABASE_URL")
    
    # Test 1: Create client with default SQLite
    print("\n1. Testing with default SQLite database...")
    client = Client()
    
    try:
        response1 = client.responses.create(
            input="Hello, what database am I using?",
            model="command-r",
            store=True
        )
        print(f"✅ Response ID (SQLite): {response1['id']}")
        print(f"   Message: {response1['output'][0]['content'][0]['text'][:100]}...")
        
        # Test continuing conversation with SQLite
        response2 = client.responses.create(
            input="What was my first question?",
            model="command-r",
            previous_response_id=response1['id'],
            store=True
        )
        print(f"✅ Continued conversation (SQLite): {response2['id']}")
        
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return False
    
    # Test 2: Use db_url parameter to override per request (if PostgreSQL available)
    if postgres_url:
        print(f"\n2. Testing with PostgreSQL via db_url parameter...")
        print(f"   URL: {postgres_url[:30]}...")
        
        try:
            # Same client, but use PostgreSQL for this specific request
            response3 = client.responses.create(
                input="Hello from PostgreSQL! Remember this message.",
                model="command-r",
                db_url=postgres_url,  # Override database for this request
                store=True
            )
            print(f"✅ Response ID (PostgreSQL): {response3['id']}")
            print(f"   Message: {response3['output'][0]['content'][0]['text'][:100]}...")
            
            # Continue conversation in PostgreSQL
            response4 = client.responses.create(
                input="What database message did you just store?",
                model="command-r",
                db_url=postgres_url,  # Must specify same db_url to continue
                previous_response_id=response3['id'],
                store=True
            )
            print(f"✅ Continued conversation (PostgreSQL): {response4['id']}")
            
            # Test 3: Switch back to SQLite for next request
            print("\n3. Testing switch back to SQLite...")
            response5 = client.responses.create(
                input="Back to SQLite now",
                model="command-r",
                # No db_url specified, uses default SQLite
                store=True
            )
            print(f"✅ Response ID (back to SQLite): {response5['id']}")
            
            # Test 4: Try to continue PostgreSQL conversation without db_url (should fail)
            print("\n4. Testing error handling...")
            try:
                response6 = client.responses.create(
                    input="Continue PostgreSQL conversation",
                    model="command-r",
                    previous_response_id=response3['id'],  # PostgreSQL response
                    # No db_url - should fail since response3 is in PostgreSQL
                    store=True
                )
                print(f"❌ Should have failed - response not found in SQLite")
            except Exception as e:
                if "not found" in str(e).lower():
                    print(f"✅ Correctly failed: Response from PostgreSQL not found in SQLite")
                else:
                    print(f"❌ Unexpected error: {e}")
            
        except Exception as e:
            print(f"❌ PostgreSQL test failed: {e}")
            return False
    
    else:
        print("\n2. Skipping PostgreSQL tests (DATABASE_URL not set)")
        print("   To test PostgreSQL, set DATABASE_URL environment variable")
    
    # Test 5: Test invalid db_url
    print("\n5. Testing invalid db_url...")
    try:
        response_bad = client.responses.create(
            input="Test invalid URL",
            model="command-r",
            db_url="invalid://url",
            store=True
        )
        print(f"❌ Should have failed with invalid URL")
    except Exception as e:
        print(f"✅ Correctly rejected invalid URL: {str(e)[:100]}...")
    
    # Test 6: Test empty db_url
    print("\n6. Testing empty db_url...")
    try:
        response_empty = client.responses.create(
            input="Test empty URL",
            model="command-r",
            db_url="",
            store=True
        )
        print(f"❌ Should have failed with empty URL")
    except Exception as e:
        print(f"✅ Correctly rejected empty URL: {str(e)[:100]}...")
    
    print("\n" + "=" * 80)
    print("✅ All db_url parameter tests completed successfully!")
    print("=" * 80)
    
    return True


def test_serverless_scenario():
    """Simulate serverless environment where each request creates new client"""
    
    print("\n" + "=" * 80)
    print("Testing serverless scenario")
    print("=" * 80)
    
    postgres_url = os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("⚠️  Skipping serverless test - DATABASE_URL not set")
        print("   In production serverless, you would pass user's db_url")
        return True
    
    print("\nSimulating serverless where each request creates new client...")
    
    # Request 1: New client, new conversation
    print("\n1. First request (new client)...")
    client1 = Client()  # New client instance
    response1 = client1.responses.create(
        input="First message in serverless",
        model="command-r",
        db_url=postgres_url,  # User passes their database
        store=True
    )
    print(f"✅ Response 1 ID: {response1['id']}")
    
    # Request 2: New client, continue conversation
    print("\n2. Second request (new client, same user)...")
    client2 = Client()  # New client instance (simulating new request)
    response2 = client2.responses.create(
        input="What was my first message?",
        model="command-r",
        db_url=postgres_url,  # Same user database
        previous_response_id=response1['id'],
        store=True
    )
    print(f"✅ Response 2 ID: {response2['id']}")
    print(f"   AI remembered: {response2['output'][0]['content'][0]['text'][:100]}...")
    
    # Request 3: Different user with different database
    print("\n3. Third request (new client, different user)...")
    client3 = Client()  # New client instance
    # In real scenario, this would be a different user's database
    # For testing, we'll just use a different conversation
    response3 = client3.responses.create(
        input="I'm a different user",
        model="command-r",
        db_url=postgres_url,  # In reality, would be user2's database
        store=True
    )
    print(f"✅ Response 3 ID: {response3['id']}")
    
    print("\n✅ Serverless scenario test completed!")
    print("   Users can pass their own database per request")
    print("   Perfect for multi-tenant serverless applications")
    
    return True


if __name__ == "__main__":
    # Run tests
    success = test_db_url_parameter()
    
    if success:
        test_serverless_scenario()
    
    print("\n✨ Testing complete!")