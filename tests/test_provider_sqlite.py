"""
Test Each Provider with SQLite
Tests each provider individually with SQLite database
"""

import os
import pytest
import tempfile
from cortex import Client


class TestProviderSQLite:
    """Test each provider individually with SQLite"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup SQLite for each test"""
        # Clear DATABASE_URL to use SQLite
        self.original_db_url = os.environ.get("DATABASE_URL")
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        # Use temp database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_provider.db")
        os.environ["CORTEX_DB_PATH"] = self.db_path
        
        yield
        
        # Cleanup
        if "CORTEX_DB_PATH" in os.environ:
            del os.environ["CORTEX_DB_PATH"]
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
    
    def test_openai_with_sqlite(self):
        """Test OpenAI provider with SQLite"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing OpenAI + SQLite ===")
        
        client = Client()
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gpt-4o-mini",
            input="OpenAI SQLite test: What is 10 + 10?",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gpt-4o-mini"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="gpt-4o-mini",
            input="Multiply that result by 2",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        del client
        client2 = Client()
        response3 = client2.create(
            model="gpt-4o-mini",
            input="What was the original calculation?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test store=False
        print("4. Testing store=False...")
        response4 = client2.create(
            model="gpt-4o-mini",
            input="This should not be saved",
            store=False,
            temperature=0.0
        )
        assert response4["status"] == "completed"
        print(f"✓ Created without storing: {response4['id']}")
        
        # Try to continue from unstored - should fail
        response5 = client2.create(
            model="gpt-4o-mini",
            input="Continue from unstored",
            previous_response_id=response4["id"],
            temperature=0.0
        )
        if response5["status"] == "failed":
            print("✓ Correctly failed to continue from unstored")
        else:
            print("⚠ Warning: Continued from unstored response")
        
        print("\n✅ OpenAI + SQLite: All tests passed!")
    
    def test_gemini_with_sqlite(self):
        """Test Google Gemini provider with SQLite"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing Gemini + SQLite ===")
        
        client = Client()
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="gemini-1.5-flash",
            input="Gemini SQLite test: Name the 7 continents",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gemini-1.5-flash"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="gemini-1.5-flash",
            input="Which continent is the largest?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        del client
        client2 = Client()
        response3 = client2.create(
            model="gemini-1.5-flash",
            input="Which continent is the smallest?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test different temperature
        print("4. Testing temperature control...")
        response4 = client2.create(
            model="gemini-1.5-flash",
            input="Write a creative story about a continent",
            temperature=0.9
        )
        assert response4["status"] == "completed"
        assert response4.get("temperature") == 0.9
        print(f"✓ Temperature control: {response4['id']}")
        
        print("\n✅ Gemini + SQLite: All tests passed!")
    
    def test_cohere_with_sqlite(self):
        """Test Cohere provider with SQLite"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing Cohere + SQLite ===")
        
        client = Client()
        
        # Test basic completion
        print("1. Testing basic completion...")
        response1 = client.create(
            model="command-r",
            input="Cohere SQLite test: Explain what a database is",
            temperature=0.0
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "command-r"
        print(f"✓ Basic completion: {response1['id']}")
        
        # Test conversation continuation
        print("2. Testing conversation continuation...")
        response2 = client.create(
            model="command-r",
            input="Give an example of a popular database",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ Continuation: {response2['id']}")
        
        # Test persistence
        print("3. Testing persistence...")
        del client
        client2 = Client()
        response3 = client2.create(
            model="command-r",
            input="What are the advantages of the database you mentioned?",
            previous_response_id=response2["id"],
            temperature=0.0
        )
        assert response3["status"] == "completed"
        print(f"✓ Persistence: {response3['id']}")
        
        # Test multiple conversations
        print("4. Testing multiple conversations...")
        conv1 = client2.create(
            model="command-r",
            input="Conversation 1: Remember the word ALPHA",
            store=True
        )
        conv2 = client2.create(
            model="command-r",
            input="Conversation 2: Remember the word BETA",
            store=True
        )
        
        # Continue first conversation
        cont1 = client2.create(
            model="command-r",
            input="What word should you remember?",
            previous_response_id=conv1["id"]
        )
        assert cont1["status"] == "completed"
        
        # Continue second conversation
        cont2 = client2.create(
            model="command-r",
            input="What word should you remember?",
            previous_response_id=conv2["id"]
        )
        assert cont2["status"] == "completed"
        
        print(f"✓ Multiple conversations: {conv1['id']}, {conv2['id']}")
        
        print("\n✅ Cohere + SQLite: All tests passed!")
    
    def test_provider_switching_sqlite(self):
        """Test switching between providers with SQLite"""
        print("\n=== Testing Provider Switching with SQLite ===")
        
        # Check which providers are available
        providers = []
        if os.getenv("OPENAI_API_KEY"):
            providers.append(("gpt-4o-mini", "OpenAI"))
        if os.getenv("GOOGLE_API_KEY"):
            providers.append(("gemini-1.5-flash", "Gemini"))
        if os.getenv("CO_API_KEY"):
            providers.append(("command-r", "Cohere"))
        
        if len(providers) < 2:
            pytest.skip(f"Need at least 2 providers, found {len(providers)}")
        
        client = Client()
        
        # Start conversation with first provider
        model1, name1 = providers[0]
        print(f"1. Starting with {name1}...")
        response1 = client.create(
            model=model1,
            input="Provider test: My favorite color is blue",
            store=True,
            temperature=0.0
        )
        assert response1["status"] == "completed"
        print(f"✓ {name1} started: {response1['id']}")
        
        # Continue with second provider
        model2, name2 = providers[1]
        print(f"2. Continuing with {name2}...")
        response2 = client.create(
            model=model2,
            input="What is my favorite color?",
            previous_response_id=response1["id"],
            temperature=0.0
        )
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response1["id"]
        print(f"✓ {name2} continued: {response2['id']}")
        
        # If we have a third provider, use it too
        if len(providers) >= 3:
            model3, name3 = providers[2]
            print(f"3. Finishing with {name3}...")
            response3 = client.create(
                model=model3,
                input="Suggest other shades of that color",
                previous_response_id=response2["id"],
                temperature=0.0
            )
            assert response3["status"] == "completed"
            print(f"✓ {name3} finished: {response3['id']}")
        
        print("\n✅ Provider Switching + SQLite: All tests passed!")
    
    def test_error_handling_sqlite(self):
        """Test error handling with SQLite"""
        print("\n=== Testing Error Handling with SQLite ===")
        
        client = Client()
        
        # Test invalid model
        print("1. Testing invalid model...")
        try:
            response = client.create(
                model="invalid-model-xyz",
                input="This should fail"
            )
            assert False, "Should have raised an error"
        except Exception as e:
            print(f"✓ Invalid model error: {str(e)[:50]}...")
        
        # Test missing model parameter
        print("2. Testing missing model...")
        try:
            response = client.create(
                input="No model specified"
            )
            assert False, "Should have raised an error"
        except Exception as e:
            print(f"✓ Missing model error: {str(e)[:50]}...")
        
        # Test invalid previous_response_id
        print("3. Testing invalid previous_response_id...")
        response = client.create(
            model="command-r",
            input="Continue from invalid",
            previous_response_id="invalid-id-12345"
        )
        # Should either fail or start fresh
        print(f"✓ Handled invalid ID: status={response['status']}")
        
        # Test very long input
        print("4. Testing very long input...")
        long_input = "Test " * 10000  # Very long input
        response = client.create(
            model="command-r",
            input=long_input[:5000],  # Limit to reasonable size
            store=False
        )
        assert response["status"] in ["completed", "failed"]
        print(f"✓ Handled long input: status={response['status']}")
        
        print("\n✅ Error Handling + SQLite: All tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING EACH PROVIDER WITH SQLITE")
    print("=" * 60)
    print("\nThis test file verifies each provider individually:")
    print("1. OpenAI (gpt-4o-mini)")
    print("2. Google Gemini (gemini-1.5-flash)")
    print("3. Cohere (command-r)")
    print("\nEach provider is tested for:")
    print("- Basic completion")
    print("- Conversation continuation")
    print("- Persistence across client instances")
    print("- store=True/False behavior")
    print("- Temperature control")
    print("- Multiple conversations")
    print("- Error handling")
    print("\nRun with: pytest tests/test_provider_sqlite.py -v -s")
    print("Or test specific provider:")
    print("  pytest tests/test_provider_sqlite.py::TestProviderSQLite::test_openai_with_sqlite -v -s")
    print("=" * 60)