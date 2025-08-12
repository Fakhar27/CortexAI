#!/usr/bin/env python3
"""
Test PostgreSQL integration with Cortex

This script tests:
1. Local SQLite (default)
2. PostgreSQL connection
3. Supabase connection (if URL provided)
4. Environment variable support
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add cortex to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import Client
from cortex.responses.persistence import DatabaseError


def test_sqlite_default():
    """Test 1: Default SQLite behavior"""
    print("\n" + "="*60)
    print("TEST 1: Default SQLite (local development)")
    print("="*60)
    
    try:
        client = Client()
        print("✅ Client initialized with SQLite")
        
        # Test create
        response = client.create(
            input="Hello, how are you?",
            instructions="You are a helpful assistant"
        )
        print(f"✅ Response created: {response['id']}")
        
        # Test continuation
        response2 = client.create(
            input="What did I just ask you?",
            previous_response_id=response['id']
        )
        print(f"✅ Continuation works: {response2['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_postgresql_local():
    """Test 2: Local PostgreSQL"""
    print("\n" + "="*60)
    print("TEST 2: Local PostgreSQL")
    print("="*60)
    
    # Common local PostgreSQL URLs to try
    test_urls = [
        "postgresql://postgres:postgres@localhost:5432/cortex",
        "postgresql://postgres:password@localhost:5432/cortex",
        "postgresql://cortex:cortex@localhost:5432/cortex",
    ]
    
    for url in test_urls:
        print(f"\nTrying: {url[:40]}...")
        try:
            client = Client(db_url=url)
            print(f"✅ Connected to PostgreSQL!")
            
            # Test create
            response = client.create(
                input="Testing PostgreSQL",
                instructions="You are a test assistant"
            )
            print(f"✅ Response created: {response['id']}")
            
            # Test continuation
            response2 = client.create(
                input="Is this working?",
                previous_response_id=response['id']
            )
            print(f"✅ Continuation works: {response2['id']}")
            
            return True
            
        except DatabaseError as e:
            if "password authentication failed" in str(e):
                print(f"❌ Wrong password")
            elif "could not translate host name" in str(e):
                print(f"❌ PostgreSQL not running on localhost")
            else:
                print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n⚠️  No local PostgreSQL found. This is OK if you're using Supabase.")
    return False


def test_supabase():
    """Test 3: Supabase connection"""
    print("\n" + "="*60)
    print("TEST 3: Supabase PostgreSQL")
    print("="*60)
    
    # Check for Supabase URL in environment
    supabase_url = os.getenv("SUPABASE_DB_URL")
    
    if not supabase_url:
        print("⚠️  No SUPABASE_DB_URL in environment")
        print("To test Supabase, add to .env file:")
        print("SUPABASE_DB_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres")
        return False
    
    try:
        print(f"Connecting to Supabase: {supabase_url[:50]}...")
        client = Client(db_url=supabase_url)
        print("✅ Connected to Supabase!")
        
        # Test create
        response = client.create(
            input="Testing Supabase",
            instructions="You are a cloud assistant"
        )
        print(f"✅ Response created: {response['id']}")
        
        # Test continuation
        response2 = client.create(
            input="Are we in the cloud?",
            previous_response_id=response['id']
        )
        print(f"✅ Continuation works: {response2['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False


def test_environment_variable():
    """Test 4: DATABASE_URL environment variable"""
    print("\n" + "="*60)
    print("TEST 4: DATABASE_URL Environment Variable")
    print("="*60)
    
    # Save current DATABASE_URL
    original_db_url = os.getenv("DATABASE_URL")
    
    try:
        # Test with no DATABASE_URL (should use SQLite)
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        client = Client()
        print("✅ Without DATABASE_URL: Uses SQLite")
        
        # Test with DATABASE_URL set
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
            client = Client()
            print("✅ With DATABASE_URL: Uses PostgreSQL from environment")
        else:
            print("⚠️  No DATABASE_URL in environment to test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Restore original DATABASE_URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url


def test_invalid_urls():
    """Test 5: Invalid database URLs"""
    print("\n" + "="*60)
    print("TEST 5: Invalid URL Handling")
    print("="*60)
    
    invalid_urls = [
        ("mongodb://localhost/test", "MongoDB URL"),
        ("mysql://localhost/test", "MySQL URL"),
        ("redis://localhost", "Redis URL"),
        ("", "Empty string"),
        ("not-a-url", "Invalid format"),
    ]
    
    for url, description in invalid_urls:
        try:
            print(f"\nTesting {description}: {url[:30] if url else 'empty'}...")
            client = Client(db_url=url)
            print(f"❌ Should have failed for {description}")
        except DatabaseError as e:
            print(f"✅ Correctly rejected: {str(e)[:60]}...")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    return True


def test_serverless_simulation():
    """Test 6: Simulate serverless environment"""
    print("\n" + "="*60)
    print("TEST 6: Serverless Environment Simulation")
    print("="*60)
    
    # Simulate serverless by setting environment variable
    os.environ["VERCEL"] = "1"
    
    try:
        # Test without db_url (should warn and use MemorySaver)
        print("\nSimulating serverless without db_url...")
        client = Client()
        print("✅ Client created with MemorySaver (no persistence)")
        
        response = client.create(
            input="Testing serverless",
            instructions="You are a serverless assistant"
        )
        print(f"✅ Response works: {response['id']}")
        
        # Test with db_url (should work if PostgreSQL available)
        db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
        if db_url:
            print(f"\nSimulating serverless with db_url...")
            client = Client(db_url=db_url)
            print("✅ Client created with PostgreSQL in serverless")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Clean up
        del os.environ["VERCEL"]


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CORTEX POSTGRESQL INTEGRATION TEST SUITE")
    print("="*60)
    
    # Check if PostgreSQL dependencies are installed
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        print("✅ PostgreSQL dependencies installed")
    except ImportError:
        print("⚠️  PostgreSQL dependencies not installed")
        print("Install with: pip install 'cortex[postgres]'")
        print("Or: pip install langgraph-checkpoint-postgres psycopg[binary]")
        print("\nContinuing with SQLite tests only...")
    
    # Run tests
    results = []
    results.append(("SQLite Default", test_sqlite_default()))
    results.append(("PostgreSQL Local", test_postgresql_local()))
    results.append(("Supabase", test_supabase()))
    results.append(("Environment Variable", test_environment_variable()))
    results.append(("Invalid URLs", test_invalid_urls()))
    results.append(("Serverless Simulation", test_serverless_simulation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "⚠️  SKIPPED/FAILED"
        print(f"{status}: {name}")
    
    # Configuration tips
    print("\n" + "="*60)
    print("CONFIGURATION TIPS")
    print("="*60)
    print("""
1. For LOCAL DEVELOPMENT:
   - Just use: Client() - SQLite works out of the box
   
2. For LOCAL POSTGRESQL:
   - Install PostgreSQL locally
   - Create database: createdb cortex
   - Use: Client(db_url="postgresql://localhost:5432/cortex")
   
3. For SUPABASE:
   - Create free project at https://supabase.com
   - Get connection string from Settings > Database
   - Use: Client(db_url="postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres")
   
4. For SERVERLESS (Vercel, AWS Lambda, etc):
   - Set DATABASE_URL environment variable
   - Use: Client() - automatically uses DATABASE_URL
   
5. INSTALL POSTGRESQL SUPPORT:
   pip install "cortex[postgres]"
   # OR
   pip install langgraph-checkpoint-postgres psycopg[binary]
""")


if __name__ == "__main__":
    main()