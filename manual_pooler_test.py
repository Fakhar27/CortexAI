#!/usr/bin/env python3
"""
Manual conversation test for pooler connections
Allows switching between backends and models interactively
Similar to Django view but runs from command line
"""

import json
import time
import sys
import os
from typing import Optional, Dict, Any

# Add cortex to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import Client


def print_separator(title: str = ""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*80}")
        print(f" {title}")
        print('='*80)
    else:
        print('='*80)


def get_backend_url(backend: str) -> str:
    """Get database URL for the specified backend"""
    if backend == 'pooler':
        # Supabase pooler connection
        url = "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
        print(f"[BACKEND] Using Pooler: {url.split('@')[1]}")
        return url
    elif backend == 'local':
        # Local PostgreSQL
        url = "postgresql://postgres:postgres@localhost:5432/cortex"
        print(f"[BACKEND] Using Local PostgreSQL")
        return url
    else:  # sqlite
        # SQLite (empty string)
        print(f"[BACKEND] Using SQLite")
        return ""


def test_conversation(
    backend: str,
    message: str,
    model: str = 'gpt-4o-mini',
    instructions: Optional[str] = None,
    previous_response_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test a single conversation turn
    
    Args:
        backend: 'pooler', 'local', or 'sqlite'
        message: User message
        model: LLM model to use
        instructions: System instructions
        previous_response_id: ID to continue conversation
        
    Returns:
        Response dictionary
    """
    print_separator("MANUAL CONVERSATION TEST")
    
    print(f"[TEST] Parameters:")
    print(f"  - Backend: {backend}")
    print(f"  - Model: {model}")
    print(f"  - Message: {message[:100]}...")
    print(f"  - Instructions: {'Yes' if instructions else 'No'}")
    print(f"  - Previous Response ID: {previous_response_id or 'None (new conversation)'}")
    
    # Get database URL
    db_url = get_backend_url(backend)
    
    # Initialize client
    print(f"\n[TEST] Initializing client...")
    client = Client(db_url=db_url)
    
    # Build request parameters
    request_params = {
        'model': model,
        'input': message,
        'store': True,
        'temperature': 0.7
    }
    
    if instructions:
        request_params['instructions'] = instructions
    
    if previous_response_id:
        request_params['previous_response_id'] = previous_response_id
    
    print(f"\n[TEST] Request parameters:")
    for key, value in request_params.items():
        if key != 'input':
            print(f"  - {key}: {value}")
    
    # Make the API call
    print(f"\n[TEST] Making API call...")
    start_time = time.time()
    
    try:
        response = client.create(**request_params)
        execution_time = time.time() - start_time
        
        print(f"\n[TEST] ✅ Response received in {execution_time:.2f}s")
        print(f"  - Response ID: {response.get('id', 'No ID')}")
        print(f"  - Status: {response.get('status', 'Unknown')}")
        
        # Extract text from response
        output = response.get('output', [])
        if output and len(output) > 0:
            content = output[0].get('content', [])
            if content and len(content) > 0:
                text = content[0].get('text', '')
                print(f"\n[RESPONSE] {text[:200]}{'...' if len(text) > 200 else ''}")
        
        return response
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n[TEST] ❌ ERROR after {execution_time:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'success': False}


def interactive_mode():
    """Run interactive conversation mode"""
    print_separator("INTERACTIVE POOLER TEST")
    print("\nThis tool allows you to test conversations with different backends and models.")
    print("\nAvailable backends:")
    print("  - pooler : Supabase pooler (tests concurrency issues)")
    print("  - local  : Local PostgreSQL")
    print("  - sqlite : SQLite (default)")
    print("\nAvailable models:")
    print("  - gpt-4o-mini")
    print("  - gemini-1.5-flash")
    print("  - command-r")
    print("  - claude-3-haiku")
    
    # Initialize conversation state
    current_backend = 'pooler'
    current_model = 'gpt-4o-mini'
    previous_response_id = None
    instructions = "You are a helpful assistant."
    
    while True:
        print_separator()
        print(f"\nCurrent settings:")
        print(f"  Backend: {current_backend}")
        print(f"  Model: {current_model}")
        print(f"  Conversation ID: {previous_response_id or 'New conversation'}")
        
        print("\nCommands:")
        print("  /backend <name>  - Switch backend (pooler/local/sqlite)")
        print("  /model <name>    - Switch model")
        print("  /new             - Start new conversation")
        print("  /instructions    - Set system instructions")
        print("  /test            - Test current setup with a simple message")
        print("  /alternate       - Test alternating between GPT and Gemini")
        print("  /quit            - Exit")
        print("\n  Or just type your message...")
        
        user_input = input("\n> ").strip()
        
        if not user_input:
            continue
            
        # Handle commands
        if user_input.startswith('/'):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == '/quit':
                print("\nGoodbye!")
                break
                
            elif command == '/backend':
                if len(parts) > 1:
                    backend = parts[1].lower()
                    if backend in ['pooler', 'local', 'sqlite']:
                        current_backend = backend
                        previous_response_id = None  # Reset conversation
                        print(f"✅ Switched to {backend} backend")
                    else:
                        print(f"❌ Unknown backend: {backend}")
                else:
                    print("Usage: /backend <pooler|local|sqlite>")
                    
            elif command == '/model':
                if len(parts) > 1:
                    current_model = parts[1]
                    print(f"✅ Switched to model: {current_model}")
                else:
                    print("Usage: /model <model-name>")
                    
            elif command == '/new':
                previous_response_id = None
                print("✅ Started new conversation")
                
            elif command == '/instructions':
                print("Enter system instructions (or empty to clear):")
                instructions = input("> ").strip() or None
                print(f"✅ Instructions {'set' if instructions else 'cleared'}")
                
            elif command == '/test':
                print("\n[QUICK TEST] Testing with 'Hello, how are you?'")
                response = test_conversation(
                    backend=current_backend,
                    message="Hello, how are you?",
                    model=current_model,
                    instructions=instructions,
                    previous_response_id=previous_response_id
                )
                if 'id' in response:
                    previous_response_id = response['id']
                    
            elif command == '/alternate':
                print("\n[ALTERNATE TEST] Testing model switching with memory...")
                
                # First message with GPT
                print("\n1. Sending with GPT-4...")
                response1 = test_conversation(
                    backend=current_backend,
                    message="Remember the number 42. What model are you?",
                    model='gpt-4o-mini',
                    instructions=instructions,
                    previous_response_id=previous_response_id
                )
                
                if 'id' in response1:
                    # Second message with Gemini
                    print("\n2. Switching to Gemini...")
                    response2 = test_conversation(
                        backend=current_backend,
                        message="What number did I ask you to remember? What model are you now?",
                        model='gemini-1.5-flash',
                        instructions=instructions,
                        previous_response_id=response1['id']
                    )
                    
                    if 'id' in response2:
                        # Third message back to GPT
                        print("\n3. Switching back to GPT-4...")
                        response3 = test_conversation(
                            backend=current_backend,
                            message="Can you still recall the number? What model are you?",
                            model='gpt-4o-mini',
                            instructions=instructions,
                            previous_response_id=response2['id']
                        )
                        
                        if 'id' in response3:
                            previous_response_id = response3['id']
                            print("\n✅ Model alternation test complete!")
                            print("Check if the conversation maintained memory across models.")
                
            else:
                print(f"❌ Unknown command: {command}")
                
        else:
            # Regular message
            response = test_conversation(
                backend=current_backend,
                message=user_input,
                model=current_model,
                instructions=instructions,
                previous_response_id=previous_response_id
            )
            
            if 'id' in response:
                previous_response_id = response['id']
                print(f"\n✅ Response ID saved: {previous_response_id}")


if __name__ == "__main__":
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)