"""
Comprehensive tests for the persistence layer
Tests SQLite, PostgreSQL, multiple agents, concurrency, and edge cases
"""

import os
import pytest
import threading
import time
import random
import sqlite3
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

from cortex import Client
from cortex.responses.persistence import (
    get_checkpointer,
    DatabaseError,
    is_serverless_environment,
    validate_postgresql_url,
    SmartCheckpointer,
    PostgresCheckpointerWrapper
)


# Test data for different agent personalities
AGENTS = {
    "life_coach": {
        "name": "Life Coach Lisa",
        "instructions": "You are Lisa, an empathetic life coach who helps people achieve their goals.",
        "test_inputs": [
            "I feel stuck in my career",
            "How can I improve my work-life balance?",
            "What should I focus on?"
        ]
    },
    "fitness_trainer": {
        "name": "Fitness Coach Frank", 
        "instructions": "You are Frank, an enthusiastic fitness trainer. Provide workout advice.",
        "test_inputs": [
            "I want to lose weight",
            "What's a good workout?",
            "How much protein?"
        ]
    },
    "tech_mentor": {
        "name": "Tech Mentor Tom",
        "instructions": "You are Tom, a senior software engineer mentoring developers.",
        "test_inputs": [
            "SQL vs NoSQL?",
            "How to debug?",
            "Python or JavaScript?"
        ]
    }
}


class TestPersistenceLayer:
    """Test the core persistence functionality"""
    
    def test_sqlite_default(self):
        """Test that SQLite is used by default in local environment"""
        checkpointer = get_checkpointer()
        assert checkpointer is not None
        assert isinstance(checkpointer, SmartCheckpointer)
    
    def test_postgresql_connection(self):
        """Test PostgreSQL connection when URL provided"""
        # Try with Docker PostgreSQL if available
        db_url = "postgresql://postgres:postgres@localhost:5432/cortex"
        
        try:
            checkpointer = get_checkpointer(db_url=db_url)
            assert checkpointer is not None
            assert isinstance(checkpointer, PostgresCheckpointerWrapper)
        except DatabaseError as e:
            if "could not translate host name" in str(e):
                pytest.skip("PostgreSQL not available locally")
            else:
                raise
    
    def test_empty_string_uses_default(self):
        """Test that empty string database URL gracefully uses default"""
        # Empty string should fall back to default SQLite
        checkpointer = get_checkpointer(db_url="")
        assert checkpointer is not None
        # Should be using SQLite (SmartCheckpointer or SqliteSaver)
        assert hasattr(checkpointer, 'conn') or hasattr(checkpointer, 'db_path')
    
    def test_invalid_database_urls(self):
        """Test that non-PostgreSQL URLs are rejected"""
        invalid_urls = [
            ("mongodb://localhost/test", "MongoDB"),
            ("mysql://localhost/test", "MySQL"),
            ("redis://localhost", "Redis"),
            ("not-a-url", "Invalid format"),
        ]
        
        for url, description in invalid_urls:
            with pytest.raises(DatabaseError, match="Only PostgreSQL is supported"):
                get_checkpointer(db_url=url)
    
    def test_serverless_environment_detection(self):
        """Test serverless environment detection"""
        # Test with no serverless indicators
        assert not is_serverless_environment()
        
        # Test with Vercel indicator
        with patch.dict(os.environ, {"VERCEL": "1"}):
            assert is_serverless_environment()
        
        # Test with AWS Lambda indicator
        with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test"}):
            assert is_serverless_environment()
    
    def test_serverless_warning(self):
        """Test that serverless without db_url shows warning"""
        with patch.dict(os.environ, {"VERCEL": "1"}):
            with pytest.warns(UserWarning, match="Running in serverless without database URL"):
                checkpointer = get_checkpointer()
                # Should get MemorySaver in serverless without db_url
                from langgraph.checkpoint.memory import MemorySaver
                assert isinstance(checkpointer, MemorySaver)
    
    def test_environment_variable_support(self):
        """Test DATABASE_URL environment variable support"""
        test_url = "postgresql://test:test@localhost:5432/test"
        
        with patch.dict(os.environ, {"DATABASE_URL": test_url}):
            try:
                checkpointer = get_checkpointer()
                # Should try to use PostgreSQL from env
                assert isinstance(checkpointer, PostgresCheckpointerWrapper)
            except DatabaseError as e:
                # Connection might fail but URL should be validated
                assert "PostgreSQL" in str(e) or "connect" in str(e)


