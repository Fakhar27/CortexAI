"""
Comprehensive tests for db_url parameter functionality
Tests the ability to pass database URLs per request for multi-tenant support
"""

import os
import pytest
import tempfile
import uuid
from unittest.mock import patch, MagicMock
from cortex import Client
from cortex.responses.persistence import DatabaseError


class TestDbUrlParameter:
    """Test suite for db_url parameter in create() method"""
    
    @pytest.fixture
    def client(self):
        """Create a test client with default SQLite"""
        return Client()
    
    @pytest.fixture
    def postgres_url(self):
        """Get PostgreSQL URL from environment or skip test"""
        url = os.getenv("DATABASE_URL")
        if not url:
            pytest.skip("PostgreSQL tests require DATABASE_URL environment variable")
        return url
    
    @pytest.fixture
    def mock_cohere_response(self):
        """Mock Cohere API response"""
        mock_response = MagicMock()
        mock_response.content = "This is a test response from the AI"
        return mock_response
    
    def test_default_sqlite_without_db_url(self, client, mock_cohere_response):
        """Test that default SQLite works when no db_url is provided"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Create response without db_url
            response = client.create(
                input="Test message",
                model="cohere",
                store=True
            )
            
            assert response is not None
            assert response['id'] is not None
            assert response['status'] == 'completed'
            assert response['output'][0]['content'][0]['text'] == "This is a test response from the AI"
            
            # Verify we can continue the conversation
            response2 = client.create(
                input="Follow up message",
                model="cohere",
                previous_response_id=response['id'],
                store=True
            )
            
            assert response2 is not None
            assert response2['previous_response_id'] == response['id']
    
    def test_db_url_override_per_request(self, client, postgres_url, mock_cohere_response):
        """Test that db_url parameter overrides instance database per request"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # First request to PostgreSQL
            response1 = client.create(
                input="Message for PostgreSQL",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            
            assert response1 is not None
            assert response1['id'] is not None
            
            # Second request to default SQLite (no db_url)
            response2 = client.create(
                input="Message for SQLite",
                model="cohere",
                store=True
            )
            
            assert response2 is not None
            assert response2['id'] != response1['id']
            
            # Third request back to PostgreSQL
            response3 = client.create(
                input="Another PostgreSQL message",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            
            assert response3 is not None
            assert response3['id'] not in [response1['id'], response2['id']]
    
    def test_conversation_continuation_with_matching_db_url(self, client, postgres_url, mock_cohere_response):
        """Test that conversations can be continued when using the same db_url"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Start conversation in PostgreSQL
            response1 = client.create(
                input="Start conversation",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            
            # Continue with same db_url
            response2 = client.create(
                input="Continue conversation",
                model="cohere",
                db_url=postgres_url,
                previous_response_id=response1['id'],
                store=True
            )
            
            assert response2 is not None
            assert response2['previous_response_id'] == response1['id']
    
    def test_conversation_fails_with_mismatched_db_url(self, client, postgres_url, mock_cohere_response):
        """Test that conversation continuation fails when db_url doesn't match"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Start conversation in PostgreSQL
            response1 = client.create(
                input="Start in PostgreSQL",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            
            # Try to continue in SQLite (no db_url) - should fail
            response2 = client.create(
                input="Try to continue in SQLite",
                model="cohere",
                previous_response_id=response1['id'],
                store=True
            )
            
            # Should return an error response
            assert response2 is not None
            assert response2['status'] == 'failed'
            assert response2['error'] is not None
            assert 'not found' in response2['error']['message'].lower()
    
    def test_empty_db_url_uses_default(self, client, mock_cohere_response):
        """Test that empty string db_url gracefully falls back to default"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            response = client.create(
                input="Test with empty db_url",
                model="cohere",
                db_url="",  # Empty string should use default
                store=True
            )
            
            assert response is not None
            assert response['status'] == 'completed'  # Should succeed with default
            assert response['error'] is None
    
    def test_invalid_db_url_format(self, client):
        """Test that invalid database URLs are rejected"""
        invalid_urls = [
            "not-a-url",
            "http://example.com",  # HTTP not allowed
            "mysql://user:pass@localhost/db",  # MySQL not supported
            "mongodb://localhost:27017",  # MongoDB not supported
            "sqlite:///path/to/db",  # SQLite URL format not supported
            "invalid://format",
        ]
        
        for invalid_url in invalid_urls:
            response = client.create(
                input=f"Test with {invalid_url}",
                model="cohere",
                db_url=invalid_url,
                store=True
            )
            
            assert response is not None
            assert response['status'] == 'failed'
            assert response['error'] is not None
            assert response['error']['param'] == 'db_url'
    
    def test_valid_postgresql_url_formats(self, client, mock_cohere_response):
        """Test that various valid PostgreSQL URL formats are accepted"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Mock the database connection to avoid actual connection attempts
            with patch('cortex.responses.persistence.PostgresCheckpointerWrapper') as mock_wrapper:
                mock_checkpointer = MagicMock()
                mock_checkpointer.response_exists.return_value = False
                mock_checkpointer.get_thread_for_response.return_value = None
                mock_wrapper.return_value = mock_checkpointer
                
                valid_urls = [
                    "postgresql://user:pass@localhost:5432/dbname",
                    "postgres://user:pass@localhost:5432/dbname",  # Both schemas work
                    "postgresql://user:pass@example.com/mydb",
                    "postgresql://user:pass@db.supabase.co:5432/postgres",
                ]
                
                for valid_url in valid_urls:
                    response = client.create(
                        input=f"Test with {valid_url[:20]}...",
                        model="cohere",
                        db_url=valid_url,
                        store=True
                    )
                    
                    # Should attempt connection (might fail but URL format is valid)
                    # Real connection errors would be different from validation errors
                    assert response is not None
    
    def test_serverless_scenario_multiple_clients(self, postgres_url, mock_cohere_response):
        """Test serverless scenario where each request creates a new client"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Simulate Request 1: New client, new conversation
            client1 = Client()
            response1 = client1.create(
                input="First serverless request",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            assert response1 is not None
            response1_id = response1['id']
            
            # Simulate Request 2: New client, continue conversation
            client2 = Client()  # New client instance
            response2 = client2.create(
                input="Continue serverless conversation",
                model="cohere",
                db_url=postgres_url,  # Same database
                previous_response_id=response1_id,
                store=True
            )
            assert response2 is not None
            assert response2['previous_response_id'] == response1_id
            
            # Simulate Request 3: New client, new conversation
            client3 = Client()
            response3 = client3.create(
                input="Different conversation",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            assert response3 is not None
            assert response3['id'] != response1_id
            assert response3['id'] != response2['id']
    
    def test_db_url_with_store_false(self, client, postgres_url, mock_cohere_response):
        """Test that db_url works correctly with store=False"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Create response with store=False
            response1 = client.create(
                input="Don't store this",
                model="cohere",
                db_url=postgres_url,
                store=False  # Don't persist
            )
            
            assert response1 is not None
            assert response1['store'] is False
            
            # Try to continue - should fail since it wasn't stored
            response2 = client.create(
                input="Try to continue",
                model="cohere",
                db_url=postgres_url,
                previous_response_id=response1['id'],
                store=True
            )
            
            assert response2 is not None
            assert response2['status'] == 'failed'
            assert 'not found' in response2['error']['message'].lower()
    
    def test_temporary_graph_creation(self, client, mock_cohere_response):
        """Test that temporary graphs are created for different db_urls"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            with patch('cortex.responses.methods.create.get_checkpointer') as mock_get_checkpointer:
                with patch('cortex.responses.methods.create.StateGraph') as mock_state_graph:
                    mock_checkpointer = MagicMock()
                    mock_get_checkpointer.return_value = mock_checkpointer
                    
                    mock_workflow = MagicMock()
                    mock_state_graph.return_value = mock_workflow
                    mock_workflow.compile.return_value = MagicMock()
                    
                    # Use a different db_url than instance default
                    test_url = "postgresql://test:test@localhost/testdb"
                    response = client.create(
                        input="Test temporary graph",
                        model="cohere",
                        db_url=test_url,
                        store=True
                    )
                    
                    # Verify temporary checkpointer was created
                    mock_get_checkpointer.assert_called_once_with(db_url=test_url)
                    
                    # Verify temporary graph was created
                    mock_state_graph.assert_called_once()
                    mock_workflow.compile.assert_called_once_with(checkpointer=mock_checkpointer)
    
    def test_db_url_none_uses_instance_default(self, client, mock_cohere_response):
        """Test that db_url=None uses the instance's default database"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Explicitly pass None for db_url
            response = client.create(
                input="Test with None db_url",
                model="cohere",
                db_url=None,  # Should use instance default
                store=True
            )
            
            assert response is not None
            assert response['status'] == 'completed'
    
    def test_connection_error_handling(self, client):
        """Test proper error handling for database connection failures"""
        # Test with a valid format but unreachable database
        unreachable_url = "postgresql://user:pass@nonexistent.host.invalid:5432/db"
        
        response = client.create(
            input="Test connection error",
            model="cohere",
            db_url=unreachable_url,
            store=True
        )
        
        assert response is not None
        assert response['status'] == 'failed'
        assert response['error'] is not None
        # Error message should indicate connection/database issue
        error_msg = response['error']['message'].lower()
        assert any(word in error_msg for word in ['connect', 'database', 'host'])


class TestDbUrlParameterIntegration:
    """Integration tests for db_url parameter with real databases"""
    
    @pytest.fixture
    def temp_sqlite_path(self):
        """Create a temporary SQLite database path"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        yield path
        # Cleanup
        try:
            os.unlink(path)
        except:
            pass
    
    @pytest.mark.integration
    def test_multiple_simultaneous_databases(self, mock_cohere_response):
        """Test that multiple databases can be used simultaneously"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            # Create multiple clients with different default databases
            client1 = Client()  # Default SQLite
            client2 = Client()  # Another instance with default
            
            # Create responses in different databases
            response1 = client1.create(
                input="Client 1 message",
                model="cohere",
                store=True
            )
            
            response2 = client2.create(
                input="Client 2 message",
                model="cohere",
                store=True
            )
            
            # Both should succeed independently
            assert response1 is not None
            assert response2 is not None
            assert response1['id'] != response2['id']
    
    @pytest.mark.integration
    def test_conversation_isolation_between_databases(self, postgres_url, mock_cohere_response):
        """Test that conversations are isolated between different databases"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm
            
            client = Client()
            
            # Create conversation in SQLite
            sqlite_response = client.create(
                input="SQLite conversation",
                model="cohere",
                store=True
            )
            
            # Create conversation in PostgreSQL
            postgres_response = client.create(
                input="PostgreSQL conversation",
                model="cohere",
                db_url=postgres_url,
                store=True
            )
            
            # Try to continue SQLite conversation in PostgreSQL (should fail)
            cross_response = client.create(
                input="Cross-database attempt",
                model="cohere",
                db_url=postgres_url,
                previous_response_id=sqlite_response['id'],
                store=True
            )
            
            assert cross_response['status'] == 'failed'
            assert 'not found' in cross_response['error']['message'].lower()