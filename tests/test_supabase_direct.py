"""
Test Supabase Direct Connection
Tests with direct Supabase URL: postgresql://postgres:Fakhar_27_1$@db.tqovtjyylrykgpehbfdl.supabase.co:5432/postgres
"""

import os
import pytest
import time
from cortex import Client

# Your direct Supabase URL
SUPABASE_DIRECT_URL = "postgresql://postgres:Fakhar_27_1$@db.tqovtjyylrykgpehbfdl.supabase.co:5432/postgres"


class TestSupabaseDirect:
    """Test with direct Supabase connection"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        # Store original DATABASE_URL
        self.original_db_url = os.environ.get("DATABASE_URL")
        
        # Clear it to ensure we use explicit db_url
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        yield
        
        # Restore original
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
    
    def test_supabase_direct_connection(self):
        """Test direct connection to Supabase"""
        print("\n=== Testing Supabase Direct Connection ===")
        print(f"Connecting to: {SUPABASE_DIRECT_URL[:50]}...")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            print("✓ Connected to Supabase successfully!")
            
            # Test creating a response
            response = client.create(
                model="command-r",
                input="Test Supabase direct connection"
            )
            
            assert response["status"] == "completed"
            print(f"✓ Response created: {response['id']}")
            return response["id"]
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            if "Network is unreachable" in str(e):
                print("  Issue: IPv6 connectivity problem")
                print("  Solution: Try using pooler URL or fix IPv6")
            elif "password authentication failed" in str(e):
                print("  Issue: Invalid password")
                print("  Check: Is 'Fakhar_27_1$' the correct password?")
            elif "could not translate host name" in str(e):
                print("  Issue: DNS resolution failed")
                print("  Check: Internet connection and DNS")
            raise
    
    def test_supabase_persistence(self):
        """Test data persistence in Supabase"""
        print("\n=== Testing Supabase Persistence ===")
        
        try:
            # First client - create data
            client1 = Client(db_url=SUPABASE_DIRECT_URL)
            response1 = client1.create(
                model="command-r",
                input="Supabase test: My secret code is ALPHA-2024",
                store=True
            )
            response_id = response1["id"]
            print(f"✓ Created response in Supabase: {response_id}")
            
            # Small delay for cloud sync
            time.sleep(1)
            
            # Delete first client
            del client1
            
            # Second client - retrieve from Supabase
            client2 = Client(db_url=SUPABASE_DIRECT_URL)
            response2 = client2.create(
                model="command-r",
                input="What was the secret code?",
                previous_response_id=response_id
            )
            
            assert response2["status"] == "completed"
            assert response2["previous_response_id"] == response_id
            print("✓ Successfully retrieved from Supabase")
            print("✓ Supabase persistence working!")
            
        except Exception as e:
            print(f"✗ Persistence test failed: {e}")
            raise
    
    def test_supabase_with_openai(self):
        """Test Supabase with OpenAI provider"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing Supabase + OpenAI ===")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            
            # Create with OpenAI
            response = client.create(
                model="gpt-4o-mini",
                input="Supabase + OpenAI test: What is 10 * 10?",
                temperature=0.0
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "gpt-4o-mini"
            print(f"✓ OpenAI + Supabase working: {response['id']}")
            
            # Test persistence
            response2 = client.create(
                model="gpt-4o-mini",
                input="What calculation did I just ask?",
                previous_response_id=response["id"]
            )
            
            assert response2["status"] == "completed"
            print("✓ Conversation persistence with OpenAI + Supabase")
            
        except Exception as e:
            print(f"✗ OpenAI + Supabase failed: {e}")
            raise
    
    def test_supabase_with_gemini(self):
        """Test Supabase with Google Gemini"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing Supabase + Gemini ===")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            
            response = client.create(
                model="gemini-1.5-flash",
                input="Supabase + Gemini test: Name the largest ocean",
                temperature=0.0
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "gemini-1.5-flash"
            print(f"✓ Gemini + Supabase working: {response['id']}")
            
        except Exception as e:
            print(f"✗ Gemini + Supabase failed: {e}")
            raise
    
    def test_supabase_with_cohere(self):
        """Test Supabase with Cohere"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing Supabase + Cohere ===")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            
            response = client.create(
                model="command-r",
                input="Supabase + Cohere test: Generate a greeting",
                temperature=0.5
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "command-r"
            print(f"✓ Cohere + Supabase working: {response['id']}")
            
        except Exception as e:
            print(f"✗ Cohere + Supabase failed: {e}")
            raise
    
    def test_supabase_cross_provider_conversation(self):
        """Test conversation across different providers with Supabase"""
        print("\n=== Testing Cross-Provider Conversation ===")
        
        required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "CO_API_KEY"]
        missing = [k for k in required_keys if not os.getenv(k)]
        if missing:
            pytest.skip(f"Missing API keys: {', '.join(missing)}")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            
            # Start with Cohere
            r1 = client.create(
                model="command-r",
                input="I'm starting a story: Once upon a time in 2024...",
                store=True
            )
            print(f"✓ Cohere started conversation: {r1['id']}")
            
            # Continue with OpenAI
            r2 = client.create(
                model="gpt-4o-mini",
                input="Continue the story with one sentence",
                previous_response_id=r1["id"]
            )
            print(f"✓ OpenAI continued: {r2['id']}")
            
            # Finish with Gemini
            r3 = client.create(
                model="gemini-1.5-flash",
                input="End the story with one sentence",
                previous_response_id=r2["id"]
            )
            print(f"✓ Gemini concluded: {r3['id']}")
            
            assert r2["previous_response_id"] == r1["id"]
            assert r3["previous_response_id"] == r2["id"]
            print("✓ Cross-provider conversation working with Supabase!")
            
        except Exception as e:
            print(f"✗ Cross-provider test failed: {e}")
            raise
    
    def test_supabase_latency(self):
        """Test latency with Supabase cloud database"""
        print("\n=== Testing Supabase Latency ===")
        
        try:
            client = Client(db_url=SUPABASE_DIRECT_URL)
            
            # Measure create latency
            start = time.time()
            response = client.create(
                model="command-r",
                input="Latency test",
                store=True
            )
            create_time = time.time() - start
            print(f"✓ Create latency: {create_time:.2f}s")
            
            # Measure retrieval latency
            start = time.time()
            response2 = client.create(
                model="command-r",
                input="Continue",
                previous_response_id=response["id"]
            )
            retrieve_time = time.time() - start
            print(f"✓ Retrieve latency: {retrieve_time:.2f}s")
            
            # Check if latency is reasonable (< 5s for cloud)
            assert create_time < 5.0, f"Create too slow: {create_time}s"
            assert retrieve_time < 5.0, f"Retrieve too slow: {retrieve_time}s"
            print("✓ Supabase latency acceptable")
            
        except Exception as e:
            print(f"✗ Latency test failed: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SUPABASE DIRECT CONNECTION")
    print("=" * 60)
    print(f"\nDirect URL: {SUPABASE_DIRECT_URL[:50]}...")
    print("\nThis test verifies:")
    print("1. Direct connection to Supabase")
    print("2. Data persistence in cloud")
    print("3. All providers work with Supabase")
    print("4. Cross-provider conversations")
    print("5. Cloud latency")
    print("\nKnown Issues:")
    print("- IPv6 connectivity problems on WSL")
    print("- May need to use pooler URL instead")
    print("\nRun with: pytest tests/test_supabase_direct.py -v -s")
    print("=" * 60)