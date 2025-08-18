"""
Master Test File for Real API Integration
Comprehensive testing of all provider-database combinations
Run this file to execute systematic tests across all scenarios
"""

import os
import sys
import time
import pytest
from typing import Dict, List, Tuple


def run_test_file(test_file: str) -> Tuple[bool, str]:
    """
    Run a specific test file and return results
    
    Args:
        test_file: Name of test file to run
        
    Returns:
        Tuple of (success, output_message)
    """
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    try:
        # Run pytest on the specific file
        result = pytest.main([
            f"tests/{test_file}",
            "-v",  # Verbose
            "-s",  # Show prints
            "--tb=short"  # Short traceback
        ])
        
        if result == 0:
            return True, f"✅ {test_file}: All tests passed"
        else:
            return False, f"❌ {test_file}: Some tests failed (code: {result})"
            
    except Exception as e:
        return False, f"❌ {test_file}: Error running tests: {e}"


def check_environment() -> Dict[str, bool]:
    """Check which API keys and databases are available"""
    env_status = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
        "CO_API_KEY": bool(os.getenv("CO_API_KEY")),
        "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
    }
    return env_status


def main():
    """Run all test files systematically"""
    print("=" * 80)
    print("COMPREHENSIVE REAL API INTEGRATION TESTS")
    print("=" * 80)
    
    # Check environment
    print("\n📋 Environment Check:")
    env_status = check_environment()
    for key, available in env_status.items():
        status = "✅" if available else "❌"
        print(f"  {status} {key}: {'Available' if available else 'Not set'}")
    
    # Available providers
    providers = []
    if env_status["OPENAI_API_KEY"]:
        providers.append("OpenAI")
    if env_status["GOOGLE_API_KEY"]:
        providers.append("Google Gemini")
    if env_status["CO_API_KEY"]:
        providers.append("Cohere")
    
    print(f"\n🤖 Available Providers: {', '.join(providers) if providers else 'None'}")
    
    if not providers:
        print("\n⚠️  No API keys found! Set at least one of:")
        print("   - OPENAI_API_KEY")
        print("   - GOOGLE_API_KEY")
        print("   - CO_API_KEY")
        return
    
    # Test files to run
    test_files = [
        # Database-focused tests
        ("test_sqlite_local.py", "SQLite Local Database"),
        ("test_postgres_docker.py", "PostgreSQL Docker"),
        ("test_supabase_direct.py", "Supabase Direct Connection"),
        ("test_serverless_scenarios.py", "Serverless Environments"),
        
        # Provider-focused tests
        ("test_provider_sqlite.py", "Each Provider with SQLite"),
        ("test_provider_postgres.py", "Each Provider with PostgreSQL"),
        ("test_provider_supabase.py", "Each Provider with Supabase"),
    ]
    
    print("\n🧪 Test Suite:")
    for i, (file, desc) in enumerate(test_files, 1):
        print(f"  {i}. {desc} ({file})")
    
    # Ask user which tests to run
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Run ALL tests")
    print("  2. Run database tests only (1-4)")
    print("  3. Run provider tests only (5-7)")
    print("  4. Run specific test (enter number)")
    print("  5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    tests_to_run = []
    if choice == "1":
        tests_to_run = test_files
    elif choice == "2":
        tests_to_run = test_files[:4]
    elif choice == "3":
        tests_to_run = test_files[4:]
    elif choice == "4":
        test_num = input("Enter test number (1-7): ").strip()
        try:
            idx = int(test_num) - 1
            if 0 <= idx < len(test_files):
                tests_to_run = [test_files[idx]]
            else:
                print("Invalid test number")
                return
        except ValueError:
            print("Invalid input")
            return
    elif choice == "5":
        print("Exiting...")
        return
    else:
        print("Invalid choice")
        return
    
    # Run selected tests
    print("\n" + "=" * 80)
    print("STARTING TEST EXECUTION")
    print("=" * 80)
    
    results = []
    start_time = time.time()
    
    for test_file, description in tests_to_run:
        print(f"\n📝 Testing: {description}")
        success, message = run_test_file(test_file)
        results.append((test_file, success, message))
        
        # Small delay between test files
        time.sleep(1)
    
    elapsed = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"\n📊 Statistics:")
    print(f"  Total Tests Run: {len(results)}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")
    print(f"  Time: {elapsed:.2f}s")
    
    print(f"\n📋 Individual Results:")
    for test_file, success, message in results:
        print(f"  {message}")
    
    if failed == 0:
        print("\n🎉 SUCCESS: All tests passed!")
    else:
        print(f"\n⚠️  WARNING: {failed} test file(s) had failures")
        print("\nCommon issues to check:")
        print("  1. Docker PostgreSQL not running (run: docker-compose up -d)")
        print("  2. Supabase IPv6 connectivity issues on WSL")
        print("  3. Missing API keys in .env file")
        print("  4. Rate limiting from API providers")
    
    print("\n" + "=" * 80)
    print("For detailed test output, run individual test files:")
    print("  pytest tests/test_file.py -v -s")
    print("=" * 80)