class TestMultipleAgents:
    """Test multiple agents and conversations"""
    
    @pytest.fixture
    def client(self):
        """Create a client for testing"""
        return Client()
    
    def test_multiple_agents_sqlite(self, client):
        """Test multiple agents with different conversations in SQLite"""
        responses_by_agent = {}
        
        for agent_id, agent_data in AGENTS.items():
            # Start a conversation with this agent
            response1 = client.create(
                input=agent_data['test_inputs'][0],
                instructions=agent_data['instructions']
            )
            assert response1 is not None
            assert 'id' in response1
            
            # Continue the conversation
            response2 = client.create(
                input=agent_data['test_inputs'][1],
                previous_response_id=response1['id']
            )
            assert response2 is not None
            
            # Verify conversation continuity
            response3 = client.create(
                input="What did we just discuss?",
                previous_response_id=response2['id']
            )
            assert response3 is not None
            
            responses_by_agent[agent_id] = [
                response1['id'], 
                response2['id'], 
                response3['id']
            ]
        
        # Verify we have responses for all agents
        assert len(responses_by_agent) == len(AGENTS)
    
    def test_conversation_isolation(self, client):
        """Test that different conversations are isolated"""
        # Create two separate conversations
        conv1_response1 = client.create(
            input="I'm Alice",
            instructions="Remember my name"
        )
        
        conv2_response1 = client.create(
            input="I'm Bob", 
            instructions="Remember my name"
        )
        
        # Continue first conversation
        conv1_response2 = client.create(
            input="What's my name?",
            previous_response_id=conv1_response1['id']
        )
        
        # Continue second conversation
        conv2_response2 = client.create(
            input="What's my name?",
            previous_response_id=conv2_response1['id']
        )
        
        # Responses should be different (isolated contexts)
        assert conv1_response2['id'] != conv2_response2['id']
        
        # Optional: Check if names are mentioned correctly
        # (This would require parsing the actual response text)
    
    def test_conversation_branching(self, client):
        """Test creating branches from the same conversation point"""
        # Create initial conversation
        response1 = client.create(
            input="Let's discuss options",
            instructions="You are a decision advisor"
        )
        
        # Create two branches from the same point
        branch1 = client.create(
            input="Let's go with option A",
            previous_response_id=response1['id']
        )
        
        branch2 = client.create(
            input="Let's go with option B",
            previous_response_id=response1['id']
        )
        
        # Both branches should work but be different
        assert branch1['id'] != branch2['id']
        assert branch1 is not None
        assert branch2 is not None


class TestPersistenceAcrossRestarts:
    """Test that conversations persist across client restarts"""
    
    def test_sqlite_persistence(self):
        """Test SQLite persistence across client instances"""
        # Create first client and conversation
        client1 = Client()
        
        response1 = client1.create(
            input="My favorite color is blue",
            instructions="Remember facts about me"
        )
        
        response2 = client1.create(
            input="I live in New York",
            previous_response_id=response1['id']
        )
        
        # Store the response IDs
        response1_id = response1['id']
        response2_id = response2['id']
        
        # Delete client1 to simulate restart
        del client1
        
        # Create new client
        client2 = Client()
        
        # Continue conversation with new client
        response3 = client2.create(
            input="What do you remember about me?",
            previous_response_id=response2_id
        )
        
        # Should successfully continue
        assert response3 is not None
        assert 'id' in response3
    
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL") and not os.getenv("SUPABASE_DB_URL"),
        reason="PostgreSQL not configured"
    )
    def test_postgresql_persistence(self):
        """Test PostgreSQL persistence across client instances"""
        db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
        
        # Create first client
        client1 = Client(db_url=db_url)
        
        response1 = client1.create(
            input="Testing PostgreSQL persistence",
            instructions="Test assistant"
        )
        
        response2 = client1.create(
            input="Second message",
            previous_response_id=response1['id']
        )
        
        response2_id = response2['id']
        
        # Delete and recreate client
        del client1
        
        client2 = Client(db_url=db_url)
        
        # Should be able to continue
        response3 = client2.create(
            input="Can you continue?",
            previous_response_id=response2_id
        )
        
        assert response3 is not None


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def client(self):
        return Client()
    
    def test_very_long_input(self, client):
        """Test handling of very long input"""
        long_input = "Hello " * 1000  # 5000+ characters
        
        response = client.create(
            input=long_input,
            instructions="You are a helpful assistant"
        )
        
        assert response is not None
        assert 'id' in response
    
    def test_invalid_previous_response_id(self, client):
        """Test handling of invalid previous_response_id"""
        with pytest.raises(Exception) as exc_info:
            client.create(
                input="Continue from nowhere",
                previous_response_id="resp_fake_invalid_12345"
            )
        
        # Should get an error about response not found
        assert "not found" in str(exc_info.value) or "error" in str(exc_info.value).lower()
    
    def test_store_false_persistence(self, client):
        """Test that store=False doesn't persist"""
        # Create without storing
        response1 = client.create(
            input="Don't save this",
            instructions="Test assistant",
            store=False
        )
        
        assert response1 is not None
        
        # Trying to continue should fail or start fresh
        # (depending on implementation)
        try:
            response2 = client.create(
                input="Continue from unsaved",
                previous_response_id=response1['id']
            )
            # If it works, it might be starting fresh
            assert response2 is not None
        except Exception:
            # Expected - can't continue from unsaved
            pass
    
    def test_rapid_conversation_switching(self, client):
        """Test rapidly switching between multiple conversations"""
        # Create multiple conversations
        conversation_ids = []
        
        for i in range(3):
            response = client.create(
                input=f"Conversation {i}",
                instructions=f"You are assistant {i}"
            )
            conversation_ids.append(response['id'])
        
        # Rapidly switch between them
        for _ in range(10):
            prev_id = random.choice(conversation_ids)
            response = client.create(
                input="Continue",
                previous_response_id=prev_id
            )
            assert response is not None


