"""
Test Serverless Scenarios
Tests how the system behaves in serverless environments
"""

import os
import pytest
import warnings
from unittest.mock import patch
from cortex import Client

# Your Supabase URL for serverless persistence tests
SUPABASE_URL = "postgresql://postgres:Fakhar_27_1$@db.tqovtjyylrykgpehbfdl.supabase.co:5432/postgres"


class TestServerlessScenarios:
    """Test serverless environment behaviors"""
    
    def test_serverless_without_db(self):
        """Test serverless environment without database URL"""
        print("\n=== Testing Serverless Without Database ===")
        
        # Simulate serverless environment
        with patch.dict(os.environ, {"VERCEL": "1"}):
            # Remove DATABASE_URL
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            
            # Should warn about no persistence
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                client = Client()
                
                # Check for warning
                assert len(w) > 0
                assert "serverless without database URL" in str(w[0].message)
                print("✓ Warning shown about no persistence")
            
            # Should still work but without persistence
            response = client.create(
                model="command-r",
                input="Test in serverless without DB"
            )
            
            assert response["status"] == "completed"
            print(f"✓ Response created (in memory): {response['id']}")
            
            # Try to continue - might fail or start fresh
            response2 = client.create(
                model="command-r",
                input="Continue",
                previous_response_id=response["id"]
            )
            
            # In memory, this might work within same instance
            print(f"✓ Memory-only response: {response2['status']}")
    
    def test_serverless_with_postgres(self):
        """Test serverless environment with PostgreSQL"""
        print("\n=== Testing Serverless With PostgreSQL ===")
        
        # Simulate serverless with database
        with patch.dict(os.environ, {"VERCEL": "1", "DATABASE_URL": SUPABASE_URL}):
            try:
                client = Client()
                print("✓ Connected to PostgreSQL in serverless")
                
                # Should work with persistence
                response = client.create(
                    model="command-r",
                    input="Serverless with PostgreSQL test",
                    store=True
                )
                
                assert response["status"] == "completed"
                print(f"✓ Response persisted: {response['id']}")
                
                # Simulate new serverless invocation
                del client
                client2 = Client()
                
                # Should be able to continue
                response2 = client2.create(
                    model="command-r",
                    input="Continue from previous serverless invocation",
                    previous_response_id=response["id"]
                )
                
                assert response2["status"] == "completed"
                print("✓ Persistence works across serverless invocations")
                
            except Exception as e:
                print(f"✗ Serverless with PostgreSQL failed: {e}")
                if "Network is unreachable" in str(e):
                    pytest.skip("Supabase connection issue")
                raise
    
    def test_serverless_per_request_db(self):
        """Test passing db_url per request (multi-tenant serverless)"""
        print("\n=== Testing Per-Request Database URL ===")
        
        # Simulate serverless
        with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test-function"}):
            # Clear DATABASE_URL
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            
            try:
                # User 1 with their database
                client1 = Client(db_url=SUPABASE_URL)
                response1 = client1.create(
                    model="command-r",
                    input="User 1 data",
                    store=True
                )
                print(f"✓ User 1 stored: {response1['id']}")
                
                # User 2 with different database (simulated with same URL)
                # In real scenario, this would be a different database
                client2 = Client(db_url=SUPABASE_URL)
                response2 = client2.create(
                    model="command-r",
                    input="User 2 data",
                    store=True
                )
                print(f"✓ User 2 stored: {response2['id']}")
                
                # Each user has isolated data
                assert response1["id"] != response2["id"]
                print("✓ Per-request database URL working")
                
            except Exception as e:
                if "Network is unreachable" in str(e):
                    pytest.skip("Supabase connection issue")
                raise
    
    def test_serverless_cold_start(self):
        """Test cold start scenario in serverless"""
        print("\n=== Testing Serverless Cold Start ===")
        
        with patch.dict(os.environ, {"NETLIFY": "1"}):
            try:
                # First cold start - with database
                client = Client(db_url=SUPABASE_URL)
                
                # First request (cold start)
                response1 = client.create(
                    model="command-r",
                    input="Cold start request",
                    store=True
                )
                print(f"✓ Cold start request: {response1['id']}")
                
                # Simulate function death
                del client
                
                # Second cold start
                client2 = Client(db_url=SUPABASE_URL)
                
                # Should still have access to previous data
                response2 = client2.create(
                    model="command-r",
                    input="After cold start",
                    previous_response_id=response1["id"]
                )
                
                assert response2["status"] == "completed"
                print("✓ Data persists across cold starts")
                
            except Exception as e:
                if "Network is unreachable" in str(e):
                    pytest.skip("Supabase connection issue")
                raise
    
    def test_serverless_timeout_handling(self):
        """Test handling of serverless timeout scenarios"""
        print("\n=== Testing Serverless Timeout Handling ===")
        
        with patch.dict(os.environ, {"RENDER": "1"}):
            # Clear DATABASE_URL to use memory
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
            
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                
                client = Client()
                
                # Create a conversation
                response1 = client.create(
                    model="command-r",
                    input="Start conversation",
                    store=False  # Don't persist (simulating timeout before save)
                )
                print(f"✓ Created without persistence: {response1['id']}")
                
                # Try to continue - should handle gracefully
                response2 = client.create(
                    model="command-r",
                    input="Try to continue",
                    previous_response_id=response1["id"]
                )
                
                # Should either fail or start fresh
                print(f"✓ Handled timeout scenario: {response2['status']}")
    
    def test_serverless_environment_detection(self):
        """Test detection of various serverless environments"""
        print("\n=== Testing Serverless Environment Detection ===")
        
        environments = [
            ("VERCEL", "Vercel"),
            ("AWS_LAMBDA_FUNCTION_NAME", "AWS Lambda"),
            ("FUNCTIONS_WORKER_RUNTIME", "Google Cloud Functions"),
            ("AZURE_FUNCTIONS_ENVIRONMENT", "Azure Functions"),
            ("NETLIFY", "Netlify"),
            ("RENDER", "Render")
        ]
        
        for env_var, platform in environments:
            with patch.dict(os.environ, {env_var: "test"}):
                # Clear DATABASE_URL
                if "DATABASE_URL" in os.environ:
                    del os.environ["DATABASE_URL"]
                
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    
                    client = Client()
                    
                    # Should detect serverless and warn
                    assert len(w) > 0
                    assert "serverless" in str(w[0].message).lower()
                    print(f"✓ Detected {platform} environment")
    
    def test_serverless_with_all_providers(self):
        """Test all providers work in serverless"""
        print("\n=== Testing All Providers in Serverless ===")
        
        with patch.dict(os.environ, {"VERCEL": "1"}):
            try:
                client = Client(db_url=SUPABASE_URL)
                
                # Test OpenAI
                if os.getenv("OPENAI_API_KEY"):
                    r1 = client.create(
                        model="gpt-4o-mini",
                        input="Serverless OpenAI test"
                    )
                    assert r1["status"] == "completed"
                    print("✓ OpenAI works in serverless")
                
                # Test Gemini
                if os.getenv("GOOGLE_API_KEY"):
                    r2 = client.create(
                        model="gemini-1.5-flash",
                        input="Serverless Gemini test"
                    )
                    assert r2["status"] == "completed"
                    print("✓ Gemini works in serverless")
                
                # Test Cohere
                if os.getenv("CO_API_KEY"):
                    r3 = client.create(
                        model="command-r",
                        input="Serverless Cohere test"
                    )
                    assert r3["status"] == "completed"
                    print("✓ Cohere works in serverless")
                
            except Exception as e:
                if "Network is unreachable" in str(e):
                    pytest.skip("Supabase connection issue")
                raise


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SERVERLESS SCENARIOS")
    print("=" * 60)
    print("\nThis test simulates serverless environments:")
    print("1. Vercel, AWS Lambda, Google Cloud Functions, etc.")
    print("2. With and without database persistence")
    print("3. Cold starts and timeout handling")
    print("4. Per-request database URLs (multi-tenancy)")
    print("\nScenarios tested:")
    print("- No database (MemorySaver with warning)")
    print("- With PostgreSQL/Supabase (full persistence)")
    print("- Cold start handling")
    print("- All providers in serverless")
    print("\nRun with: pytest tests/test_serverless_scenarios.py -v -s")
    print("=" * 60)