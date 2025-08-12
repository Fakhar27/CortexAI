#!/usr/bin/env python3
"""
Example: Using Cortex with PostgreSQL/Supabase

This example shows all the ways to use Cortex with different databases.
"""

import os
from dotenv import load_dotenv
from cortex import Client

# Load environment variables from .env file
load_dotenv()


def example_1_sqlite():
    """Example 1: Local development with SQLite (default)"""
    print("\n=== Example 1: SQLite (Local Development) ===\n")
    
    # No configuration needed - just works!
    client = Client()
    
    response = client.create(
        input="What's the weather like?",
        instructions="You are a helpful weather assistant"
    )
    
    print(f"Response ID: {response['id']}")
    print(f"Assistant: {response['output'][0]['content'][0]['text']}")
    
    # Continue the conversation
    response2 = client.create(
        input="Should I bring an umbrella?",
        previous_response_id=response['id']
    )
    
    print(f"\nContinuation: {response2['output'][0]['content'][0]['text']}")


def example_2_postgresql():
    """Example 2: PostgreSQL (local or cloud)"""
    print("\n=== Example 2: PostgreSQL ===\n")
    
    # Option A: Direct connection string
    client = Client(db_url="postgresql://user:pass@localhost:5432/cortex")
    
    # Option B: From environment variable (recommended)
    # export DATABASE_URL=postgresql://user:pass@localhost:5432/cortex
    client = Client()  # Automatically uses DATABASE_URL if set
    
    response = client.create(
        input="Tell me about PostgreSQL",
        instructions="You are a database expert"
    )
    
    print(f"Response: {response['output'][0]['content'][0]['text']}")


def example_3_supabase():
    """Example 3: Supabase (PostgreSQL in the cloud)"""
    print("\n=== Example 3: Supabase ===\n")
    
    # Get your connection string from Supabase dashboard
    supabase_url = "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"
    
    # Or better, use environment variable
    supabase_url = os.getenv("SUPABASE_DB_URL")
    
    if supabase_url:
        client = Client(db_url=supabase_url)
        
        response = client.create(
            input="Hello from the cloud!",
            instructions="You are a cloud-native assistant"
        )
        
        print(f"Response: {response['output'][0]['content'][0]['text']}")
    else:
        print("Set SUPABASE_DB_URL in .env file to test Supabase")


def example_4_serverless():
    """Example 4: Serverless function (Vercel, AWS Lambda, etc)"""
    print("\n=== Example 4: Serverless Function ===\n")
    
    # In your serverless function:
    def handler(request):
        # The DATABASE_URL should be set as an environment variable
        # in your serverless platform (Vercel, AWS, etc)
        
        client = Client()  # Automatically uses DATABASE_URL
        
        response = client.create(
            input=request.get("message"),
            previous_response_id=request.get("previous_response_id"),
            instructions=request.get("instructions")
        )
        
        return {
            "response_id": response["id"],
            "message": response["output"][0]["content"][0]["text"]
        }
    
    # Simulate a request
    result = handler({
        "message": "Hello from serverless!",
        "instructions": "You are a serverless assistant"
    })
    
    print(f"Serverless response: {result}")


def example_5_environment_setup():
    """Example 5: Environment configuration"""
    print("\n=== Example 5: Environment Setup ===\n")
    
    print("Create a .env file with:")
    print("---")
    print("# For local PostgreSQL:")
    print("DATABASE_URL=postgresql://localhost:5432/cortex")
    print()
    print("# For Supabase:")
    print("DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres")
    print()
    print("# For Cohere LLM:")
    print("COHERE_API_KEY=your-api-key-here")
    print("---")
    
    # Show current configuration
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if "supabase" in db_url:
            print(f"\n✅ Currently configured for Supabase")
        elif "localhost" in db_url:
            print(f"\n✅ Currently configured for local PostgreSQL")
        else:
            print(f"\n✅ Currently configured for: {db_url[:30]}...")
    else:
        print("\n✅ Currently using SQLite (no DATABASE_URL set)")


def main():
    """Run examples based on environment"""
    print("\n" + "="*60)
    print("CORTEX DATABASE CONFIGURATION EXAMPLES")
    print("="*60)
    
    # Always show SQLite example (works everywhere)
    try:
        example_1_sqlite()
    except Exception as e:
        print(f"SQLite example error: {e}")
    
    # Show environment setup
    example_5_environment_setup()
    
    # Try PostgreSQL if configured
    if os.getenv("DATABASE_URL"):
        try:
            if "supabase" in os.getenv("DATABASE_URL", ""):
                example_3_supabase()
            else:
                example_2_postgresql()
        except Exception as e:
            print(f"\nPostgreSQL example error: {e}")
            print("Make sure your DATABASE_URL is correct")
    
    print("\n" + "="*60)
    print("QUICK START GUIDE")
    print("="*60)
    print("""
1. INSTALL POSTGRESQL SUPPORT (if needed):
   pip install "cortex[postgres]"

2. LOCAL DEVELOPMENT:
   from cortex import Client
   client = Client()  # Uses SQLite automatically

3. PRODUCTION WITH POSTGRESQL:
   client = Client(db_url="postgresql://...")
   
4. PRODUCTION WITH ENVIRONMENT VARIABLE:
   # Set DATABASE_URL in environment
   client = Client()  # Automatically uses DATABASE_URL

5. SERVERLESS (Vercel, AWS Lambda):
   # Set DATABASE_URL in platform settings
   client = Client()  # Works automatically
""")


if __name__ == "__main__":
    main()