"""
Core functionality tests - The absolute essentials
These MUST pass for the package to be usable
"""

import pytest
from cortex import Client


class TestBasicCreation:
    """Test the most basic create() functionality"""
    
    @pytest.mark.critical
    def test_client_instantiation(self):
        """Test that we can create a client"""
        client = Client()
        assert client is not None
        assert hasattr(client, 'create')
    
    @pytest.mark.critical
    def test_basic_create_structure(self, client):
        """Test that create returns proper structure"""
        response = client.create(
            model="cohere",
            input="Test message"
        )
        
        # Must have these fields
        assert "id" in response
        assert "status" in response
        assert "output" in response
        
        # Check types
        assert isinstance(response["id"], str)
        assert isinstance(response["output"], list)
    
    @pytest.mark.critical
    def test_response_id_format(self, client):
        """Test that response IDs have correct format"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        # Should start with resp_
        assert response["id"].startswith("resp_"), f"Invalid ID format: {response['id']}"
        
        # Should have message ID
        assert response["output"][0]["id"].startswith("msg_"), "Message ID should start with msg_"
    
    @pytest.mark.critical
    def test_error_response_structure(self, client):
        """Test that errors have proper structure"""
        response = client.create(
            model="invalid-model-xyz",
            input="Test"
        )
        
        assert "error" in response
        assert response["status"] == "failed"
        assert "message" in response["error"]
        assert "type" in response["error"]


class TestConversationContinuity:
    """Test the killer feature - conversation continuity"""
    
    @pytest.mark.critical
    def test_basic_continuity(self, client):
        """Test basic conversation continuity"""
        # First message
        response1 = client.create(
            model="cohere",
            input="My name is Alice",
            store=True
        )
        
        assert not response1.get("error"), f"First message failed: {response1.get('error')}"
        
        # Continue conversation
        response2 = client.create(
            model="cohere",
            input="What's my name?",
            previous_response_id=response1["id"]
        )
        
        assert not response2.get("error"), f"Continuation failed: {response2.get('error')}"
        assert response2["previous_response_id"] == response1["id"]
    
    @pytest.mark.critical
    def test_invalid_previous_response_id(self, client):
        """Test error when previous_response_id doesn't exist"""
        response = client.create(
            model="cohere",
            input="Continue",
            previous_response_id="resp_nonexistent123"
        )
        
        assert response.get("error") is not None
        assert "not found" in response["error"]["message"].lower()
    
    def test_store_false_not_persisted(self, client):
        """Test that store=False doesn't persist"""
        # Create without storing
        response1 = client.create(
            model="cohere",
            input="Don't store this",
            store=False
        )
        
        # Try to continue - should fail
        response2 = client.create(
            model="cohere",
            input="Continue",
            previous_response_id=response1["id"]
        )
        
        assert response2.get("error") is not None
        assert "not found" in response2["error"]["message"].lower()


class TestInputValidation:
    """Test input validation and error handling"""
    
    @pytest.mark.critical
    def test_empty_input_rejected(self, client):
        """Test that empty input is rejected"""
        response = client.create(
            model="cohere",
            input=""
        )
        
        assert response.get("error") is not None
        assert "empty" in response["error"]["message"].lower()
    
    @pytest.mark.critical
    def test_whitespace_input_rejected(self, client):
        """Test that whitespace-only input is rejected"""
        response = client.create(
            model="cohere",
            input="   \n\t   "
        )
        
        assert response.get("error") is not None
        assert "empty" in response["error"]["message"].lower() or "whitespace" in response["error"]["message"].lower()
    
    @pytest.mark.critical
    def test_invalid_model_rejected(self, client):
        """Test that invalid models are rejected"""
        response = client.create(
            model="gpt-5000-ultra",
            input="Test"
        )
        
        assert response.get("error") is not None
        assert "not supported" in response["error"]["message"].lower()
        # Should list available models
        assert "Available models" in response["error"]["message"]
    
    def test_invalid_temperature_rejected(self, client):
        """Test temperature validation"""
        # Too high
        response = client.create(
            model="cohere",
            input="Test",
            temperature=3.0
        )
        assert response.get("error") is not None
        assert "between 0 and 2.0" in response["error"]["message"]
        
        # Negative
        response = client.create(
            model="cohere",
            input="Test",
            temperature=-1.0
        )
        assert response.get("error") is not None
        assert "between 0 and 2.0" in response["error"]["message"]
    
    def test_valid_temperature_accepted(self, client):
        """Test valid temperature values"""
        # Min
        response = client.create(
            model="cohere",
            input="Test",
            temperature=0.0
        )
        assert response.get("error") is None
        assert response["temperature"] == 0.0
        
        # Max
        response = client.create(
            model="cohere",
            input="Test",
            temperature=2.0
        )
        assert response.get("error") is None
        assert response["temperature"] == 2.0


class TestMetadata:
    """Test metadata handling"""
    
    def test_metadata_stored(self, client):
        """Test that metadata is included in response"""
        metadata = {"user_id": "123", "session": "abc"}
        response = client.create(
            model="cohere",
            input="Test",
            metadata=metadata
        )
        
        assert response.get("metadata") == metadata
    
    def test_empty_metadata(self, client):
        """Test empty metadata handling"""
        response = client.create(
            model="cohere",
            input="Test",
            metadata={}
        )
        
        assert response.get("metadata") == {}
    
    def test_no_metadata(self, client):
        """Test when no metadata provided"""
        response = client.create(
            model="cohere",
            input="Test"
        )
        
        assert response.get("metadata") == {}
    
    def test_invalid_metadata_rejected(self, client):
        """Test that invalid metadata is rejected"""
        response = client.create(
            model="cohere",
            input="Test",
            metadata="not a dict"  # Should be dict
        )
        
        assert response.get("error") is not None
        assert "dictionary" in response["error"]["message"].lower()


class TestInstructions:
    """Test instructions parameter behavior"""
    
    def test_instructions_in_new_conversation(self, client):
        """Test instructions are included for new conversations"""
        response = client.create(
            model="cohere",
            input="Hello",
            instructions="You are a helpful assistant"
        )
        
        assert response.get("instructions") == "You are a helpful assistant"
    
    @pytest.mark.critical
    def test_instructions_discarded_on_continuation(self, client):
        """Test instructions are discarded when continuing (OpenAI spec)"""
        # Start conversation
        response1 = client.create(
            model="cohere",
            input="Hello",
            instructions="You are a helpful assistant",
            store=True
        )
        
        # Continue with different instructions
        response2 = client.create(
            model="cohere",
            input="Hi again",
            previous_response_id=response1["id"],
            instructions="You are now a pirate"  # Should be ignored
        )
        
        # Instructions should be None when continuing
        assert response2.get("instructions") is None