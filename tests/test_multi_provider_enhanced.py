"""
Enhanced multi-provider tests with database support
Tests SQLite, PostgreSQL (local & Supabase), and provider switching
"""

import pytest
import warnings
import os
import tempfile
from unittest.mock import patch, MagicMock
from cortex import Client
from cortex.models.registry import get_model_config, list_available_models
from cortex.responses.llm import get_llm, validate_api_key, handle_llm_error
from cortex.responses.persistence import get_checkpointer, DatabaseError


class TestDatabaseIntegration:
    """Test multi-provider with different database backends"""
    
    @pytest.fixture
    def supabase_url(self):
        """Get Supabase URL from environment"""
        # Use the URL you provided or from env
        return os.getenv("DATABASE_URL", 
                        "postgresql://postgres:Fakhar_27_1$@db.tqovtjyylrykgpehbfdl.supabase.co:5432/postgres")
    
    @pytest.fixture
    def local_postgres_url(self):
        """Get local PostgreSQL URL from docker-compose"""
        return os.getenv("LOCAL_POSTGRES_URL", 
                        "postgresql://postgres:postgres@localhost:5432/cortex")
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for database tests"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Test response from mock LLM")
        return mock_llm
    
    def test_sqlite_with_multiple_providers(self, temp_db_path, mock_llm_response):
        """Test SQLite persistence with provider switching"""
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm_response):
            client = Client(db_path=temp_db_path)
            
            # Create responses with different providers
            r1 = client.create(model="gpt-4o-mini", input="Test with OpenAI")
            assert r1["status"] == "completed"
            assert r1["model"] == "gpt-4o-mini"
            
            # Continue conversation with different provider
            r2 = client.create(
                model="gemini-1.5-flash",
                input="Switch to Gemini",
                previous_response_id=r1["id"]
            )
            assert r2["status"] == "completed"
            assert r2["model"] == "gemini-1.5-flash"
            assert r2["previous_response_id"] == r1["id"]
    
    @pytest.mark.skipif(
        not os.getenv("LOCAL_POSTGRES_URL"),
        reason="Local PostgreSQL not available"
    )
    def test_local_postgres_with_providers(self, local_postgres_url, mock_llm_response):
        """Test local PostgreSQL with multiple providers"""
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm_response):
            try:
                client = Client(db_url=local_postgres_url)
                
                # Test with each provider
                providers_models = [
                    ("gpt-4o", "OpenAI GPT-4"),
                    ("gemini-1.5-pro", "Google Gemini"),
                    ("command-r", "Cohere Command")
                ]
                
                for model, input_text in providers_models:
                    response = client.create(
                        model=model,
                        input=f"Testing {input_text} with PostgreSQL"
                    )
                    assert response["status"] == "completed"
                    assert response["model"] == model
                    
            except DatabaseError as e:
                pytest.skip(f"PostgreSQL connection failed: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("DATABASE_URL"),
        reason="Supabase URL not configured"
    )
    def test_supabase_with_providers(self, supabase_url, mock_llm_response):
        """Test Supabase PostgreSQL with multiple providers"""
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm_response):
            try:
                client = Client(db_url=supabase_url)
                
                # Start conversation with OpenAI
                r1 = client.create(
                    model="gpt-3.5-turbo",
                    input="Testing Supabase with OpenAI"
                )
                assert r1["status"] == "completed"
                
                # Continue with Google
                r2 = client.create(
                    model="gemini-1.0-pro",
                    input="Continue with Gemini",
                    previous_response_id=r1["id"]
                )
                assert r2["status"] == "completed"
                assert r2["previous_response_id"] == r1["id"]
                
            except DatabaseError as e:
                pytest.skip(f"Supabase connection failed: {e}")
    
    def test_db_url_per_request(self, mock_llm_response):
        """Test passing db_url per request (serverless pattern)"""
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm_response):
            # Create client with SQLite
            client = Client()
            
            # First request uses SQLite (default)
            r1 = client.create(
                model="command-r",
                input="Using default SQLite"
            )
            assert r1["status"] == "completed"
            
            # Second request with custom db_url (if available)
            postgres_url = os.getenv("LOCAL_POSTGRES_URL")
            if postgres_url:
                try:
                    r2 = client.create(
                        model="gpt-4o-mini",
                        input="Using custom PostgreSQL",
                        db_url=postgres_url
                    )
                    assert r2["status"] == "completed"
                except DatabaseError:
                    pass  # PostgreSQL might not be running
    
    def test_parallel_databases_different_providers(self, temp_db_path, mock_llm_response):
        """Test multiple databases with different providers simultaneously"""
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm_response):
            # SQLite client
            sqlite_client = Client(db_path=temp_db_path)
            
            # Create conversations with different providers
            sqlite_openai = sqlite_client.create(
                model="gpt-4o",
                input="SQLite with OpenAI"
            )
            
            sqlite_google = sqlite_client.create(
                model="gemini-1.5-flash",
                input="SQLite with Google"
            )
            
            # Verify different response IDs
            assert sqlite_openai["id"] != sqlite_google["id"]
            assert sqlite_openai["model"] == "gpt-4o"
            assert sqlite_google["model"] == "gemini-1.5-flash"
            
            # If PostgreSQL available, test parallel
            postgres_url = os.getenv("LOCAL_POSTGRES_URL")
            if postgres_url:
                try:
                    pg_client = Client(db_url=postgres_url)
                    pg_response = pg_client.create(
                        model="command-r-plus",
                        input="PostgreSQL with Cohere"
                    )
                    assert pg_response["model"] == "command-r-plus"
                except DatabaseError:
                    pass


