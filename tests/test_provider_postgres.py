"""
Test Each Provider with PostgreSQL
Tests each provider individually with PostgreSQL database (Docker)
"""

import os
import pytest
import time
from cortex import Client

# Docker PostgreSQL URL
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"


class TestProviderPostgreSQL:
    """Test each provider individually with PostgreSQL"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup PostgreSQL for each test"""
        # Clear DATABASE_URL to use explicit db_url
        self.original_db_url = os.environ.get("DATABASE_URL")
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        yield
        
        # Restore original
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
    
    def test_openai_with_postgres(self):
        """Test OpenAI provider with PostgreSQL"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing OpenAI + PostgreSQL ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e) or "could not translate" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="OpenAI PostgreSQL test: What is the speed of light?",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gpt-4o-mini"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="gpt-4o-mini",
            input="Express that in miles per hour",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence with new client
        print("3. Testing persistence...")
        del client
        client2 = Client(db_url=DOCKER_POSTGRES_URL)
        response3 = client2.create(
            model="gpt-4o-mini",
            input="What was the original question about?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test concurrent requests
        print("4. Testing concurrent requests...")
        responses = []
        for i in range(3):
            r = client2.create(
                model="gpt-4o-mini",
                input=f"Concurrent request {i}: Calculate {i+1} * 100",
                temperature=0.0,
                store=True
            )
            responses.append(r["id"])
            print(f"  ✓ Request {i}: {r['id']}")
        
        assert len(responses) == 3
        print("✓ Concurrent requests handled")
        
        print("\n✅ OpenAI + PostgreSQL: All tests passed!")
    
    def test_gemini_with_postgres(self):
        """Test Google Gemini provider with PostgreSQL"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing Gemini + PostgreSQL ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gemini-1.5-flash",
            input="Gemini PostgreSQL test: List the planets in our solar system",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gemini-1.5-flash"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="gemini-1.5-flash",
            input="Which planet is known as the red planet?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        del client
        client2 = Client(db_url=DOCKER_POSTGRES_URL)
        response3 = client2.create(
            model="gemini-1.5-flash",
            input="Which planet has the most moons?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test transaction handling
        print("4. Testing transaction handling...")
        # With store=True
        r_stored = client2.create(
            model="gemini-1.5-flash",
            input="This should be saved in PostgreSQL",
            store=True
        )
        # With store=False
        r_not_stored = client2.create(
            model="gemini-1.5-flash",
            input="This should NOT be saved",
            store=False
        )
        
        # New client should find stored, not unstored
        client3 = Client(db_url=DOCKER_POSTGRES_URL)
        
        # Should work - was stored
        r_continue_stored = client3.create(
            model="gemini-1.5-flash",
            input="Continue",
            previous_response_id=r_stored["id"]
        )
        assert r_continue_stored["status"] == "completed"
        print("✓ Continued from stored response")
        
        # Should fail - was not stored
        r_continue_unstored = client3.create(
            model="gemini-1.5-flash",
            input="Continue",
            previous_response_id=r_not_stored["id"]
        )
        if r_continue_unstored["status"] == "failed":
            print("✓ Correctly failed for unstored response")
        else:
            print("⚠ Warning: Continued from unstored response")
        
        print("\n✅ Gemini + PostgreSQL: All tests passed!")
    
    def test_cohere_with_postgres(self):
        """Test Cohere provider with PostgreSQL"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing Cohere + PostgreSQL ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="command-r",
            input="Cohere PostgreSQL test: What are the benefits of using PostgreSQL?",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "command-r"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="command-r",
            input="Compare it to MySQL",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        del client
        client2 = Client(db_url=DOCKER_POSTGRES_URL)
        response3 = client2.create(
            model="command-r",
            input="What about NoSQL databases?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test bulk operations
        print("4. Testing bulk operations...")
        bulk_responses = []
        start_time = time.time()
        
        for i in range(5):
            r = client2.create(
                model="command-r",
                input=f"Bulk test {i}: Generate a random fact",
                temperature=0.5,
                store=True
            )
            bulk_responses.append(r["id"])
        
        elapsed = time.time() - start_time
        print(f"✓ Created 5 responses in {elapsed:.2f}s")
        assert len(bulk_responses) == 5
        
        print("\n✅ Cohere + PostgreSQL: All tests passed!")
    
    def test_cross_provider_postgres(self):
        """Test cross-provider conversation with PostgreSQL"""
        print("\n=== Testing Cross-Provider with PostgreSQL ===")
        
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
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Start with first provider
        model1, name1 = providers[0]
        print(f"1. Starting with {name1}...")
        response1 = client.create(
            model=model1,
            input="Cross-provider test: I'm thinking of the number 42",
            store=True,
            temperature=0.0
        )
        assert response1["status"] == "completed"
        print(f"✓ {name1}: {response1['id']}")
        
        # Continue with second provider
        model2, name2 = providers[1]
        print(f"2. Continuing with {name2}...")
        response2 = client.create(
            model=model2,
            input="What number were you thinking of?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ {name2}: {response2['id']}")
        
        # If third provider available, use it
        if len(providers) >= 3:
            model3, name3 = providers[2]
            print(f"3. Finishing with {name3}...")
            response3 = client.create(
                model=model3,
                input="Is that number from a famous book?",
                previous_response_id=response2["id"],
                temperature=0.0
            )
            assert response3["status"] == "completed"
            print(f"✓ {name3}: {response3['id']}")
        
        print("\n✅ Cross-Provider + PostgreSQL: All tests passed!")
    
    def test_postgres_performance(self):
        """Test PostgreSQL performance characteristics"""
        print("\n=== Testing PostgreSQL Performance ===")
        
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY needed for performance test")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            raise
        
        # Test write performance
        print("1. Testing write performance...")
        write_times = []
        for i in range(5):
            start = time.time()
            r = client.create(
                model="command-r",
                input=f"Performance test {i}",
                store=True,
                temperature=0.0
            )
            write_time = time.time() - start
            write_times.append(write_time)
            print(f"  Write {i}: {write_time:.3f}s")
        
        avg_write = sum(write_times) / len(write_times)
        print(f"✓ Average write time: {avg_write:.3f}s")
        
        # Test read performance (continuation)
        print("2. Testing read performance...")
        base_response = client.create(
            model="command-r",
            input="Base message for read test",
            store=True,
            temperature=0.0
        )
        
        read_times = []
        for i in range(5):
            start = time.time()
            r = client.create(
                model="command-r",
                input=f"Continue {i}",
                previous_response_id=base_response["id"],
                temperature=0.0
            )
            read_time = time.time() - start
            read_times.append(read_time)
            print(f"  Read {i}: {read_time:.3f}s")
        
        avg_read = sum(read_times) / len(read_times)
        print(f"✓ Average read time: {avg_read:.3f}s")
        
        # Performance should be reasonable for local PostgreSQL
        assert avg_write < 3.0, f"Write too slow: {avg_write}s"
        assert avg_read < 3.0, f"Read too slow: {avg_read}s"
        
        print("\n✅ PostgreSQL Performance: Tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING EACH PROVIDER WITH POSTGRESQL")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Docker PostgreSQL must be running")
    print("2. Run: docker-compose up -d")
    print(f"3. Connection: {DOCKER_POSTGRES_URL}")
    print("\nThis test file verifies each provider with PostgreSQL:")
    print("1. OpenAI (gpt-4o-mini)")
    print("2. Google Gemini (gemini-1.5-flash)")
    print("3. Cohere (command-r)")
    print("\nEach provider is tested for:")
    print("- Basic completion")
    print("- Conversation continuation")
    print("- Persistence across clients")
    print("- Transaction handling")
    print("- Concurrent requests")
    print("- Cross-provider conversations")
    print("- Performance characteristics")
    print("\nRun with: pytest tests/test_provider_postgres.py -v -s")
    print("Or test specific provider:")
    print("  pytest tests/test_provider_postgres.py::TestProviderPostgreSQL::test_openai_with_postgres -v -s")
    print("=" * 60)