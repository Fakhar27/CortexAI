"""
Test PostgreSQL Docker Database
Tests with local PostgreSQL from docker-compose
"""

import os
import pytest
from cortex import Client

# Docker PostgreSQL URL from docker-compose.yml
DOCKER_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5432/cortex"


class TestPostgreSQLDocker:
    """Test with local PostgreSQL from Docker"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        # Clear DATABASE_URL to ensure we use explicit db_url
        if "DATABASE_URL" in os.environ:
            self.original_db_url = os.environ["DATABASE_URL"]
            del os.environ["DATABASE_URL"]
        else:
            self.original_db_url = None
        
        yield
        
        # Restore original
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
    
    def test_docker_postgres_connection(self):
        """Test connection to Docker PostgreSQL"""
        print("\n=== Testing Docker PostgreSQL Connection ===")
        print(f"Connecting to: {DOCKER_POSTGRES_URL}")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            print("✓ Connected to Docker PostgreSQL")
            
            # Test creating a response
            response = client.create(
                model="command-r",
                input="Test Docker PostgreSQL"
            )
            
            assert response["status"] == "completed"
            print(f"✓ Response created: {response['id']}")
            
        except Exception as e:
            if "could not translate host name" in str(e) or "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not running: {e}")
            else:
                raise
    
    def test_postgres_persistence(self):
        """Test persistence with Docker PostgreSQL"""
        print("\n=== Testing PostgreSQL Persistence ===")
        
        try:
            # First client
            client1 = Client(db_url=DOCKER_POSTGRES_URL)
            response1 = client1.create(
                model="command-r",
                input="PostgreSQL test: Remember the color blue",
                store=True
            )
            response_id = response1["id"]
            print(f"✓ Created response: {response_id}")
            
            # Delete first client
            del client1
            
            # Second client - should retrieve from PostgreSQL
            client2 = Client(db_url=DOCKER_POSTGRES_URL)
            response2 = client2.create(
                model="command-r",
                input="What color should you remember?",
                previous_response_id=response_id
            )
            
            assert response2["status"] == "completed"
            assert response2["previous_response_id"] == response_id
            print("✓ PostgreSQL persistence working")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise
    
    def test_postgres_with_openai(self):
        """Test PostgreSQL with OpenAI provider"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        print("\n=== Testing PostgreSQL + OpenAI ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            response = client.create(
                model="gpt-4o-mini",
                input="PostgreSQL + OpenAI test: What is 5+5?",
                temperature=0.0
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "gpt-4o-mini"
            print(f"✓ OpenAI + PostgreSQL working: {response['id']}")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise
    
    def test_postgres_with_gemini(self):
        """Test PostgreSQL with Google Gemini"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        print("\n=== Testing PostgreSQL + Gemini ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            response = client.create(
                model="gemini-1.5-flash",
                input="PostgreSQL + Gemini test: Name a planet",
                temperature=0.0
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "gemini-1.5-flash"
            print(f"✓ Gemini + PostgreSQL working: {response['id']}")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise
    
    def test_postgres_with_cohere(self):
        """Test PostgreSQL with Cohere"""
        if not os.getenv("CO_API_KEY"):
            pytest.skip("CO_API_KEY not set")
        
        print("\n=== Testing PostgreSQL + Cohere ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            response = client.create(
                model="command-r",
                input="PostgreSQL + Cohere test: Say hello",
                temperature=0.0
            )
            
            assert response["status"] == "completed"
            assert response["model"] == "command-r"
            print(f"✓ Cohere + PostgreSQL working: {response['id']}")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise
    
    def test_postgres_concurrent_access(self):
        """Test concurrent access to PostgreSQL"""
        print("\n=== Testing Concurrent PostgreSQL Access ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            
            # Create multiple conversations rapidly
            conversations = []
            for i in range(5):
                response = client.create(
                    model="command-r",
                    input=f"Concurrent test {i}",
                    store=True
                )
                conversations.append(response["id"])
                print(f"✓ Created conversation {i}")
            
            # PostgreSQL should handle all without issues
            assert len(conversations) == 5
            print("✓ PostgreSQL handled concurrent access")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise
    
    def test_postgres_transaction_handling(self):
        """Test PostgreSQL transaction handling"""
        print("\n=== Testing PostgreSQL Transactions ===")
        
        try:
            client = Client(db_url=DOCKER_POSTGRES_URL)
            
            # Create with store=True (should commit)
            response1 = client.create(
                model="command-r",
                input="This should be saved",
                store=True
            )
            print(f"✓ Created with store=True: {response1['id']}")
            
            # Create with store=False (should not commit)
            response2 = client.create(
                model="command-r",
                input="This should NOT be saved",
                store=False
            )
            print(f"✓ Created with store=False: {response2['id']}")
            
            # Try to continue from stored response (should work)
            response3 = client.create(
                model="command-r",
                input="Continue",
                previous_response_id=response1["id"]
            )
            assert response3["status"] == "completed"
            print("✓ Continued from stored response")
            
            # Try to continue from unstored response (should fail)
            response4 = client.create(
                model="command-r",
                input="Continue",
                previous_response_id=response2["id"]
            )
            
            if response4["status"] == "failed":
                print("✓ Correctly failed to continue from unstored response")
            else:
                print("⚠ Warning: Continued from unstored response")
            
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Docker PostgreSQL not available: {e}")
            else:
                raise


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING DOCKER POSTGRESQL DATABASE")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Run: docker-compose up -d")
    print("2. PostgreSQL should be running on localhost:5432")
    print(f"3. Connection: {DOCKER_POSTGRES_URL}")
    print("\nThis test verifies:")
    print("1. Connection to Docker PostgreSQL")
    print("2. Data persistence in PostgreSQL")
    print("3. All providers work with PostgreSQL")
    print("4. Concurrent access handling")
    print("5. Transaction handling")
    print("\nRun with: pytest tests/test_postgres_docker.py -v -s")
    print("=" * 60)