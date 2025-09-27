#!/usr/bin/env python3
"""
Test that simulates exactly what lambda_handler.py does
This will help us reproduce the transaction blocking issue
"""

import os
import json
import time

# Set Lambda environment 
os.environ['AWS_LAMBDA_FUNCTION_NAME'] = 'cortex-test'

def simulate_lambda_request(db_url, model="gpt-4o-mini", use_fresh_db=True):
    """
    Simulate exactly what lambda_handler does:
    1. from cortex import Client
    2. client = Client(db_url=db_url) 
    3. client.create(...)
    """
    
    print(f"🧪 Testing Lambda simulation with {model}")
    print(f"   Fresh DB: {use_fresh_db}")
    print(f"   DB URL: {db_url[:50]}...")
    
    try:
        # This is exactly what lambda_handler.py does
        from cortex import Client
        
        # Simulate the lambda request body
        body = {
            "input": "hello my name is fakhar and i like apples",
            "model": model,
            "db_url": db_url,
            "store": True,
            "instructions": "reply to each question like you are tony stark"
        }
        
        start_time = time.time()
        
        # This line is where the transaction issue happens
        client = Client(db_url=db_url)
        print("✅ Client created successfully")
        
        # This triggers the checkpointer setup and potential transaction block
        response = client.create(
            input=body["input"],
            model=body["model"],
            store=body["store"],
            instructions=body["instructions"]
        )
        
        execution_time = time.time() - start_time
        print(f"✅ Request completed in {execution_time:.2f}s")
        print(f"   Response ID: {response.get('id', 'None')}")
        print(f"   Status: {response.get('status', 'unknown')}")
        
        if response.get('status') == 'failed':
            print(f"❌ Request failed: {response.get('error', {}).get('message', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Exception during simulation: {e}")
        
        # Check for specific transaction error
        if "current transaction is aborted" in str(e):
            print("🔍 FOUND THE TRANSACTION BLOCK ERROR!")
            print("   This confirms the setup is corrupting the connection")
        
        import traceback
        traceback.print_exc()
        return False

def test_multiple_models():
    """Test different models to see which ones work"""
    
    db_url = "postgresql://postgres.tufdswbxffpoifosusvg:22E8HwfuCfvkr4eY@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
    
    models_to_test = [
        "gpt-4o-mini",           # OpenAI - should work
        "command-r-08-2024",     # New Cohere - should work  
        "gemini-2.0-flash",      # New Gemini - test if fixed
        "gemini-1.5-flash",      # Old Gemini - should show deprecation
    ]
    
    results = {}
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing Model: {model}")
        print(f"{'='*60}")
        
        success = simulate_lambda_request(db_url, model)
        results[model] = success
        
        # Small delay between tests
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    
    for model, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{model:<20} {status}")
    
    return results

def test_fresh_db_behavior():
    """Test the fresh database behavior that's causing issues"""
    
    print("🧪 Testing fresh database setup behavior...")
    
    db_url = "postgresql://postgres.tufdswbxffpoifosusvg:22E8HwfuCfvkr4eY@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
    
    print("\n--- Testing FRESH database first request ---")
    result = simulate_lambda_request(db_url, "gpt-4o-mini", use_fresh_db=True)
    
    if result:
        print("✅ Fresh database test PASSED!")
        print("   The transaction fix appears to be working")
    else:
        print("❌ Fresh database test FAILED!")
        print("   The transaction blocking issue persists")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Lambda simulation tests...")
    
    # Test 1: Multiple models
    print("\n" + "="*80)
    print("TEST 1: Multiple Models")
    print("="*80)
    test_multiple_models()
    
    # Test 2: Fresh database behavior
    print("\n" + "="*80)  
    print("TEST 2: Fresh Database Behavior")
    print("="*80)
    test_fresh_db_behavior()
    
    print("\n🏁 Tests completed!")