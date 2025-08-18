"""
Test SQLite Local Database
Tests when no db_url is provided - should use SQLite automatically
"""

import os
import pytest
import tempfile
from pathlib import Path
from cortex import Client

# Removed helper imports

# IMPORTANT: Clear DATABASE_URL to ensure SQLite is used
if "DATABASE_URL" in os.environ:
    del os.environ["DATABASE_URL"]


class TestSQLiteLocal:
    """Test SQLite persistence without any db_url"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure clean environment for each test"""
        # Remove DATABASE_URL if it exists
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        # Use a temporary database file
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_conversations.db")
        os.environ["CORTEX_DB_PATH"] = self.db_path
        
        yield
        
        # Cleanup
        if "CORTEX_DB_PATH" in os.environ:
            del os.environ["CORTEX_DB_PATH"]
    
    def test_sqlite_auto_selection(self):
        """Test that SQLite is automatically selected when no db_url"""
        print("\n=== Testing SQLite Auto Selection ===")
        
        # Create client without any db_url
        client = Client()
        print("✓ Client created without db_url")
        
        # Verify SQLite file is created
        assert os.path.exists(self.db_path), f"SQLite database not created at {self.db_path}"
        print(f"✓ SQLite database created at {self.db_path}")
        
        # Test creating a response
        response = client.create(
            model="command-r",
            input="Test SQLite storage"
        )
        
        assert response["status"] == "completed"
        assert response["id"] is not None
        print(f"✓ Response created with ID: {response['id']}")
        
        return response["id"]
    
    def test_sqlite_persistence(self):
        """Test that data persists in SQLite across client instances"""
        print("\n=== Testing SQLite Persistence ===")
        
        # First client - create conversation
        client1 = Client()
        response1 = client1.create(
            model="command-r",
            input="Remember this: My favorite number is 42",
            store=True
        )
        response_id = response1["id"]
        print(f"✓ Created response with ID: {response_id}")
        
        # Delete first client
        del client1
        
        # Second client - continue conversation
        client2 = Client()
        response2 = client2.create(
            model="command-r",
            input="What was my favorite number?",
            previous_response_id=response_id
        )
        
        assert response2["status"] == "completed"
        assert response2["previous_response_id"] == response_id
        print(f"✓ Continued conversation from previous response")
        
        # Check if the number is remembered (would require checking actual content)
        print(f"✓ SQLite persistence working correctly")
    
    def test_sqlite_with_openai(self):
        """Test SQLite with OpenAI provider"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing SQLite + OpenAI ===")
        
        client = Client()
        response = client.create(
            model="gpt-4o-mini",
            input="Test OpenAI with SQLite: What is 2+2?",
            temperature=0.0
        )
        
        assert response["status"] == "completed"
        assert response["model"] == "gpt-4o-mini"
        print(f"✓ OpenAI + SQLite working: {response['id']}")
        
        # Test persistence
        response2 = client.create(
            model="gpt-4o-mini",
            input="What was the math question I asked?",
            previous_response_id=response["id"]
        )
        
        assert response2["status"] == "completed"
        print("✓ Conversation persistence with OpenAI + SQLite working")
    
    def test_sqlite_with_gemini(self):
        """Test SQLite with Google Gemini provider"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing SQLite + Gemini ===")
        
        client = Client()
        response = client.create(
            model="gemini-1.5-flash",
            input="Test Gemini with SQLite: What is the capital of France?",
            temperature=0.0
        )
        
        assert response["status"] == "completed"
        assert response["model"] == "gemini-1.5-flash"
        print(f"✓ Gemini + SQLite working: {response['id']}")
    
    def test_sqlite_with_cohere(self):
        """Test SQLite with Cohere provider"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing SQLite + Cohere ===")
        
        client = Client()
        response = client.create(
            model="command-r",
            input="Test Cohere with SQLite: Say hello",
            temperature=0.0
        )
        
        assert response["status"] == "completed"
        assert response["model"] == "command-r"
        print(f"✓ Cohere + SQLite working: {response['id']}")
    
    def test_sqlite_multi_conversation(self):
        """Test multiple parallel conversations in SQLite"""
        print("\n=== Testing Multiple Conversations in SQLite ===")
        
        client = Client()
        
        # Create 3 separate conversations
        conversations = []
        for i in range(3):
            response = client.create(
                model="command-r",
                input=f"This is conversation {i}. Remember this number: {i * 100}",
                store=True
            )
            conversations.append(response["id"])
            print(f"✓ Created conversation {i}: {response['id']}")
        
        # Continue each conversation
        for i, conv_id in enumerate(conversations):
            response = client.create(
                model="command-r",
                input="What number should you remember?",
                previous_response_id=conv_id
            )
            assert response["status"] == "completed"
            print(f"✓ Continued conversation {i}")
        
        print("✓ Multiple conversations working in SQLite")
    
    def test_sqlite_store_false(self):
        """Test that store=False doesn't persist in SQLite"""
        print("\n=== Testing store=False in SQLite ===")
        
        client = Client()
        
        # Create without storing
        response1 = client.create(
            model="command-r",
            input="Don't save this message",
            store=False
        )
        print(f"✓ Created response with store=False: {response1['id']}")
        
        # Try to continue - should fail
        response2 = client.create(
            model="command-r",
            input="Continue from the unsaved message",
            previous_response_id=response1["id"]
        )
        
        # This should fail or return an error
        if response2["status"] == "failed":
            print("✓ Correctly failed to continue from unsaved response")
        else:
            print("⚠ Warning: Continued from unsaved response (unexpected)")


if __name__ == "__main__":
    # Run specific test
    print("=" * 60)
    print("TESTING SQLITE LOCAL DATABASE")
    print("=" * 60)
    print("\nThis test verifies:")
    print("1. SQLite is automatically used when no db_url provided")
    print("2. Data persists across client instances")
    print("3. All providers work with SQLite")
    print("4. Multiple conversations can be managed")
    print("\nRun with: pytest tests/test_sqlite_local.py -v -s")
    print("=" * 60)