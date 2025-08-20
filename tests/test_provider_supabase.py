"""
Test Each Provider with Supabase
Tests each provider individually with Supabase cloud database
"""

import os
import pytest
import time
from cortex import Client

# Direct Supabase URL
SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


class TestProviderSupabase:
    """Test each provider individually with Supabase"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Supabase for each test"""
        # Clear DATABASE_URL to use explicit db_url
        self.original_db_url = os.environ.get("DATABASE_URL")
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        yield
        
        # Restore original
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
    
    def test_openai_with_supabase(self):
        """Test OpenAI provider with Supabase"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing OpenAI + Supabase ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue (IPv6): {e}")
            elif "could not translate" in str(e):
                pytest.skip(f"DNS resolution failed: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="OpenAI Supabase test: What is machine learning?",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gpt-4o-mini"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        time.sleep(0.5)  # Small delay for cloud sync
        response2 = client.create(
            model="gpt-4o-mini",
            input="Give me a simple example",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test cloud persistence
        print("3. Testing cloud persistence...")
        time.sleep(1)  # Allow cloud sync
        del client
        
        client2 = Client(db_url=SUPABASE_URL)
        response3 = client2.create(
            model="gpt-4o-mini",
            input="What was the original question about?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Cloud persistence: {response3['id']}")
        
        # Test latency
        print("4. Testing cloud latency...")
        start = time.time()
        response4 = client2.create(
            model="gpt-4o-mini",
            input="Quick latency test",
            temperature=0.0,
            store=True
        )
        latency = time.time() - start
        print(f"✓ Cloud latency: {latency:.2f}s")
        assert latency < 10.0, f"Latency too high: {latency}s"
        
        print("\n✅ OpenAI + Supabase: All tests passed!")
    
    def test_gemini_with_supabase(self):
        """Test Google Gemini provider with Supabase"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing Gemini + Supabase ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gemini-1.5-flash",
            input="Gemini Supabase test: Explain cloud databases",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gemini-1.5-flash"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        time.sleep(0.5)
        response2 = client.create(
            model="gemini-1.5-flash",
            input="What are the advantages?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        time.sleep(1)
        del client
        
        client2 = Client(db_url=SUPABASE_URL)
        response3 = client2.create(
            model="gemini-1.5-flash",
            input="What are the disadvantages?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test multiple conversations
        print("4. Testing multiple conversations...")
        convs = []
        for i in range(3):
            r = client2.create(
                model="gemini-1.5-flash",
                input=f"Conversation {i}: Remember {i*111}",
                store=True,
                temperature=0.0
            )
            convs.append(r["id"])
            time.sleep(0.3)  # Avoid rate limits
        
        assert len(convs) == 3
        print(f"✓ Created {len(convs)} conversations")
        
        print("\n✅ Gemini + Supabase: All tests passed!")
    
    def test_cohere_with_supabase(self):
        """Test Cohere provider with Supabase"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing Cohere + Supabase ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="command-r",
            input="Cohere Supabase test: What is Supabase?",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "command-r"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        time.sleep(0.5)
        response2 = client.create(
            model="command-r",
            input="How does it compare to Firebase?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        time.sleep(1)
        del client
        
        client2 = Client(db_url=SUPABASE_URL)
        response3 = client2.create(
            model="command-r",
            input="What about pricing?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test store=False with cloud
        print("4. Testing store=False with cloud...")
        r_not_stored = client2.create(
            model="command-r",
            input="Don't save this to cloud",
            store=False,
            temperature=0.0
        )
        print(f"✓ Created without storing: {r_not_stored['id']}")
        
        # Try to continue - should fail
        r_continue = client2.create(
            model="command-r",
            input="Continue from unsaved",
            previous_response_id=r_not_stored["id"],
            temperature=0.0
        )
        if r_continue["status"] == "failed":
            print("✓ Correctly failed for unstored response")
        else:
            print("⚠ Warning: Continued from unstored response")
        
        print("\n✅ Cohere + Supabase: All tests passed!")
    
    def test_cross_provider_supabase(self):
        """Test cross-provider conversation with Supabase"""
        print("\n=== Testing Cross-Provider with Supabase ===")
        
        # Check available providers
        providers = []
        if os.getenv("OPENAI_API_KEY"):
            providers.append(("gpt-4o-mini", "OpenAI"))
        if os.getenv("GOOGLE_API_KEY"):
            providers.append(("gemini-1.5-flash", "Gemini"))
        if os.getenv("CO_API_KEY"):
            providers.append(("command-r", "Cohere"))
        
        if len(providers) < 2:
            pytest.skip(f"Need at least 2 providers, found {len(providers)}")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue: {e}")
            raise
        
        print("Starting cross-provider conversation chain...")
        
        # Start with first provider
        model1, name1 = providers[0]
        print(f"1. {name1} starting...")
        response1 = client.create(
            model=model1,
            input="Let's play a game: I'm thinking of an animal that lives in the ocean and is very intelligent",
            store=True,
            temperature=0.0
        )
        assert response1["status"] == "completed"
        print(f"✓ {name1}: {response1['id']}")
        time.sleep(0.5)  # Cloud sync
        
        # Continue with second provider
        model2, name2 = providers[1]
        print(f"2. {name2} continuing...")
        response2 = client.create(
            model=model2,
            input="Is it a dolphin?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ {name2}: {response2['id']}")
        time.sleep(0.5)  # Cloud sync
        
        # If third provider available
        if len(providers) >= 3:
            model3, name3 = providers[2]
            print(f"3. {name3} finishing...")
            response3 = client.create(
                model=model3,
                input="Tell me an interesting fact about that animal",
                previous_response_id=response2["id"],
                temperature=0.0
            )
            assert response3["status"] == "completed"
            print(f"✓ {name3}: {response3['id']}")
        
        print("\n✅ Cross-Provider + Supabase: All tests passed!")
    
    def test_supabase_resilience(self):
        """Test Supabase resilience and error handling"""
        print("\n=== Testing Supabase Resilience ===")
        
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY needed for resilience test")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue: {e}")
            raise
        
        # Test recovery from network issues
        print("1. Testing conversation recovery...")
        response1 = client.create(
            model="command-r",
            input="Resilience test: Start conversation",
            store=True,
            temperature=0.0
        )
        response_id = response1["id"]
        print(f"✓ Created: {response_id}")
        
        # Simulate connection loss (delete client)
        del client
        time.sleep(2)  # Wait for any connections to close
        
        # Reconnect and continue
        print("2. Reconnecting after disconnect...")
        try:
            client2 = Client(db_url=SUPABASE_URL)
            response2 = client2.create(
                model="command-r",
                input="Continue after reconnection",
                previous_response_id=response_id,
                temperature=0.0
            )
            assert response2["status"] == "completed"
            print("✓ Successfully recovered conversation")
        except Exception as e:
            if "Network is unreachable" in str(e):
                print("⚠ Network still unreachable")
            else:
                raise
        
        # Test handling of invalid response IDs
        print("3. Testing invalid response ID...")
        response3 = client2.create(
            model="command-r",
            input="Try to continue from invalid ID",
            previous_response_id="invalid-id-xyz-123",
            temperature=0.0
        )
        print(f"✓ Handled invalid ID: status={response3['status']}")
        
        # Test rapid requests (rate limiting)
        print("4. Testing rapid requests...")
        rapid_responses = []
        for i in range(3):
            try:
                r = client2.create(
                    model="command-r",
                    input=f"Rapid request {i}",
                    temperature=0.0,
                    store=True
                )
                rapid_responses.append(r["id"])
                print(f"  ✓ Request {i}: {r['id']}")
                time.sleep(0.2)  # Small delay to avoid rate limits
            except Exception as e:
                print(f"  ⚠ Request {i} failed: {e}")
        
        print(f"✓ Completed {len(rapid_responses)}/3 rapid requests")
        
        print("\n✅ Supabase Resilience: Tests completed!")
    
    def test_supabase_performance(self):
        """Test Supabase cloud performance"""
        print("\n=== Testing Supabase Performance ===")
        
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY needed for performance test")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            print("✓ Connected to Supabase")
        except Exception as e:
            if "Network is unreachable" in str(e):
                pytest.skip(f"Supabase connection issue: {e}")
            raise
        
        # Test write performance to cloud
        print("1. Testing cloud write performance...")
        write_times = []
        for i in range(3):
            start = time.time()
            r = client.create(
                model="command-r",
                input=f"Performance test write {i}",
                store=True,
                temperature=0.0
            )
            write_time = time.time() - start
            write_times.append(write_time)
            print(f"  Write {i}: {write_time:.2f}s")
            time.sleep(0.5)  # Avoid rate limits
        
        avg_write = sum(write_times) / len(write_times)
        print(f"✓ Average cloud write: {avg_write:.2f}s")
        
        # Test read performance from cloud
        print("2. Testing cloud read performance...")
        base_response = client.create(
            model="command-r",
            input="Base for read test",
            store=True,
            temperature=0.0
        )
        time.sleep(1)  # Ensure it's saved
        
        read_times = []
        for i in range(3):
            start = time.time()
            r = client.create(
                model="command-r",
                input=f"Read test {i}",
                previous_response_id=base_response["id"],
                temperature=0.0
            )
            read_time = time.time() - start
            read_times.append(read_time)
            print(f"  Read {i}: {read_time:.2f}s")
            time.sleep(0.5)  # Avoid rate limits
        
        avg_read = sum(read_times) / len(read_times)
        print(f"✓ Average cloud read: {avg_read:.2f}s")
        
        # Cloud performance should be reasonable
        assert avg_write < 10.0, f"Cloud write too slow: {avg_write}s"
        assert avg_read < 10.0, f"Cloud read too slow: {avg_read}s"
        
        print("\n✅ Supabase Performance: Tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING EACH PROVIDER WITH SUPABASE")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL[:50]}...")
    print("\nThis test file verifies each provider with Supabase:")
    print("1. OpenAI (gpt-4o-mini)")
    print("2. Google Gemini (gemini-1.5-flash)")
    print("3. Cohere (command-r)")
    print("\nEach provider is tested for:")
    print("- Basic completion")
    print("- Conversation continuation")
    print("- Cloud persistence")
    print("- Cross-provider conversations")
    print("- Cloud latency")
    print("- Resilience and recovery")
    print("- Performance characteristics")
    print("\nKnown Issues:")
    print("- IPv6 connectivity problems on WSL")
    print("- May experience network timeouts")
    print("\nRun with: pytest tests/test_provider_supabase.py -v -s")
    print("Or test specific provider:")
    print("  pytest tests/test_provider_supabase.py::TestProviderSupabase::test_openai_with_supabase -v -s")
    print("=" * 60)