class TestProviderSwitchingWithPersistence:
    """Test provider switching with real persistence"""
    
    @pytest.fixture
    def persistent_client(self, temp_db_path):
        """Client with SQLite persistence and mocked LLMs"""
        mock_llm = MagicMock()
        
        # Track messages to verify persistence
        self.message_history = []
        
        def track_messages(messages):
            self.message_history.append(len(messages))
            return MagicMock(content=f"Response with {len(messages)} messages")
        
        mock_llm.invoke = track_messages
        
        with patch('cortex.responses.llm.get_llm', return_value=mock_llm):
            yield Client(db_path=temp_db_path)
    
    def test_conversation_persistence_across_providers(self, persistent_client):
        """Test that conversation history persists when switching providers"""
        client = persistent_client
        
        # First message with OpenAI
        r1 = client.create(
            model="gpt-4o-mini",
            input="Start with OpenAI",
            store=True  # Explicitly store
        )
        
        # Continue with Google (should have history)
        r2 = client.create(
            model="gemini-1.5-flash",
            input="Continue with Google",
            previous_response_id=r1["id"],
            store=True
        )
        
        # Continue with Cohere (should have full history)
        r3 = client.create(
            model="command-r",
            input="End with Cohere",
            previous_response_id=r2["id"],
            store=True
        )
        
        # Verify conversation history grew
        assert self.message_history[0] < self.message_history[1]
        assert self.message_history[1] < self.message_history[2]
        
        # All should be successful
        assert all(r["status"] == "completed" for r in [r1, r2, r3])
    
    def test_store_false_with_provider_switching(self, persistent_client):
        """Test store=False doesn't persist but allows continuation"""
        client = persistent_client
        
        # Create with store=False
        r1 = client.create(
            model="gpt-3.5-turbo",
            input="Don't store this",
            store=False
        )
        assert r1["status"] == "completed"
        
        # Try to continue - should fail
        r2 = client.create(
            model="gemini-1.0-pro",
            input="Try to continue",
            previous_response_id=r1["id"]
        )
        
        # Should fail because r1 wasn't stored
        assert r2["status"] == "failed"
        assert "not found" in r2["error"]["message"].lower()