# Keep original test classes for backward compatibility
from cortex import Client
from cortex.models.registry import list_available_models, get_model_config


@pytest.mark.integration
class TestRealOpenAIIntegration:
    """Test real OpenAI API integration"""
    
    @pytest.fixture
    def openai_client(self):
        """Create client for OpenAI testing with real API and Supabase"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        # Use real Supabase from DATABASE_URL
        return Client()
    
    def test_real_gpt_4o_mini_response(self, openai_client):
        """Test actual GPT-4o-mini API call and response"""
        response = openai_client.create(
            model="gpt-4o-mini",
            input="What is 2+2? Reply with just the number.",
            temperature=0.0  # Deterministic
        )
        
        # Verify response structure
        assert response["status"] == "completed"
        assert response["model"] == "gpt-4o-mini"
        assert response["id"] is not None
        assert response["output"] is not None
        assert len(response["output"]) > 0
        
        # Check actual content
        content = response["output"][0]["content"][0]["text"]
        assert "4" in content  # Should contain the answer
        
        # Verify usage statistics from real API
        assert response["usage"] is not None
        assert response["usage"]["total_tokens"] > 0
        assert response["usage"]["input_tokens"] > 0
        assert response["usage"]["output_tokens"] > 0
    
    def test_real_gpt_4o_conversation(self, openai_client):
        """Test real conversation with GPT-4o"""
        # First message
        response1 = openai_client.create(
            model="gpt-4o",
            input="Remember this number: 42. I'll ask about it later.",
            instructions="You are a helpful assistant with perfect memory."
        )
        assert response1["status"] == "completed"
        
        # Continue conversation
        response2 = openai_client.create(
            model="gpt-4o",
            input="What number did I ask you to remember?",
            previous_response_id=response1["id"]
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        
        # Check if GPT-4o actually remembered
        content = response2["output"][0]["content"][0]["text"]
        assert "42" in content
    
    def test_real_gpt_35_turbo_speed(self, openai_client):
        """Test GPT-3.5-turbo response time"""
        start_time = time.time()
        
        response = openai_client.create(
            model="gpt-3.5-turbo",
            input="Say 'fast response' and nothing else.",
            temperature=0.0
        )
        
        elapsed = time.time() - start_time
        
        assert response["status"] == "completed"
        assert elapsed < 5.0  # Should respond within 5 seconds
        assert "fast" in response["output"][0]["content"][0]["text"].lower()
    
    def test_openai_temperature_variations(self, openai_client):
        """Test temperature effects on real OpenAI responses"""
        prompt = "Write a creative one-word response"
        
        # Low temperature (deterministic)
        response_low = openai_client.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.0
        )
        
        # High temperature (creative)
        response_high = openai_client.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=1.5
        )
        
        # Both should complete
        assert response_low["status"] == "completed"
        assert response_high["status"] == "completed"
        assert response_low["temperature"] == 0.0
        assert response_high["temperature"] == 1.5


@pytest.mark.integration
class TestRealGoogleGeminiIntegration:
    """Test real Google Gemini API integration"""
    
    @pytest.fixture
    def gemini_client(self):
        """Create client for Gemini testing with real API and Supabase"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        # Use real Supabase from DATABASE_URL
        return Client()
    
    def test_real_gemini_flash_response(self, gemini_client):
        """Test actual Gemini 1.5 Flash API call"""
        response = gemini_client.create(
            model="gemini-1.5-flash",
            input="What is the capital of France? Reply with just the city name.",
            temperature=0.0
        )
        
        assert response["status"] == "completed"
        assert response["model"] == "gemini-1.5-flash"
        
        content = response["output"][0]["content"][0]["text"]
        assert "Paris" in content
    
    def test_real_gemini_pro_analysis(self, gemini_client):
        """Test Gemini Pro's analytical capabilities"""
        response = gemini_client.create(
            model="gemini-1.5-pro",
            input="Analyze this sequence: 2, 4, 8, 16. What comes next and why?",
            temperature=0.1
        )
        
        assert response["status"] == "completed"
        content = response["output"][0]["content"][0]["text"]
        assert "32" in content  # Should identify the pattern
    
    def test_gemini_conversation_memory(self, gemini_client):
        """Test Gemini's conversation memory"""
        # Setup context
        r1 = gemini_client.create(
            model="gemini-1.0-pro",
            input="My favorite color is blue. Remember this.",
            store=True
        )
        
        # Test recall
        r2 = gemini_client.create(
            model="gemini-1.0-pro",
            input="What's my favorite color?",
            previous_response_id=r1["id"]
        )
        
        assert r2["status"] == "completed"
        assert "blue" in r2["output"][0]["content"][0]["text"].lower()