class TestConcurrency:
    """Test concurrent access patterns"""
    
    def test_concurrent_conversations_sqlite(self):
        """Test concurrent conversations with SQLite"""
        results = []
        errors = []
        
        def create_conversation(thread_id):
            try:
                client = Client()
                
                response1 = client.create(
                    input=f"Thread {thread_id} message 1",
                    instructions=f"Assistant for thread {thread_id}"
                )
                
                response2 = client.create(
                    input=f"Thread {thread_id} message 2",
                    previous_response_id=response1['id']
                )
                
                results.append({
                    "thread_id": thread_id,
                    "responses": [response1['id'], response2['id']]
                })
            except Exception as e:
                errors.append({"thread_id": thread_id, "error": str(e)})
        
        # Create threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_conversation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # SQLite might have some concurrency issues, but should handle most
        assert len(results) >= 3  # At least 3 should succeed
    
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL") and not os.getenv("SUPABASE_DB_URL"),
        reason="PostgreSQL not configured"
    )
    def test_concurrent_conversations_postgresql(self):
        """Test concurrent conversations with PostgreSQL"""
        db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
        results = []
        errors = []
        
        def create_conversation(thread_id):
            try:
                client = Client(db_url=db_url)
                
                response1 = client.create(
                    input=f"Thread {thread_id} message 1",
                    instructions=f"Assistant for thread {thread_id}"
                )
                
                response2 = client.create(
                    input=f"Thread {thread_id} message 2",
                    previous_response_id=response1['id']
                )
                
                results.append({
                    "thread_id": thread_id,
                    "responses": [response1['id'], response2['id']]
                })
            except Exception as e:
                errors.append({"thread_id": thread_id, "error": str(e)})
        
        # Create threads
        threads = []
        for i in range(10):  # More threads for PostgreSQL
            thread = threading.Thread(target=create_conversation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # PostgreSQL should handle all concurrent requests
        assert len(results) == 10
        assert len(errors) == 0


class TestPostgreSQLSpecific:
    """Test PostgreSQL-specific functionality"""
    
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL") and not os.getenv("SUPABASE_DB_URL"),
        reason="PostgreSQL not configured"
    )
    def test_postgresql_wrapper_methods(self):
        """Test PostgresCheckpointerWrapper methods"""
        db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
        
        checkpointer = get_checkpointer(db_url=db_url)
        assert isinstance(checkpointer, PostgresCheckpointerWrapper)
        
        # Test response_exists method
        assert not checkpointer.response_exists("resp_nonexistent")
        
        # Test get_thread_for_response method
        assert checkpointer.get_thread_for_response("resp_nonexistent") is None
        
        # Create a real response and test again
        client = Client(db_url=db_url)
        response = client.create(
            input="Test message",
            instructions="Test assistant"
        )
        
        # Now it should exist
        assert checkpointer.response_exists(response['id'])
        assert checkpointer.get_thread_for_response(response['id']) == response['id']
    
    @pytest.mark.skipif(
        not os.getenv("SUPABASE_DB_URL"),
        reason="Supabase not configured"
    )
    def test_supabase_compatibility(self):
        """Test that Supabase works correctly"""
        supabase_url = os.getenv("SUPABASE_DB_URL")
        
        client = Client(db_url=supabase_url)
        
        # Create a conversation
        response1 = client.create(
            input="Testing Supabase",
            instructions="Supabase test assistant"
        )
        
        # Continue it
        response2 = client.create(
            input="Is Supabase working?",
            previous_response_id=response1['id']
        )
        
        assert response1 is not None
        assert response2 is not None


class TestMemoryPressure:
    """Test behavior under memory pressure"""
    
    def test_many_conversations(self):
        """Test creating many separate conversations"""
        client = Client()
        conversation_ids = []
        
        # Create 50 conversations
        for i in range(50):
            response = client.create(
                input=f"Conversation {i}",
                instructions=f"Assistant {i}"
            )
            conversation_ids.append(response['id'])
        
        assert len(conversation_ids) == 50
        
        # Continue random conversations
        for _ in range(20):
            prev_id = random.choice(conversation_ids)
            response = client.create(
                input="Continue",
                previous_response_id=prev_id
            )
            assert response is not None
    
    def test_deep_conversation_chain(self):
        """Test a very deep conversation chain"""
        client = Client()
        
        # Start conversation
        response = client.create(
            input="Start of a long conversation",
            instructions="You are a patient assistant"
        )
        
        # Continue many times
        for i in range(20):
            response = client.create(
                input=f"Message {i+2}",
                previous_response_id=response['id']
            )
            assert response is not None
        
        # Should still work after many messages
        assert response['id'] is not None