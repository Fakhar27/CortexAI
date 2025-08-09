"""
OpenAI format compatibility tests
Ensures our responses match OpenAI's structure exactly
"""

import pytest
from cortex import Client


class TestResponseFormat:
    """Test that response format matches OpenAI exactly"""
    
    @pytest.mark.critical
    def test_all_required_fields_present(self, client):
        """Test all OpenAI fields are present"""
        response = client.create(
            model="cohere",
            input="Test message"
        )
        
        # All top-level fields that OpenAI returns
        required_fields = [
            "id", "object", "created_at", "status", "error",
            "incomplete_details", "instructions", "max_output_tokens",
            "model", "output", "parallel_tool_calls", "previous_response_id",
            "reasoning", "store", "temperature", "text", "tool_choice",
            "tools", "top_p", "truncation", "usage", "user", "metadata"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in response:
                missing_fields.append(field)
        
        assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"
    
    @pytest.mark.critical
    def test_output_structure(self, client):
        """Test output array structure matches OpenAI"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        # Check output is array
        assert isinstance(response["output"], list)
        assert len(response["output"]) > 0
        
        # Check message structure
        message = response["output"][0]
        assert "type" in message
        assert "id" in message
        assert "status" in message
        assert "role" in message
        assert "content" in message
        
        # Check content structure
        assert isinstance(message["content"], list)
        content = message["content"][0]
        assert "type" in content
        assert "text" in content
        assert "annotations" in content
    
    @pytest.mark.critical
    def test_usage_structure(self, client):
        """Test usage object structure"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        usage = response["usage"]
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert "total_tokens" in usage
        assert "input_tokens_details" in usage
        assert "output_tokens_details" in usage
        
        # Check nested structure
        assert "cached_tokens" in usage["input_tokens_details"]
        assert "reasoning_tokens" in usage["output_tokens_details"]
    
    def test_reasoning_structure(self, client):
        """Test reasoning object structure (for o-series models)"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        assert "reasoning" in response
        assert "effort" in response["reasoning"]
        assert "summary" in response["reasoning"]
    
    def test_text_format_structure(self, client):
        """Test text format configuration structure"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        assert "text" in response
        assert "format" in response["text"]
        assert "type" in response["text"]["format"]
        assert response["text"]["format"]["type"] == "text"
    
    def test_null_fields_exist(self, client):
        """Test that null fields are present (not missing)"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        # These should be None but present
        assert "error" in response
        assert response["error"] is None
        
        assert "incomplete_details" in response
        assert response["incomplete_details"] is None
        
        assert "user" in response
        assert response["user"] is None
    
    def test_default_values(self, client):
        """Test default values match OpenAI"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        assert response["object"] == "response"
        assert response["parallel_tool_calls"] == True
        assert response["tool_choice"] == "auto"
        assert response["tools"] == []
        assert response["top_p"] == 1.0
        assert response["truncation"] == "disabled"


class TestErrorFormat:
    """Test error response format matches OpenAI"""
    
    @pytest.mark.critical
    def test_error_response_structure(self, client):
        """Test error responses have all fields"""
        response = client.create(
            model="invalid-model",
            input="Test"
        )
        
        # Should have all fields even in error
        assert "id" in response
        assert "object" in response
        assert "created_at" in response
        assert "status" in response
        assert "error" in response
        
        # Status should be failed
        assert response["status"] == "failed"
        
        # Error should be populated
        assert response["error"] is not None
        assert "message" in response["error"]
        assert "type" in response["error"]
        
        # Other fields should be None/empty
        assert response["output"] == []
        assert response["usage"] is None
    
    def test_error_object_fields(self, client):
        """Test error object has correct fields"""
        response = client.create(
            model="invalid-model",
            input="Test"
        )
        
        error = response["error"]
        assert "message" in error
        assert "type" in error
        
        # Optional fields may or may not be present
        if "param" in error:
            assert isinstance(error["param"], str)
        if "code" in error:
            assert isinstance(error["code"], str)


class TestClientCompatibility:
    """Test that common OpenAI client patterns work"""
    
    def test_error_checking_pattern(self, client):
        """Test common error checking pattern"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        # This is how OpenAI clients check for errors
        if response["error"] is not None:
            pytest.fail("Should not have error")
        
        # Should be able to access these without KeyError
        assert response["output"][0]["id"]
        assert response["usage"]["input_tokens_details"]["cached_tokens"] == 0
        assert response["output"][0]["content"][0]["annotations"] == []
    
    def test_token_counting_pattern(self, client):
        """Test token counting patterns work"""
        response = client.create(
            model="cohere",
            input="Test message for token counting"
        )
        
        # Common patterns for token counting
        input_tokens = response["usage"]["input_tokens"]
        output_tokens = response["usage"]["output_tokens"]
        total_tokens = response["usage"]["total_tokens"]
        
        assert isinstance(input_tokens, int)
        assert isinstance(output_tokens, int)
        assert isinstance(total_tokens, int)
        assert total_tokens == input_tokens + output_tokens
    
    def test_message_extraction_pattern(self, client):
        """Test message content extraction patterns"""
        response = client.create(
            model="cohere",
            input="Say hello"
        )
        
        # Common way to extract message content
        content = response["output"][0]["content"][0]["text"]
        assert isinstance(content, str)
        assert len(content) > 0
        
        # Message ID extraction
        msg_id = response["output"][0]["id"]
        assert msg_id.startswith("msg_")