class TestMultiAgentScenarios:
    """Test multi-agent selection and conversation scenarios"""
    
    @pytest.fixture
    def multi_agent_client(self, temp_db_path):
        """Client setup for multi-agent testing"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            # Different responses for different models
            def model_specific_response(model_name, *args, **kwargs):
                mock = MagicMock()
                if "gpt" in model_name:
                    mock.invoke.return_value = MagicMock(content="OpenAI Agent Response")
                elif "gemini" in model_name:
                    mock.invoke.return_value = MagicMock(content="Google Agent Response")
                else:
                    mock.invoke.return_value = MagicMock(content="Cohere Agent Response")
                return mock
            
            mock_get_llm.side_effect = model_specific_response
            yield Client(db_path=temp_db_path)
    
    def test_multi_agent_conversation_flow(self, multi_agent_client):
        """Test a complex multi-agent conversation flow"""
        client = multi_agent_client
        
        # Agent 1: OpenAI for analysis
        analysis = client.create(
            model="gpt-4o",
            input="Analyze this problem",
            instructions="You are an analytical agent"
        )
        assert "OpenAI" in str(analysis["output"][0]["content"][0]["text"])
        
        # Agent 2: Google for creative solution
        creative = client.create(
            model="gemini-1.5-pro",
            input="Provide creative solution",
            previous_response_id=analysis["id"],
            instructions="You are a creative agent"  # New instructions override
        )
        assert "Google" in str(creative["output"][0]["content"][0]["text"])
        
        # Agent 3: Cohere for summary
        summary = client.create(
            model="command-r-plus",
            input="Summarize the discussion",
            previous_response_id=creative["id"],
            instructions="You are a summarization agent"
        )
        assert "Cohere" in str(summary["output"][0]["content"][0]["text"])
        
        # Verify chain
        assert creative["previous_response_id"] == analysis["id"]
        assert summary["previous_response_id"] == creative["id"]
    
    def test_parallel_multi_agent_tasks(self, multi_agent_client):
        """Test parallel multi-agent tasks with different providers"""
        client = multi_agent_client
        
        # Run three parallel tasks with different agents
        tasks = [
            ("gpt-4o-mini", "Task 1: Quick analysis", "Analyst"),
            ("gemini-1.5-flash", "Task 2: Fast generation", "Generator"),
            ("command", "Task 3: Basic summary", "Summarizer")
        ]
        
        responses = []
        for model, input_text, role in tasks:
            response = client.create(
                model=model,
                input=input_text,
                instructions=f"You are a {role}",
                temperature=0.5
            )
            responses.append(response)
        
        # All should complete successfully
        assert all(r["status"] == "completed" for r in responses)
        
        # Each should use correct model
        for i, (model, _, _) in enumerate(tasks):
            assert responses[i]["model"] == model
            assert responses[i]["temperature"] == 0.5


class TestStressTestingWithDatabases:
    """Stress test provider switching with database persistence"""
    
    def test_rapid_provider_db_switching(self, temp_db_path):
        """Test rapid provider and database switching"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Stress test response")
            mock_get_llm.return_value = mock_llm
            
            client = Client(db_path=temp_db_path)
            
            # Rapid model switching pattern
            switch_pattern = [
                ("gpt-4o", True),
                ("gemini-1.5-flash", False),
                ("command-r", True),
                ("gpt-3.5-turbo", False),
                ("gemini-1.0-pro", True),
                ("command-r-plus", True),
                ("gpt-4o-mini", False),
                ("gemini-1.5-pro", True),
                ("command", False)
            ]
            
            responses = []
            for model, store in switch_pattern * 2:  # 18 requests
                response = client.create(
                    model=model,
                    input=f"Stress test {model}",
                    store=store
                )
                responses.append(response)
                assert response["status"] == "completed"
                assert response["model"] == model
                assert response["store"] == store
            
            # Verify unique IDs
            ids = [r["id"] for r in responses]
            assert len(ids) == len(set(ids))
    
    def test_database_failover_scenario(self):
        """Test failover from PostgreSQL to SQLite"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Failover test")
            mock_get_llm.return_value = mock_llm
            
            # Try PostgreSQL first
            postgres_url = "postgresql://invalid:invalid@nonexistent:5432/test"
            
            # This should fail gracefully
            try:
                client = Client(db_url=postgres_url)
                pytest.fail("Should have raised DatabaseError")
            except DatabaseError:
                pass  # Expected
            
            # Fallback to SQLite
            with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
                client = Client(db_path=tmp.name)
                response = client.create(
                    model="gpt-4o-mini",
                    input="Fallback test"
                )
                assert response["status"] == "completed"


class TestEdgeCasesWithDatabases:
    """Test edge cases with database and provider combinations"""
    
    def test_empty_db_url_handling(self):
        """Test that empty db_url is handled gracefully"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Test")
            mock_get_llm.return_value = mock_llm
            
            # Empty string should use default SQLite
            client = Client(db_url="")
            response = client.create(
                model="gpt-4o",
                input="Test with empty db_url"
            )
            assert response["status"] == "completed"
    
    def test_mixed_persistence_modes(self, temp_db_path):
        """Test mixing store=True and store=False in conversation"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Mixed mode test")
            mock_get_llm.return_value = mock_llm
            
            client = Client(db_path=temp_db_path)
            
            # First: store=True with OpenAI
            r1 = client.create(
                model="gpt-4o",
                input="Store this",
                store=True
            )
            
            # Second: store=False with Google (continues from r1)
            r2 = client.create(
                model="gemini-1.5-flash",
                input="Don't store this",
                previous_response_id=r1["id"],
                store=False
            )
            assert r2["status"] == "completed"
            
            # Third: Try to continue from r2 (should fail)
            r3 = client.create(
                model="command-r",
                input="Try to continue",
                previous_response_id=r2["id"]
            )
            assert r3["status"] == "failed"
            
            # Fourth: Continue from r1 (should work)
            r4 = client.create(
                model="gpt-3.5-turbo",
                input="Continue from r1",
                previous_response_id=r1["id"],
                store=True
            )
            assert r4["status"] == "completed"
    
    def test_provider_specific_errors_with_db(self, temp_db_path):
        """Test provider-specific errors are handled correctly with persistence"""
        client = Client(db_path=temp_db_path)
        
        # Test with invalid API key scenario
        with patch('cortex.responses.llm.validate_api_key') as mock_validate:
            mock_validate.side_effect = ValueError("Missing API key for openai")
            
            response = client.create(
                model="gpt-4o-mini",
                input="Test without API key"
            )
            
            assert response["status"] == "failed"
            assert "API key" in response["error"]["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])