#!/usr/bin/env python3
"""
AWS Lambda function for testing pooler connections with provider switching.
Returns JSON response with all logs and test results.
"""

import json
import sys
import os
import traceback
from datetime import datetime
from io import StringIO

# Add cortex to path if needed
sys.path.insert(0, '/opt/python')  # For Lambda layers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def capture_output(func, *args, **kwargs):
    """Capture stdout/stderr from a function"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        result = func(*args, **kwargs)
        return result, stdout_capture.getvalue(), stderr_capture.getvalue()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

def extract_response_text(response):
    """Extract text from response output"""
    output = response.get("output", [])
    
    if isinstance(output, list) and len(output) > 0:
        first_item = output[0]
        if isinstance(first_item, dict):
            # Handle nested structure
            content = first_item.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                content_item = content[0]
                if isinstance(content_item, dict):
                    return content_item.get("text", str(content_item))
            return first_item.get("text", str(first_item))
    
    return str(output) if output else "No response"

def lambda_handler(event, context):
    """
    AWS Lambda handler for pooler connection testing
    
    Parameters (passed in event):
    - db_url: PostgreSQL pooler connection string (required)
    - test_name: Name for this test run (optional, default: "pooler_test")
    - models: Dict of model names to test (optional, default: gpt-4o-mini and gemini-1.5-flash)
    - test_data: Dict with test inputs (optional)
        - user_name: Name to remember (default: "Steve")
        - favorite_color: Color to remember (default: "purple")
        - initial_instructions: System prompt for first message
        - pirate_instructions: Pirate style instructions for mid-conversation
    - run_tests: List of test numbers to run (optional, default: [1,2,3])
    
    Returns:
    - JSON response with:
        - success: boolean
        - test_name: string
        - timestamp: ISO format timestamp
        - tests_run: list of test results
        - summary: test summary
        - errors: any errors encountered
        - logs: captured stdout/stderr
    """
    
    # Initialize response structure
    response = {
        "success": False,
        "test_name": event.get("test_name", f"pooler_test_{int(datetime.now().timestamp())}"),
        "timestamp": datetime.utcnow().isoformat(),
        "tests_run": [],
        "summary": {},
        "errors": [],
        "logs": {
            "stdout": "",
            "stderr": ""
        }
    }
    
    try:
        from cortex import Client
        
        # Get parameters from event
        db_url = event.get("db_url")
        if not db_url:
            raise ValueError("db_url is required in event parameters")
        
        # Get test configuration
        models = event.get("models", {
            "primary": "gpt-4o-mini",
            "secondary": "gemini-1.5-flash"
        })
        
        test_data = event.get("test_data", {
            "user_name": "Steve",
            "favorite_color": "purple",
            "initial_instructions": "You are a helpful assistant who always mentions the weather is sunny today when greeting someone.",
            "pirate_instructions": "You must speak like a pirate in all your responses. Use 'arr', 'matey', 'ahoy' frequently."
        })
        
        run_tests = event.get("run_tests", [1, 2, 3])
        
        # Initialize client
        print(f"Initializing client with pooler URL: {db_url[:60]}...")
        client = Client(db_url=db_url)
        response["logs"]["stdout"] += f"Client initialized successfully\n"
        
        # Store response IDs for chaining
        response_ids = {}
        
        # Test 1: Initial conversation with primary model
        if 1 in run_tests:
            test1_result = {
                "test_number": 1,
                "test_name": "Initial conversation with instructions",
                "model": models["primary"],
                "success": False,
                "response": None,
                "error": None
            }
            
            try:
                print(f"\nTest 1: Initial conversation with {models['primary']}")
                response1 = client.create(
                    model=models["primary"],
                    input=f"My name is {test_data['user_name']} and my favorite color is {test_data['favorite_color']}. Remember this.",
                    store=True,
                    temperature=0.5,
                    instructions=test_data["initial_instructions"]
                )
                
                response_ids["test1"] = response1["id"]
                response_text = extract_response_text(response1)
                
                test1_result["success"] = True
                test1_result["response"] = {
                    "id": response1["id"],
                    "text": response_text,
                    "mentions_weather": "sunny" in response_text.lower() or "weather" in response_text.lower()
                }
                
                print(f"Test 1 Success: {response_text}")
                
            except Exception as e:
                test1_result["error"] = str(e)
                print(f"Test 1 Failed: {e}")
            
            response["tests_run"].append(test1_result)
        
        # Test 2: Switch to secondary model and check memory
        if 2 in run_tests and response_ids.get("test1"):
            test2_result = {
                "test_number": 2,
                "test_name": "Provider switch - memory retention",
                "model": models["secondary"],
                "success": False,
                "response": None,
                "error": None
            }
            
            try:
                print(f"\nTest 2: Switch to {models['secondary']} - checking memory")
                response2 = client.create(
                    model=models["secondary"],
                    input="What's my name and favorite color?",
                    previous_response_id=response_ids["test1"],
                    store=True,
                    temperature=0.5
                )
                
                response_ids["test2"] = response2["id"]
                response_text = extract_response_text(response2)
                
                # Check if memory persisted
                remembers_name = test_data["user_name"].lower() in response_text.lower()
                remembers_color = test_data["favorite_color"].lower() in response_text.lower()
                
                test2_result["success"] = True
                test2_result["response"] = {
                    "id": response2["id"],
                    "text": response_text,
                    "remembers_name": remembers_name,
                    "remembers_color": remembers_color,
                    "memory_intact": remembers_name and remembers_color
                }
                
                print(f"Test 2 - Memory intact: {remembers_name and remembers_color}")
                
            except Exception as e:
                test2_result["error"] = str(e)
                print(f"Test 2 Failed: {e}")
            
            response["tests_run"].append(test2_result)
        
        # Test 3: Update instructions mid-conversation
        if 3 in run_tests and response_ids.get("test2"):
            test3_result = {
                "test_number": 3,
                "test_name": "Instruction update mid-conversation",
                "model": models["secondary"],
                "success": False,
                "response": None,
                "error": None
            }
            
            try:
                print(f"\nTest 3: Updating instructions to pirate style")
                response3 = client.create(
                    model=models["secondary"],
                    input="From now on, please respond in a pirate style. Now tell me what you remember about me.",
                    previous_response_id=response_ids["test2"],
                    store=True,
                    temperature=0.5,
                    instructions=test_data["pirate_instructions"]
                )
                
                response_ids["test3"] = response3["id"]
                response_text = extract_response_text(response3)
                
                # Check for pirate style and memory
                pirate_words = ["arr", "matey", "ahoy", "ye", "treasure", "sail", "captain"]
                has_pirate_style = any(word.lower() in response_text.lower() for word in pirate_words)
                remembers_info = (test_data["user_name"].lower() in response_text.lower() or 
                                test_data["favorite_color"].lower() in response_text.lower())
                
                test3_result["success"] = True
                test3_result["response"] = {
                    "id": response3["id"],
                    "text": response_text,
                    "has_pirate_style": has_pirate_style,
                    "remembers_info": remembers_info,
                    "pirate_words_found": [word for word in pirate_words if word.lower() in response_text.lower()]
                }
                
                print(f"Test 3 - Pirate style: {has_pirate_style}, Memory: {remembers_info}")
                
            except Exception as e:
                test3_result["error"] = str(e)
                print(f"Test 3 Failed: {e}")
            
            response["tests_run"].append(test3_result)
        
        # Generate summary
        total_tests = len(response["tests_run"])
        successful_tests = sum(1 for test in response["tests_run"] if test["success"])
        
        response["summary"] = {
            "total_tests_run": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "memory_working": any(
                test.get("response", {}).get("memory_intact", False) 
                for test in response["tests_run"] 
                if test["test_number"] == 2
            ),
            "instructions_working": any(
                test.get("response", {}).get("has_pirate_style", False) 
                for test in response["tests_run"] 
                if test["test_number"] == 3
            ),
            "response_ids_generated": response_ids
        }
        
        response["success"] = successful_tests == total_tests
        
        # Capture any remaining logs
        stdout_capture = StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_capture
        
    except Exception as e:
        response["errors"].append({
            "type": "fatal",
            "message": str(e),
            "traceback": traceback.format_exc()
        })
        response["success"] = False
    
    finally:
        # Restore stdout
        if 'old_stdout' in locals():
            sys.stdout = old_stdout
        
        # Add captured logs
        if 'stdout_capture' in locals():
            response["logs"]["stdout"] += stdout_capture.getvalue()
    
    return response

# For local testing
if __name__ == "__main__":
    # Example event for testing
    test_event = {
        "db_url": "postgresql://postgres.tqovtjyylrykgpehbfdl:Fakhar_27_1$@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres",
        "test_name": "local_test",
        "models": {
            "primary": "gpt-4o-mini",
            "secondary": "gemini-1.5-flash"
        },
        "test_data": {
            "user_name": "Alice",
            "favorite_color": "blue",
            "initial_instructions": "You are a helpful assistant.",
            "pirate_instructions": "You must speak like a pirate."
        },
        "run_tests": [1, 2, 3]
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))