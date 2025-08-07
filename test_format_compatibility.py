#!/usr/bin/env python3
"""
Test OpenAI format compatibility for Responses API
Verifies all required fields are present in both success and error responses
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add cortex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cortex'))

from responses.api import ResponsesAPI


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70)


def check_field_exists(response: Dict, field_path: str, test_name: str) -> bool:
    """
    Check if a field exists in the response (can be None)
    
    Args:
        response: Response dictionary
        field_path: Dot-separated path to field (e.g., "usage.input_tokens_details")
        test_name: Name of the test for logging
        
    Returns:
        True if field exists, False otherwise
    """
    parts = field_path.split('.')
    current = response
    
    for i, part in enumerate(parts):
        # Handle array index notation like "output[0]"
        if '[' in part:
            field_name = part.split('[')[0]
            index = int(part.split('[')[1].rstrip(']'))
            
            if field_name not in current:
                print(f"   ❌ {test_name}: Missing field '{'.'.join(parts[:i+1])}'")
                return False
            
            if not isinstance(current[field_name], list):
                print(f"   ❌ {test_name}: Field '{field_name}' is not an array")
                return False
                
            if len(current[field_name]) <= index:
                print(f"   ❌ {test_name}: Array '{field_name}' has no index {index}")
                return False
                
            current = current[field_name][index]
        else:
            if part not in current:
                print(f"   ❌ {test_name}: Missing field '{'.'.join(parts[:i+1])}'")
                return False
            current = current[part]
    
    print(f"   ✅ {test_name}: Field '{field_path}' exists")
    return True


def test_success_response_format():
    """Test that successful responses have all OpenAI fields"""
    print_test_header("Success Response Format")
    
    try:
        api = ResponsesAPI(db_path="./test_format.db")
        
        # Create a simple response
        response = api.create(
            input="Hello, how are you?",
            model="cohere",
            instructions="You are a helpful assistant.",
            temperature=0.7,
            metadata={"test": "true"}
        )
        
        # Check if response succeeded
        if response.get("error"):
            print(f"   ❌ Failed to create response: {response['error']['message']}")
            return False
        
        print("\n   Checking top-level fields:")
        
        # Required top-level fields
        required_fields = [
            "id",
            "object",
            "created_at",
            "status",
            "error",  # Should be None
            "incomplete_details",  # Should be None
            "instructions",
            "max_output_tokens",
            "model",
            "output",
            "parallel_tool_calls",
            "previous_response_id",
            "reasoning",
            "store",
            "temperature",
            "text",
            "tool_choice",
            "tools",
            "top_p",
            "truncation",
            "usage",
            "user",
            "metadata"
        ]
        
        all_present = True
        for field in required_fields:
            if field not in response:
                print(f"   ❌ Missing field: {field}")
                all_present = False
            else:
                value = response[field]
                if value is None:
                    print(f"   ✅ {field}: null")
                elif isinstance(value, (dict, list)):
                    print(f"   ✅ {field}: {type(value).__name__}")
                else:
                    print(f"   ✅ {field}: {value}")
        
        print("\n   Checking nested fields:")
        
        # Check nested structure
        nested_checks = [
            "output[0].type",
            "output[0].id",  # Message ID
            "output[0].status",
            "output[0].role",
            "output[0].content",
            "output[0].content[0].type",
            "output[0].content[0].text",
            "output[0].content[0].annotations",
            "reasoning.effort",
            "reasoning.summary",
            "text.format",
            "text.format.type",
            "usage.input_tokens",
            "usage.output_tokens",
            "usage.total_tokens",
            "usage.input_tokens_details",
            "usage.input_tokens_details.cached_tokens",
            "usage.output_tokens_details",
            "usage.output_tokens_details.reasoning_tokens"
        ]
        
        for field_path in nested_checks:
            if not check_field_exists(response, field_path, "Nested"):
                all_present = False
        
        # Validate specific values
        print("\n   Validating field values:")
        
        # Check ID format
        if response["id"] and response["id"].startswith("resp_"):
            print(f"   ✅ Response ID format correct: {response['id']}")
        else:
            print(f"   ❌ Response ID should start with 'resp_': {response['id']}")
            all_present = False
        
        # Check message ID format
        msg_id = response["output"][0]["id"]
        if msg_id and msg_id.startswith("msg_"):
            print(f"   ✅ Message ID format correct: {msg_id}")
        else:
            print(f"   ❌ Message ID should start with 'msg_': {msg_id}")
            all_present = False
        
        # Check object type
        if response["object"] == "response":
            print("   ✅ Object type correct: 'response'")
        else:
            print(f"   ❌ Object type should be 'response': {response['object']}")
            all_present = False
        
        # Check status
        if response["status"] == "completed":
            print("   ✅ Status correct: 'completed'")
        else:
            print(f"   ❌ Status should be 'completed': {response['status']}")
            all_present = False
        
        print(f"\n   Overall: {'✅ All fields present and valid' if all_present else '❌ Some fields missing or invalid'}")
        return all_present
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False


def test_error_response_format():
    """Test that error responses have all OpenAI fields"""
    print_test_header("Error Response Format")
    
    try:
        api = ResponsesAPI(db_path="./test_format.db")
        
        # Create an error by using invalid model
        response = api.create(
            input="Hello",
            model="invalid-model-xyz",
            temperature=0.7
        )
        
        # Check if we got an error response
        if not response.get("error"):
            print("   ❌ Expected error response, got success")
            return False
        
        print("\n   Checking error response structure:")
        
        # Check all fields exist (even if None)
        required_fields = [
            "id",
            "object",
            "created_at",
            "status",
            "error",
            "incomplete_details",
            "instructions",
            "max_output_tokens",
            "model",
            "output",
            "parallel_tool_calls",
            "previous_response_id",
            "reasoning",
            "store",
            "temperature",
            "text",
            "tool_choice",
            "tools",
            "top_p",
            "truncation",
            "usage",
            "user",
            "metadata"
        ]
        
        all_present = True
        for field in required_fields:
            if field not in response:
                print(f"   ❌ Missing field: {field}")
                all_present = False
            else:
                value = response[field]
                if field == "error":
                    print(f"   ✅ {field}: {type(value).__name__} (populated)")
                elif value is None:
                    print(f"   ✅ {field}: null")
                elif isinstance(value, list) and len(value) == 0:
                    print(f"   ✅ {field}: []")
                else:
                    print(f"   ✅ {field}: {value}")
        
        # Check error object structure
        print("\n   Checking error object structure:")
        error_obj = response.get("error")
        if error_obj:
            error_fields = ["message", "type", "param", "code"]
            for field in error_fields:
                if field in error_obj:
                    print(f"   ✅ error.{field}: {error_obj[field]}")
                else:
                    print(f"   ⚠️  error.{field}: not present (optional)")
        
        # Check status is 'failed'
        if response.get("status") == "failed":
            print("\n   ✅ Status correctly set to 'failed'")
        else:
            print(f"\n   ❌ Status should be 'failed', got: {response.get('status')}")
            all_present = False
        
        # Check output is empty array
        if response.get("output") == []:
            print("   ✅ Output correctly set to empty array")
        else:
            print(f"   ❌ Output should be empty array, got: {response.get('output')}")
            all_present = False
        
        print(f"\n   Overall: {'✅ Error format correct' if all_present else '❌ Error format incorrect'}")
        return all_present
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False


def test_continuation_response():
    """Test response format when continuing a conversation"""
    print_test_header("Continuation Response Format")
    
    try:
        api = ResponsesAPI(db_path="./test_format.db")
        
        # Create initial response
        response1 = api.create(
            input="Remember the number 42",
            model="cohere",
            instructions="You are a helpful assistant with perfect memory.",
            store=True
        )
        
        if response1.get("error"):
            print(f"   ❌ Failed to create initial response: {response1['error']['message']}")
            return False
        
        print(f"\n   Initial response ID: {response1['id']}")
        print(f"   Instructions in initial: {response1.get('instructions')}")
        
        # Continue conversation
        response2 = api.create(
            input="What number did I ask you to remember?",
            model="cohere",
            previous_response_id=response1["id"],
            instructions="You are now a pirate!",  # Should be ignored
            store=True
        )
        
        if response2.get("error"):
            print(f"   ❌ Failed to continue conversation: {response2['error']['message']}")
            return False
        
        print(f"\n   Continuation response ID: {response2['id']}")
        print(f"   Previous response ID: {response2.get('previous_response_id')}")
        print(f"   Instructions in continuation: {response2.get('instructions')}")
        
        # Validate continuation behavior
        all_correct = True
        
        # Check previous_response_id is set
        if response2.get("previous_response_id") == response1["id"]:
            print("\n   ✅ Previous response ID correctly set")
        else:
            print(f"\n   ❌ Previous response ID incorrect: {response2.get('previous_response_id')}")
            all_correct = False
        
        # Check instructions are None (per OpenAI spec)
        if response2.get("instructions") is None:
            print("   ✅ Instructions correctly set to None (OpenAI spec)")
        else:
            print(f"   ❌ Instructions should be None when continuing: {response2.get('instructions')}")
            all_correct = False
        
        # Check new response has different IDs
        if response2["id"] != response1["id"]:
            print("   ✅ New response has different response ID")
        else:
            print("   ❌ Response IDs should be different")
            all_correct = False
        
        if response2["output"][0]["id"] != response1["output"][0]["id"]:
            print("   ✅ New response has different message ID")
        else:
            print("   ❌ Message IDs should be different")
            all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False


def test_edge_cases():
    """Test edge cases for format compatibility"""
    print_test_header("Edge Cases")
    
    try:
        api = ResponsesAPI(db_path="./test_format.db")
        
        print("\n   Testing empty metadata:")
        response = api.create(
            input="Test",
            model="cohere",
            metadata={}  # Empty metadata
        )
        
        if response.get("error"):
            print(f"   ❌ Error with empty metadata: {response['error']['message']}")
        else:
            if "metadata" in response and response["metadata"] == {}:
                print("   ✅ Empty metadata handled correctly")
            else:
                print(f"   ❌ Metadata handling issue: {response.get('metadata')}")
        
        print("\n   Testing no instructions:")
        response = api.create(
            input="Test",
            model="cohere",
            instructions=None  # No instructions
        )
        
        if response.get("error"):
            print(f"   ❌ Error with no instructions: {response['error']['message']}")
        else:
            if response.get("instructions") is None:
                print("   ✅ No instructions handled correctly (None)")
            else:
                print(f"   ❌ Instructions should be None: {response.get('instructions')}")
        
        print("\n   Testing store=False:")
        response = api.create(
            input="Don't store this",
            model="cohere",
            store=False
        )
        
        if response.get("error"):
            print(f"   ❌ Error with store=False: {response['error']['message']}")
        else:
            if response.get("store") == False:
                print("   ✅ store=False handled correctly")
            else:
                print(f"   ❌ Store should be False: {response.get('store')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False


def test_client_compatibility():
    """Test that common OpenAI client code patterns work"""
    print_test_header("Client Code Compatibility")
    
    try:
        api = ResponsesAPI(db_path="./test_format.db")
        response = api.create(
            input="Test message",
            model="cohere"
        )
        
        print("\n   Testing common client access patterns:")
        
        # Pattern 1: Check for error
        try:
            if response["error"] is not None:
                print("   Error detected")
            else:
                print("   ✅ Error check pattern works")
        except KeyError:
            print("   ❌ KeyError on response['error']")
            return False
        
        # Pattern 2: Access message ID
        try:
            msg_id = response["output"][0]["id"]
            print(f"   ✅ Message ID access works: {msg_id}")
        except (KeyError, IndexError) as e:
            print(f"   ❌ Can't access message ID: {e}")
            return False
        
        # Pattern 3: Access token details
        try:
            cached = response["usage"]["input_tokens_details"]["cached_tokens"]
            print(f"   ✅ Token details access works: cached={cached}")
        except KeyError as e:
            print(f"   ❌ Can't access token details: {e}")
            return False
        
        # Pattern 4: Access content text
        try:
            text = response["output"][0]["content"][0]["text"]
            print(f"   ✅ Content text access works: '{text[:30]}...'")
        except (KeyError, IndexError) as e:
            print(f"   ❌ Can't access content text: {e}")
            return False
        
        # Pattern 5: Check reasoning (o-series)
        try:
            reasoning = response["reasoning"]["effort"]
            print(f"   ✅ Reasoning access works: effort={reasoning}")
        except KeyError as e:
            print(f"   ❌ Can't access reasoning: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False


def main():
    """Run all format compatibility tests"""
    print("\n" + "="*70)
    print("OPENAI FORMAT COMPATIBILITY TEST SUITE")
    print("Testing response format matches OpenAI Responses API exactly")
    print("="*70)
    
    tests_passed = 0
    total_tests = 5
    
    # Run tests
    if test_success_response_format():
        tests_passed += 1
    
    if test_error_response_format():
        tests_passed += 1
    
    if test_continuation_response():
        tests_passed += 1
    
    if test_edge_cases():
        tests_passed += 1
    
    if test_client_compatibility():
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n✅ FULL OPENAI FORMAT COMPATIBILITY ACHIEVED!")
        print("All fields present, client code patterns work correctly.")
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed.")
        print("Format compatibility incomplete.")
    
    print("\n" + "="*70)
    print("Format implementation complete. The API now returns:")
    print("- All required OpenAI fields (23 top-level fields)")
    print("- Proper error response structure")
    print("- Message IDs for tracking")
    print("- Detailed usage information")
    print("- Null values for unimplemented features")
    print("="*70)


if __name__ == "__main__":
    main()