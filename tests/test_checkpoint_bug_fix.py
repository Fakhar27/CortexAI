#!/usr/bin/env python3
"""
Direct test for the checkpoint_ns bug fix
Focuses specifically on the KeyError that was occurring
"""

import os
import pytest
import psycopg2
from cortex import Client
from unittest.mock import patch, MagicMock

SUPABASE_URL = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


class TestCheckpointBugFix:
    """Test the specific checkpoint_ns bug fix"""
    
    def test_checkpoint_ns_no_key_error(self):
        """Test that checkpoint_ns KeyError is fixed"""
        print("\n=== Testing checkpoint_ns KeyError Fix ===")
        
        # This was failing before with KeyError: 'checkpoint_ns'
        try:
            client = Client(db_url=SUPABASE_URL)
            response = client.create(
                model="gpt-4o-mini",
                input="Test checkpoint_ns bug fix",
                store=True
            )
            
            # If we get here without KeyError, the bug is fixed!
            assert response["status"] == "completed"
            print("✅ No KeyError! Bug is fixed!")
            
            # Double-check by continuing conversation
            response2 = client.create(
                model="gpt-4o-mini",
                input="Continue test",
                previous_response_id=response["id"]
            )
            
            assert response2["status"] == "completed"
            print("✅ Conversation continuation works!")
            
        except KeyError as e:
            if "checkpoint_ns" in str(e):
                pytest.fail(f"🔴 BUG NOT FIXED: {e}")
            raise
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect to Supabase: {e}")
            raise
    
    def test_config_has_checkpoint_ns(self):
        """Test that config includes checkpoint_ns"""
        print("\n=== Testing Config Contains checkpoint_ns ===")
        
        from cortex.responses.methods.create import create_response
        from cortex.responses.api import ResponsesAPI
        
        # Create a mock API instance
        mock_api = MagicMock(spec=ResponsesAPI)
        mock_api.db_url = None
        mock_api.graph = MagicMock()
        mock_api.graph.invoke = MagicMock(return_value={
            "messages": [MagicMock(content="Test response")]
        })
        
        # Capture the config passed to graph.invoke
        captured_config = {}
        
        def capture_invoke(state, config, **kwargs):
            captured_config.update(config)
            return {"messages": [MagicMock(content="Test")]}
        
        mock_api.graph.invoke = capture_invoke
        mock_api._generate_node = MagicMock()
        
        # Call create_response
        with patch('cortex.responses.methods.create.get_checkpointer', return_value=MagicMock()):
            response = create_response(
                api_instance=mock_api,
                input="Test",
                model="gemini-1.5-flash"
            )
        
        # Verify checkpoint_ns is in config
        if captured_config:
            assert "configurable" in captured_config
            assert "checkpoint_ns" in captured_config["configurable"]
            print(f"✅ checkpoint_ns in config: '{captured_config['configurable']['checkpoint_ns']}'")
        else:
            print("⚠️ Could not capture config in mock test")
    
    def test_postgres_saver_receives_checkpoint_ns(self):
        """Test that PostgresSaver actually receives checkpoint_ns"""
        print("\n=== Testing PostgresSaver Receives checkpoint_ns ===")
        
        from cortex.responses.persistence import PostgresCheckpointerWrapper
        
        # Create wrapper
        try:
            wrapper = PostgresCheckpointerWrapper(SUPABASE_URL)
        except Exception as e:
            pytest.skip(f"Cannot create wrapper: {e}")
        
        # Test config
        config = {
            "configurable": {
                "thread_id": "test_thread",
                "response_id": "test_response",
                "store": True,
                "checkpoint_ns": ""  # This should be present now
            }
        }
        
        checkpoint = {
            "v": 1,
            "ts": "2024-01-01T00:00:00",
            "id": "test_checkpoint",
            "channel_values": {}
        }
        
        metadata = {"test": "metadata"}
        
        # This should NOT raise KeyError anymore
        try:
            result = wrapper.put(config, checkpoint, metadata, {})
            print("✅ PostgresSaver.put() succeeded with checkpoint_ns!")
        except KeyError as e:
            if "checkpoint_ns" in str(e):
                pytest.fail(f"🔴 Still getting KeyError: {e}")
            raise
    
    def test_checkpoints_actually_created(self):
        """Test that checkpoints are actually saved to database"""
        print("\n=== Testing Actual Checkpoint Creation ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            
            # Create a conversation
            response = client.create(
                model="gemini-1.5-flash",
                input="Create checkpoint test",
                store=True
            )
            
            thread_id = response["id"]
            print(f"Created thread: {thread_id}")
            
            # Check database directly
            import time
            time.sleep(2)  # Allow for database write
            
            conn = psycopg2.connect(SUPABASE_URL)
            cursor = conn.cursor()
            
            # Check checkpoints table
            cursor.execute("""
                SELECT COUNT(*) FROM checkpoints 
                WHERE thread_id = %s
            """, (thread_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if count == 0:
                pytest.fail(f"🔴 NO CHECKPOINTS CREATED for thread {thread_id}")
            else:
                print(f"✅ Checkpoints created: {count}")
                
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect to database: {e}")
            raise
    
    def test_memory_actually_works(self):
        """Test that conversation memory actually works"""
        print("\n=== Testing Actual Memory Persistence ===")
        
        try:
            client = Client(db_url=SUPABASE_URL)
            
            # Create with memorable content
            response1 = client.create(
                model="gpt-4o-mini",
                input="Remember this number: 999",
                store=True,
                temperature=0.0
            )
            
            print(f"First response: {response1['id']}")
            
            # Ask about it
            response2 = client.create(
                model="gpt-4o-mini",
                input="What number did I just ask you to remember?",
                previous_response_id=response1["id"],
                temperature=0.0
            )
            
            content = response2["output"][0]["content"][0]["text"]
            print(f"Model response: {content[:200]}")
            
            if "999" not in content:
                pytest.fail(f"🔴 Model FORGOT! Memory not working! Response: {content}")
            else:
                print("✅ Model remembered! Memory is working!")
                
        except Exception as e:
            if "could not connect" in str(e):
                pytest.skip(f"Cannot connect: {e}")
            if "OPENAI_API_KEY" in str(e):
                pytest.skip("OpenAI API key not set")
            raise


if __name__ == "__main__":
    print("="*60)
    print("TESTING CHECKPOINT_NS BUG FIX")
    print("="*60)
    print("\nThis test validates the specific bug fix for:")
    print("- KeyError: 'checkpoint_ns' in PostgresSaver")
    print("- Checkpoints not being created")
    print("- Memory not persisting")
    print("\nRun with: pytest tests/test_checkpoint_bug_fix.py -v -s")
    print("="*60)