"""
Comprehensive tests for multi-provider LLM support
Tests OpenAI, Google Gemini, and Cohere integration with edge cases
"""

import pytest
import warnings
import os
from unittest.mock import patch, MagicMock, Mock
from cortex import Client
from cortex.models.registry import get_model_config, list_available_models, MODELS
from cortex.responses.llm import get_llm, validate_api_key, handle_llm_error


class TestModelRegistry:
    """Test model registry functionality"""
    
    def test_all_providers_registered(self):
        """Verify all three providers have models registered"""
        providers = set()
        for model_id, config in MODELS.items():
            if not config.get("_deprecated"):
                providers.add(config["provider"])
        
        assert "openai" in providers
        assert "google" in providers
        assert "cohere" in providers
        assert len(providers) >= 3
    
    def test_openai_models_configured(self):
        """Test OpenAI models are properly configured"""
        openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        for model in openai_models:
            config = get_model_config(model)
            assert config["provider"] == "openai"
            assert config["api_key_env"] == "OPENAI_API_KEY"
            assert "max_tokens" in config
            assert "temperature" in config
    
    def test_google_models_configured(self):
        """Test Google Gemini models are properly configured"""
        google_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        
        for model in google_models:
            config = get_model_config(model)
            assert config["provider"] == "google"
            assert config["api_key_env"] == "GOOGLE_API_KEY"
            assert "max_tokens" in config
    
    def test_cohere_models_configured(self):
        """Test Cohere models are properly configured"""
        cohere_models = ["command-r", "command-r-plus", "command"]
        
        for model in cohere_models:
            config = get_model_config(model)
            assert config["provider"] == "cohere"
            assert config["api_key_env"] == "CO_API_KEY"
    
    def test_deprecated_model_warning(self):
        """Test that deprecated 'cohere' alias shows warning"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = get_model_config("cohere")
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "command-r" in str(w[0].message)
    
    def test_invalid_model_raises_error(self):
        """Test that invalid model names raise appropriate errors"""
        with pytest.raises(ValueError) as exc_info:
            get_model_config("gpt-5-ultra")
        
        assert "not found" in str(exc_info.value)
        assert "Available models" in str(exc_info.value)
    
    def test_list_available_models(self):
        """Test listing available models with configuration status"""
        # Test with only OpenAI key set, clear others
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "GOOGLE_API_KEY": "", "CO_API_KEY": ""}, clear=True):
            models = list_available_models()
            
            # Should have multiple models
            assert len(models) > 5
            
            # Check structure
            for model in models:
                assert "model" in model
                assert "provider" in model
                assert "configured" in model
                assert "requires" in model
                assert "max_tokens" in model
            
            # OpenAI models should show as configured
            openai_models = [m for m in models if m["provider"] == "openai"]
            for model in openai_models:
                assert model["configured"] == True
            
            # Other providers without keys should show as not configured
            google_models = [m for m in models if m["provider"] == "google"]
            for model in google_models:
                assert model["configured"] == False
            
            # Cohere models should also show as not configured
            cohere_models = [m for m in models if m["provider"] == "cohere"]
            for model in cohere_models:
                assert model["configured"] == False


class TestAPIKeyValidation:
    """Test API key validation functionality"""
    
    def test_missing_openai_key_raises_error(self):
        """Test that missing OpenAI API key raises helpful error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_api_key("openai", "OPENAI_API_KEY")
            
            error_msg = str(exc_info.value)
            assert "Missing API key for openai" in error_msg
            assert "OPENAI_API_KEY" in error_msg
            assert "platform.openai.com" in error_msg
    
    def test_missing_google_key_raises_error(self):
        """Test that missing Google API key raises helpful error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_api_key("google", "GOOGLE_API_KEY")
            
            error_msg = str(exc_info.value)
            assert "Missing API key for google" in error_msg
            assert "GOOGLE_API_KEY" in error_msg
            assert "makersuite.google.com" in error_msg
    
    def test_valid_api_key_passes(self):
        """Test that valid API key passes validation"""
        with patch.dict(os.environ, {"TEST_API_KEY": "valid-key"}):
            # Should not raise
            validate_api_key("test", "TEST_API_KEY")


class TestErrorHandling:
    """Test provider-specific error handling"""
    
    def test_openai_rate_limit_error(self):
        """Test OpenAI rate limit error handling"""
        error = Exception("Rate limit exceeded for requests")
        result = handle_llm_error(error, "openai")
        
        assert result["error_type"] == "rate_limit"
        assert "rate limit" in result["message"].lower()
        assert result["provider"] == "openai"
    
    def test_google_auth_error(self):
        """Test Google authentication error handling"""
        error = Exception("UNAUTHENTICATED: Invalid API key")
        result = handle_llm_error(error, "google")
        
        assert result["error_type"] == "auth"
        assert "authentication" in result["message"].lower()
        assert "GOOGLE" in result["message"]
    
    def test_cohere_context_error(self):
        """Test Cohere context length error handling"""
        error = Exception("Message contains too many tokens")
        result = handle_llm_error(error, "cohere")
        
        assert result["error_type"] == "context"
        assert "context length" in result["message"].lower()
    
    def test_unknown_error_handling(self):
        """Test handling of unknown errors"""
        error = Exception("Some random error occurred")
        result = handle_llm_error(error, "openai")
        
        assert result["error_type"] == "unknown"
        assert "Some random error" in result["original_error"]


class TestMultiProviderIntegration:
    """Test multi-provider integration scenarios"""
    
    @pytest.fixture
    def mock_llms(self):
        """Mock all LLM providers"""
        with patch('cortex.responses.llm.ChatOpenAI') as mock_openai, \
             patch('cortex.responses.llm.ChatGoogleGenerativeAI') as mock_google, \
             patch('cortex.responses.llm.ChatCohere') as mock_cohere:
            
            # Set availability flags
            with patch('cortex.responses.llm.OPENAI_AVAILABLE', True), \
                 patch('cortex.responses.llm.GOOGLE_AVAILABLE', True), \
                 patch('cortex.responses.llm.COHERE_AVAILABLE', True):
                
                yield {
                    'openai': mock_openai,
                    'google': mock_google,
                    'cohere': mock_cohere
                }
    
    def test_openai_model_selection(self, mock_llms):
        """Test that OpenAI models route correctly"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            llm = get_llm("gpt-4o-mini", temperature=0.5)
            
            mock_llms['openai'].assert_called_once()
            call_kwargs = mock_llms['openai'].call_args.kwargs
            assert call_kwargs['model'] == "gpt-4o-mini"
            assert call_kwargs['temperature'] == 0.5
            assert call_kwargs['api_key'] == "test-key"
    
    def test_google_model_selection(self, mock_llms):
        """Test that Google models route correctly"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}):
            llm = get_llm("gemini-1.5-flash", temperature=0.9)
            
            mock_llms['google'].assert_called_once()
            call_kwargs = mock_llms['google'].call_args.kwargs
            assert call_kwargs['model'] == "gemini-1.5-flash"
            assert call_kwargs['temperature'] == 0.9
            assert call_kwargs['google_api_key'] == "test-google-key"
    
    def test_cohere_model_selection(self, mock_llms):
        """Test that Cohere models route correctly"""
        with patch.dict(os.environ, {"CO_API_KEY": "test-cohere-key"}):
            llm = get_llm("command-r", temperature=0.3)
            
            mock_llms['cohere'].assert_called_once()
            call_kwargs = mock_llms['cohere'].call_args.kwargs
            assert call_kwargs['model'] == "command-r"
            assert call_kwargs['temperature'] == 0.3
            assert call_kwargs['cohere_api_key'] == "test-cohere-key"


class TestProviderSwitching:
    """Test switching between providers in conversations"""
    
    @pytest.fixture
    def mock_multi_provider_client(self, temp_db_path):
        """Create a client with mocked multi-provider support"""
        client = Client(db_path=temp_db_path)
        
        # Mock different provider responses
        def mock_invoke_side_effect(*args, **kwargs):
            # Get the state from the graph execution
            if hasattr(client.graph, '_current_model'):
                model = client.graph._current_model
                if model.startswith("gpt"):
                    return MagicMock(content="OpenAI response")
                elif model.startswith("gemini"):
                    return MagicMock(content="Google response")
                else:
                    return MagicMock(content="Cohere response")
            return MagicMock(content="Default response")
        
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = mock_invoke_side_effect
            mock_get_llm.return_value = mock_llm
            yield client
    
    def test_conversation_across_providers(self, mock_multi_provider_client):
        """Test a conversation that switches between different providers"""
        client = mock_multi_provider_client
        
        # Start with OpenAI
        response1 = client.create(
            model="gpt-4o-mini",
            input="Hello from OpenAI"
        )
        assert response1["status"] == "completed"
        assert response1["model"] == "gpt-4o-mini"
        
        # Continue with Google
        response2 = client.create(
            model="gemini-1.5-flash",
            input="Now using Gemini",
            previous_response_id=response1["id"]
        )
        assert response2["status"] == "completed"
        assert response2["model"] == "gemini-1.5-flash"
        assert response2["previous_response_id"] == response1["id"]
        
        # Finish with Cohere
        response3 = client.create(
            model="command-r",
            input="Finally with Cohere",
            previous_response_id=response2["id"]
        )
        assert response3["status"] == "completed"
        assert response3["model"] == "command-r"
        assert response3["previous_response_id"] == response2["id"]
    
    def test_parallel_conversations_different_providers(self, mock_multi_provider_client):
        """Test running parallel conversations with different providers"""
        client = mock_multi_provider_client
        
        # Start three separate conversations with different providers
        openai_conv = client.create(
            model="gpt-3.5-turbo",
            input="OpenAI conversation"
        )
        
        google_conv = client.create(
            model="gemini-1.0-pro",
            input="Google conversation"
        )
        
        cohere_conv = client.create(
            model="command",
            input="Cohere conversation"
        )
        
        # Each should have different response IDs
        assert openai_conv["id"] != google_conv["id"]
        assert google_conv["id"] != cohere_conv["id"]
        assert openai_conv["id"] != cohere_conv["id"]
        
        # Each should use correct model
        assert openai_conv["model"] == "gpt-3.5-turbo"
        assert google_conv["model"] == "gemini-1.0-pro"
        assert cohere_conv["model"] == "command"


class TestStressTesting:
    """Stress tests for multi-provider system"""
    
    @pytest.fixture
    def stress_test_client(self, temp_db_path):
        """Client for stress testing"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Test response")
            mock_get_llm.return_value = mock_llm
            
            yield Client(db_path=temp_db_path)
    
    def test_rapid_provider_switching(self, stress_test_client):
        """Test rapid switching between providers"""
        client = stress_test_client
        models = [
            "gpt-4o", "gemini-1.5-flash", "command-r",
            "gpt-3.5-turbo", "gemini-1.0-pro", "command",
            "gpt-4o-mini", "gemini-1.5-pro", "command-r-plus"
        ]
        
        responses = []
        for i, model in enumerate(models * 3):  # Test 27 rapid switches
            response = client.create(
                model=model,
                input=f"Test message {i}"
            )
            responses.append(response)
            assert response["status"] == "completed"
            assert response["model"] == model
        
        # Verify all responses are unique
        response_ids = [r["id"] for r in responses]
        assert len(response_ids) == len(set(response_ids))
    
    def test_concurrent_different_models(self, stress_test_client):
        """Test using different models concurrently"""
        client = stress_test_client
        
        # Simulate concurrent requests with different models
        models_to_test = [
            ("gpt-4o", "OpenAI GPT-4"),
            ("gemini-1.5-pro", "Google Gemini Pro"),
            ("command-r-plus", "Cohere Command R+"),
            ("gpt-3.5-turbo", "OpenAI GPT-3.5"),
            ("gemini-1.0-pro", "Google Gemini 1.0"),
        ]
        
        responses = []
        for model, input_text in models_to_test:
            response = client.create(
                model=model,
                input=input_text,
                temperature=0.7
            )
            responses.append(response)
        
        # Verify each response
        for i, (model, _) in enumerate(models_to_test):
            assert responses[i]["model"] == model
            assert responses[i]["temperature"] == 0.7
    
    def test_model_not_in_registry(self, stress_test_client):
        """Test handling of models not in registry"""
        client = stress_test_client
        
        response = client.create(
            model="claude-3-opus",  # Not in registry
            input="Test with unavailable model"
        )
        
        assert response["status"] == "failed"
        assert response["error"] is not None
        assert "not supported" in response["error"]["message"]
    
    def test_missing_required_model_parameter(self, stress_test_client):
        """Test that model parameter is required"""
        client = stress_test_client
        
        with pytest.raises(TypeError) as exc_info:
            client.create(input="Test without model")
        
        assert "required" in str(exc_info.value).lower()


