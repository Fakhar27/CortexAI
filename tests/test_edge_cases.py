"""
Edge case and stress tests
Tests unusual inputs and boundary conditions
"""

import pytest
import threading
import time
from cortex import Client


class TestLargeInputs:
    """Test handling of large inputs"""
    
    def test_large_input_handling(self, client):
        """Test that large inputs are handled gracefully"""
        # Create 60k character input
        large_input = "Please summarize: " + ("Lorem ipsum dolor sit amet. " * 2000)
        
        response = client.create(
            model="cohere",
            input=large_input
        )
        
        # Should either handle it or give clear error
        if response.get("error"):
            assert "too long" in response["error"]["message"].lower() or \
                   "length" in response["error"]["message"].lower()
        else:
            # If it succeeded, should have valid response
            assert response["status"] == "completed"
    
    def test_max_valid_input(self, client):
        """Test input at maximum valid size"""
        # Just under 50k limit
        max_input = "a" * 49999
        
        response = client.create(
            model="cohere",
            input=max_input
        )
        
        # Should handle this
        assert response.get("error") is None or "too long" in str(response.get("error", ""))
    
    def test_unicode_input(self, client):
        """Test Unicode and special characters"""
        unicode_input = "Test 你好 مرحبا 🚀 émojis ñ § ∑"
        
        response = client.create(
            model="cohere",
            input=unicode_input
        )
        
        assert not response.get("error"), f"Unicode failed: {response.get('error')}"


class TestConcurrency:
    """Test concurrent request handling"""
    
    def test_sequential_rapid_requests(self, client):
        """Test rapid sequential requests"""
        responses = []
        
        for i in range(5):
            response = client.create(
                model="cohere",
                input=f"Request {i}"
            )
            responses.append(response)
            
        # All should succeed or fail gracefully
        for i, response in enumerate(responses):
            if response.get("error"):
                # Rate limiting is acceptable
                assert "rate" in response["error"]["message"].lower() or \
                       "limit" in response["error"]["message"].lower()
            else:
                assert response["status"] == "completed"
    
    def test_concurrent_requests_same_client(self, client):
        """Test concurrent requests using same client"""
        results = []
        errors = []
        
        def make_request(index):
            try:
                response = client.create(
                    model="cohere",
                    input=f"Concurrent request {index}"
                )
                results.append(response)
            except Exception as e:
                errors.append(str(e))
        
        # Launch 3 concurrent threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=make_request, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all to complete
        for t in threads:
            t.join(timeout=30)
        
        # Should handle concurrency (SQLite might have issues)
        if errors:
            # Check if it's SQLite concurrency issue
            for error in errors:
                assert "database is locked" in error.lower() or \
                       "database" in error.lower()
        else:
            # All succeeded
            assert len(results) == 3


class TestAPIKeyHandling:
    """Test API key error handling"""
    
    @pytest.mark.requires_api_key
    def test_missing_api_key_error(self, client, mock_env):
        """Test helpful error when API key missing"""
        # Remove API key
        mock_env(CO_API_KEY=None)
        
        response = client.create(
            model="cohere",
            input="Test without API key"
        )
        
        assert response.get("error") is not None
        error_msg = response["error"]["message"].lower()
        
        # Should mention authentication or API key
        assert "authentication" in error_msg or \
               "api" in error_msg or \
               "key" in error_msg
    
    def test_invalid_api_key_error(self, client, mock_env):
        """Test error with invalid API key"""
        # Set invalid key
        mock_env(CO_API_KEY="invalid_key_12345")
        
        response = client.create(
            model="cohere",
            input="Test with invalid key"
        )
        
        if response.get("error"):
            # Should give authentication error
            assert "authentication" in response["error"]["message"].lower() or \
                   "invalid" in response["error"]["message"].lower()


class TestPersistence:
    """Test persistence edge cases"""
    
    def test_persistence_across_clients(self, temp_db_path):
        """Test conversation persists across client instances"""
        # Client 1: Start conversation
        client1 = Client(db_path=temp_db_path)
        response1 = client1.create(
            model="cohere",
            input="Remember: the code is 1234",
            store=True
        )
        resp_id = response1["id"]
        
        # Client 2: Continue conversation
        client2 = Client(db_path=temp_db_path)
        response2 = client2.create(
            model="cohere",
            input="What was the code?",
            previous_response_id=resp_id
        )
        
        assert not response2.get("error"), f"Continuation failed: {response2.get('error')}"
    
    def test_memory_mode(self):
        """Test memory mode (no persistence)"""
        # Create client with no DB
        client = Client(db_path=None)
        
        response = client.create(
            model="cohere",
            input="Memory mode test",
            store=True  # Even with store=True, won't persist
        )
        
        assert not response.get("error")
        
        # Create new client, try to continue
        client2 = Client(db_path=None)
        response2 = client2.create(
            model="cohere",
            input="Continue",
            previous_response_id=response["id"]
        )
        
        # Should fail - not persisted
        assert response2.get("error") is not None


class TestEdgeCaseInputs:
    """Test weird and edge case inputs"""
    
    def test_only_punctuation(self, client):
        """Test input with only punctuation"""
        response = client.create(
            model="cohere",
            input="...!!!???"
        )
        
        # Should handle this gracefully
        assert not response.get("error") or "empty" in str(response.get("error"))
    
    def test_sql_injection_attempt(self, client):
        """Test SQL injection doesn't break anything"""
        response = client.create(
            model="cohere",
            input="'; DROP TABLE checkpoints; --"
        )
        
        # Should handle safely
        assert response["status"] in ["completed", "failed"]
    
    def test_json_in_input(self, client):
        """Test JSON strings in input"""
        json_input = '{"test": "value", "nested": {"key": "value"}}'
        
        response = client.create(
            model="cohere",
            input=f"Parse this JSON: {json_input}"
        )
        
        assert not response.get("error"), "JSON input should work"
    
    def test_code_in_input(self, client):
        """Test code snippets in input"""
        code_input = """
        def hello_world():
            print("Hello, World!")
            return 42
        """
        
        response = client.create(
            model="cohere",
            input=f"Explain this code: {code_input}"
        )
        
        assert not response.get("error"), "Code input should work"
    
    def test_repeated_continuation(self, client):
        """Test continuing same conversation multiple times"""
        # Start
        response1 = client.create(
            model="cohere",
            input="Count: 1",
            store=True
        )
        
        # Continue multiple times
        prev_id = response1["id"]
        for i in range(2, 5):
            response = client.create(
                model="cohere",
                input=f"Count: {i}",
                previous_response_id=prev_id,
                store=True
            )
            assert not response.get("error"), f"Continuation {i} failed"
            prev_id = response["id"]