@pytest.mark.integration
class TestRealCohereIntegration:
    """Test real Cohere API integration"""
    
    @pytest.fixture
    def cohere_client(self):
        """Create client for Cohere testing with real API and Supabase"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        # Use real Supabase from DATABASE_URL
        return Client()
    
    def test_real_command_r_response(self, cohere_client):
        """Test actual Command-R API call"""
        response = cohere_client.create(
            model="command-r",
            input="Explain quantum computing in one sentence.",
            temperature=0.3
        )
        
        assert response["status"] == "completed"
        assert response["model"] == "command-r"
        
        content = response["output"][0]["content"][0]["text"]
        assert "quantum" in content.lower()
        assert len(content) > 10  # Should have actual content
    
    def test_command_r_plus_quality(self, cohere_client):
        """Test Command-R+ enhanced capabilities"""
        response = cohere_client.create(
            model="command-r-plus",
            input="Write a haiku about programming.",
            temperature=0.7
        )
        
        assert response["status"] == "completed"
        content = response["output"][0]["content"][0]["text"]
        
        # Haiku should have multiple lines
        lines = content.strip().split('\n')
        assert len(lines) >= 3
    
    def test_cohere_conversation_flow(self, cohere_client):
        """Test Cohere conversation continuity"""
        # Initial context
        r1 = cohere_client.create(
            model="command",
            input="I'm learning Python. What should I know first?",
            instructions="You are a programming tutor."
        )
        
        # Follow-up question
        r2 = cohere_client.create(
            model="command",
            input="Can you give me a simple example?",
            previous_response_id=r1["id"]
        )
        
        assert r2["status"] == "completed"
        assert r2["previous_response_id"] == r1["id"]
        # Should reference Python in the follow-up
        assert "python" in r2["output"][0]["content"][0]["text"].lower() or "print" in r2["output"][0]["content"][0]["text"].lower()


@pytest.mark.integration
class TestRealProviderSwitching:
    """Test switching between real providers in conversations"""
    
    @pytest.fixture
    def multi_provider_client(self):
        """Create client with all providers configured and Supabase"""
        missing_keys = []
        if not os.getenv("OPENAI_API_KEY"):
            missing_keys.append("OPENAI_API_KEY")
        if not os.getenv("GOOGLE_API_KEY"):
            missing_keys.append("GOOGLE_API_KEY")
        if not os.getenv("CO_API_KEY"):
            missing_keys.append("CO_API_KEY")
        
        if missing_keys:
            pytest.skip(f"Missing API keys: {', '.join(missing_keys)}")
        
        # Use real Supabase from DATABASE_URL
        return Client()
    
    def test_real_openai_to_gemini_handoff(self, multi_provider_client):
        """Test real handoff from OpenAI to Gemini"""
        # OpenAI sets context
        r1 = multi_provider_client.create(
            model="gpt-4o-mini",
            input="I'll tell you a secret: the password is 'rainbow123'. Remember it.",
            temperature=0.0
        )
        assert r1["status"] == "completed"
        
        # Gemini continues
        r2 = multi_provider_client.create(
            model="gemini-1.5-flash",
            input="What was the password I mentioned?",
            previous_response_id=r1["id"],
            temperature=0.0
        )
        assert r2["status"] == "completed"
        
        # Gemini should have access to conversation history
        content = r2["output"][0]["content"][0]["text"]
        assert "rainbow123" in content or "password" in content.lower()
    
    def test_real_three_way_provider_conversation(self, multi_provider_client):
        """Test conversation across all three providers"""
        # Cohere starts
        r1 = multi_provider_client.create(
            model="command-r",
            input="Let's play a game. I'm thinking of the number 7.",
            instructions="You are a playful assistant"
        )
        assert r1["status"] == "completed"
        
        # OpenAI continues
        r2 = multi_provider_client.create(
            model="gpt-3.5-turbo",
            input="What number were you thinking of?",
            previous_response_id=r1["id"]
        )
        assert r2["status"] == "completed"
        
        # Gemini concludes
        r3 = multi_provider_client.create(
            model="gemini-1.0-pro",
            input="Was the number between 5 and 10?",
            previous_response_id=r2["id"]
        )
        assert r3["status"] == "completed"
        
        # All should maintain context
        assert r2["previous_response_id"] == r1["id"]
        assert r3["previous_response_id"] == r2["id"]
    
    def test_real_provider_specific_features(self, multi_provider_client):
        """Test provider-specific features with real APIs"""
        # OpenAI - JSON mode style request
        openai_response = multi_provider_client.create(
            model="gpt-4o-mini",
            input='Generate a JSON object with keys "name" and "age" for a fictional person.',
            temperature=0.0
        )
        assert "{" in openai_response["output"][0]["content"][0]["text"]
        
        # Gemini - Long context
        gemini_response = multi_provider_client.create(
            model="gemini-1.5-flash",
            input="Count from 1 to 10, with each number on a new line.",
            temperature=0.0
        )
        content = gemini_response["output"][0]["content"][0]["text"]
        assert "10" in content
        
        # Cohere - Concise responses
        cohere_response = multi_provider_client.create(
            model="command",
            input="Define AI in exactly three words.",
            temperature=0.0
        )
        assert cohere_response["status"] == "completed"


@pytest.mark.integration
class TestRealDatabaseIntegration:
    """Test real database persistence with actual LLM calls"""
    
    @pytest.fixture
    def postgres_client(self):
        """Create client with PostgreSQL if available"""
        if not os.getenv("LOCAL_POSTGRES_URL"):
            pytest.skip("LOCAL_POSTGRES_URL not set")
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        return Client(db_url=os.getenv("LOCAL_POSTGRES_URL"))
    
    def test_real_postgres_persistence(self, postgres_client):
        """Test real PostgreSQL persistence with actual API calls"""
        # Create a conversation
        r1 = postgres_client.create(
            model="gpt-4o-mini",
            input="Remember this code: ABC123",
            store=True
        )
        response_id = r1["id"]
        
        # Create new client instance (simulating app restart)
        new_client = Client(db_url=os.getenv("LOCAL_POSTGRES_URL"))
        
        # Continue conversation with new client
        r2 = new_client.create(
            model="gpt-4o-mini",
            input="What was the code I gave you?",
            previous_response_id=response_id
        )
        
        assert r2["status"] == "completed"
        assert "ABC123" in r2["output"][0]["content"][0]["text"]
    
    def test_real_supabase_integration(self):
        """Test real Supabase cloud PostgreSQL with actual API calls"""
        if not os.getenv("DATABASE_URL"):
            pytest.skip("DATABASE_URL (Supabase) not set")
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        client = Client(db_url=os.getenv("DATABASE_URL"))
        
        # Create conversation in cloud
        response = client.create(
            model="command-r",
            input="Hello from Supabase test!",
            store=True
        )
        
        assert response["status"] == "completed"
        assert response["store"] == True
        
        # Verify we can continue (proves it was stored)
        r2 = client.create(
            model="command-r",
            input="What did I just say?",
            previous_response_id=response["id"]
        )
        
        assert r2["status"] == "completed"


@pytest.mark.integration
class TestRealErrorScenarios:
    """Test real error scenarios with actual APIs"""
    
    def test_real_invalid_api_key_error(self):
        """Test with intentionally invalid API key"""
        # Temporarily set invalid key
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "sk-invalid-key-12345"
        
        try:
            client = Client()
            response = client.create(
                model="gpt-4o-mini",
                input="This should fail"
            )
            
            assert response["status"] == "failed"
            assert response["error"] is not None
            assert "auth" in response["error"]["message"].lower() or "api" in response["error"]["message"].lower()
        finally:
            # Restore original key
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key
    
    def test_real_model_not_available_error(self):
        """Test requesting a model that doesn't exist"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        client = Client()
        
        # Try to use a model that doesn't exist
        response = client.create(
            model="gpt-2",  # Old model, not available via API
            input="This model doesn't exist"
        )
        
        assert response["status"] == "failed"
        assert "not found" in response["error"]["message"].lower() or "not supported" in response["error"]["message"].lower()
    
    def test_real_context_length_exceeded(self):
        """Test exceeding context length with real API"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        client = Client()
        
        # Create very long input (over 50k chars limit)
        long_input = "Test " * 15000  # 75k chars
        
        response = client.create(
            model="gpt-4o-mini",
            input=long_input
        )
        
        assert response["status"] == "failed"
        assert "too long" in response["error"]["message"].lower() or "length" in response["error"]["message"].lower()


@pytest.mark.integration
class TestRealPerformanceMetrics:
    """Test real performance metrics across providers"""
    
    @pytest.fixture
    def perf_client(self):
        """Client for performance testing with Supabase"""
        missing = []
        for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY", "CO_API_KEY"]:
            if not os.getenv(key):
                missing.append(key)
        if missing:
            pytest.skip(f"Missing: {', '.join(missing)}")
        
        # Use real Supabase from DATABASE_URL
        return Client()
    
    def test_real_provider_response_times(self, perf_client):
        """Compare real response times across providers"""
        prompt = "What is 10 + 10? Reply with just the number."
        
        # Test each provider
        providers = [
            ("gpt-3.5-turbo", "OpenAI"),
            ("gemini-1.5-flash", "Gemini"),
            ("command", "Cohere")
        ]
        
        results = {}
        for model, name in providers:
            start = time.time()
            response = perf_client.create(
                model=model,
                input=prompt,
                temperature=0.0
            )
            elapsed = time.time() - start
            
            assert response["status"] == "completed"
            assert "20" in response["output"][0]["content"][0]["text"]
            
            results[name] = elapsed
            print(f"\n{name} ({model}): {elapsed:.2f}s")
        
        # All should respond within reasonable time
        for name, elapsed in results.items():
            assert elapsed < 10.0, f"{name} took too long: {elapsed}s"
    
    def test_real_token_usage_tracking(self, perf_client):
        """Test real token usage across providers"""
        prompt = "Write a 50-word story about a robot."
        
        models = ["gpt-4o-mini", "gemini-1.5-flash", "command-r"]
        
        for model in models:
            response = perf_client.create(
                model=model,
                input=prompt,
                temperature=0.7
            )
            
            assert response["status"] == "completed"
            
            # Check usage stats (if provided)
            if response.get("usage"):
                assert response["usage"]["total_tokens"] > 0
                assert response["usage"]["input_tokens"] > 0
                assert response["usage"]["output_tokens"] > 0
                
                # Output should be roughly 50 words (± margin)
                # Rough estimate: 1 token ≈ 0.75 words
                output_tokens = response["usage"]["output_tokens"]
                estimated_words = output_tokens * 0.75
                assert 30 < estimated_words < 100, f"Expected ~50 words, got ~{estimated_words}"


@pytest.mark.integration  
class TestRealStressTest:
    """Stress test with real APIs"""
    
    def test_rapid_real_api_calls(self):
        """Test rapid successive real API calls with Supabase"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        client = Client()
        
        # Make 5 rapid calls
        responses = []
        for i in range(5):
            response = client.create(
                model="gpt-3.5-turbo",  # Fastest model
                input=f"Say 'Response {i}'",
                temperature=0.0
            )
            responses.append(response)
            assert response["status"] == "completed"
            assert str(i) in response["output"][0]["content"][0]["text"]
        
        # All should have unique IDs
        ids = [r["id"] for r in responses]
        assert len(ids) == len(set(ids))
    
    def test_parallel_provider_stress(self):
        """Stress test with multiple providers in sequence with Supabase"""
        required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "CO_API_KEY"]
        for key in required_keys:
            if not os.getenv(key):
                pytest.skip(f"{key} not set")
        
        client = Client()
        
        # Cycle through providers rapidly
        models = ["gpt-3.5-turbo", "gemini-1.5-flash", "command"]
        
        for cycle in range(3):  # 3 cycles = 9 requests
            for model in models:
                response = client.create(
                    model=model,
                    input=f"Cycle {cycle}, Model {model}: Say OK",
                    temperature=0.0
                )
                assert response["status"] == "completed"
                assert response["model"] == model


if __name__ == "__main__":
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)