class TestBackwardCompatibility:
    """Test backward compatibility with existing code"""
    
    @pytest.fixture
    def legacy_client(self, temp_db_path):
        """Client configured for legacy usage"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Legacy response")
            mock_get_llm.return_value = mock_llm
            
            yield Client(db_path=temp_db_path)
    
    def test_deprecated_cohere_alias_works(self, legacy_client):
        """Test that deprecated 'cohere' alias still works"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            response = legacy_client.create(
                model="cohere",  # Deprecated alias
                input="Test with legacy model name"
            )
            
            # Should work but show warning
            assert response["status"] == "completed"
            assert len(w) > 0
            assert "deprecated" in str(w[0].message).lower()
    
    def test_explicit_model_required(self, legacy_client):
        """Test that model parameter is now required"""
        # This should fail since we removed the default
        with pytest.raises(TypeError):
            legacy_client.create(input="Test without model param")


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_provider_library_not_installed(self):
        """Test graceful handling when provider library not installed"""
        with patch('cortex.responses.llm.OPENAI_AVAILABLE', False):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                # Should return mock LLM with warning
                with patch('builtins.print') as mock_print:
                    llm = get_llm("gpt-4o-mini")
                    
                    # Check warning was printed
                    mock_print.assert_called()
                    call_args = str(mock_print.call_args)
                    assert "OpenAI not available" in call_args
                    assert "pip install langchain-openai" in call_args
    
    def test_temperature_override(self):
        """Test that temperature can be overridden"""
        with patch('cortex.responses.llm.ChatOpenAI') as mock_openai:
            with patch('cortex.responses.llm.OPENAI_AVAILABLE', True):
                with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
                    # Default temperature from registry
                    llm1 = get_llm("gpt-4o")
                    call1 = mock_openai.call_args.kwargs
                    assert call1['temperature'] == 0.7  # Registry default
                    
                    # Override temperature
                    mock_openai.reset_mock()
                    llm2 = get_llm("gpt-4o", temperature=0.2)
                    call2 = mock_openai.call_args.kwargs
                    assert call2['temperature'] == 0.2  # Overridden
    
    def test_max_tokens_passed_correctly(self):
        """Test that max_tokens is passed to each provider correctly"""
        # Test OpenAI
        with patch('cortex.responses.llm.ChatOpenAI') as mock_openai:
            with patch('cortex.responses.llm.OPENAI_AVAILABLE', True):
                with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
                    llm = get_llm("gpt-4-turbo")
                    call_kwargs = mock_openai.call_args.kwargs
                    assert call_kwargs['max_tokens'] == 128000
        
        # Test Google (uses max_output_tokens)
        with patch('cortex.responses.llm.ChatGoogleGenerativeAI') as mock_google:
            with patch('cortex.responses.llm.GOOGLE_AVAILABLE', True):
                with patch.dict(os.environ, {"GOOGLE_API_KEY": "test"}):
                    llm = get_llm("gemini-1.5-pro")
                    call_kwargs = mock_google.call_args.kwargs
                    assert call_kwargs['max_output_tokens'] == 2097152
    
    def test_conversation_persistence_across_providers(self, temp_db_path):
        """Test that conversation history persists when switching providers"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            
            # Track conversation history
            conversation_history = []
            
            def mock_invoke(messages):
                # Store the messages passed to LLM
                conversation_history.append(len(messages))
                return MagicMock(content=f"Response with {len(messages)} messages")
            
            mock_llm.invoke = mock_invoke
            mock_get_llm.return_value = mock_llm
            
            client = Client(db_path=temp_db_path)
            
            # First message with OpenAI
            r1 = client.create(model="gpt-4o", input="First message")
            
            # Second message with Google (should include history)
            r2 = client.create(
                model="gemini-1.5-flash",
                input="Second message",
                previous_response_id=r1["id"]
            )
            
            # Third message with Cohere (should include full history)
            r3 = client.create(
                model="command-r",
                input="Third message",
                previous_response_id=r2["id"]
            )
            
            # Verify conversation history grew
            assert conversation_history[0] <= conversation_history[1]
            assert conversation_history[1] <= conversation_history[2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])