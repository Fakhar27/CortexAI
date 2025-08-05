#!/usr/bin/env python3
"""
Test the transaction fix for rapid/concurrent requests
Verifies the two-key solution prevents transaction conflicts
"""

import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import ResponsesAPI


def make_request(api, request_id):
    """Make a single request and return result"""
    try:
        start_time = time.time()
        response = api.create(
            input=f"Request {request_id}: What is {request_id} + {request_id}?",
            metadata={"request_id": str(request_id)}
        )
        elapsed = time.time() - start_time
        
        if "error" in response:
            return f"Request {request_id}: ERROR - {response['error']['message']} ({elapsed:.2f}s)"
        else:
            return f"Request {request_id}: SUCCESS - {response['id']} ({elapsed:.2f}s)"
    except Exception as e:
        elapsed = time.time() - start_time
        return f"Request {request_id}: EXCEPTION - {str(e)} ({elapsed:.2f}s)"


def test_rapid_sequential_requests(api, count=5):
    """Test rapid sequential requests"""
    print(f"\n{'='*60}")
    print(f"Test: Rapid Sequential Requests ({count} requests)")
    print('='*60)
    
    results = []
    for i in range(count):
        result = make_request(api, i+1)
        print(f"   {result}")
        results.append(result)
    
    # Count successes and failures
    successes = sum(1 for r in results if "SUCCESS" in r)
    errors = sum(1 for r in results if "ERROR" in r or "EXCEPTION" in r)
    
    print(f"\nResults: {successes} successes, {errors} errors")
    return errors == 0


def test_concurrent_requests(api, count=5):
    """Test truly concurrent requests using threads"""
    print(f"\n{'='*60}")
    print(f"Test: Concurrent Requests ({count} simultaneous)")
    print('='*60)
    
    with ThreadPoolExecutor(max_workers=count) as executor:
        # Submit all requests at once
        futures = [executor.submit(make_request, api, i+1) for i in range(count)]
        
        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            result = future.result()
            print(f"   {result}")
            results.append(result)
    
    # Count successes and failures
    successes = sum(1 for r in results if "SUCCESS" in r)
    errors = sum(1 for r in results if "ERROR" in r or "EXCEPTION" in r)
    
    print(f"\nResults: {successes} successes, {errors} errors")
    return errors == 0


def test_mixed_store_requests(api):
    """Test mixing store=True and store=False requests"""
    print(f"\n{'='*60}")
    print("Test: Mixed Store Requests (True/False/True)")
    print('='*60)
    
    # Create with store=True
    response1 = api.create(input="Store this message", store=True)
    if "error" in response1:
        print(f"   Request 1 (store=True): ERROR - {response1['error']['message']}")
        return False
    print(f"   Request 1 (store=True): SUCCESS - {response1['id']}")
    
    # Create with store=False
    response2 = api.create(input="Don't store this", store=False)
    if "error" in response2:
        print(f"   Request 2 (store=False): ERROR - {response2['error']['message']}")
        return False
    print(f"   Request 2 (store=False): SUCCESS - {response2['id']}")
    
    # Create with store=True again
    response3 = api.create(input="Store this too", store=True)
    if "error" in response3:
        print(f"   Request 3 (store=True): ERROR - {response3['error']['message']}")
        return False
    print(f"   Request 3 (store=True): SUCCESS - {response3['id']}")
    
    print("\nAll mixed store requests succeeded!")
    return True


def test_conversation_continuity(api):
    """Test continuing conversations with rapid requests"""
    print(f"\n{'='*60}")
    print("Test: Conversation Continuity with Rapid Requests")
    print('='*60)
    
    # Start conversation
    response1 = api.create(input="My name is TestBot", store=True)
    if "error" in response1:
        print(f"   Initial: ERROR - {response1['error']['message']}")
        return False
    print(f"   Initial: SUCCESS - {response1['id']}")
    
    # Rapid continuations
    prev_id = response1['id']
    for i in range(3):
        response = api.create(
            input=f"Question {i+1}: What's my name?",
            previous_response_id=prev_id,
            store=True
        )
        if "error" in response:
            print(f"   Continuation {i+1}: ERROR - {response['error']['message']}")
            return False
        print(f"   Continuation {i+1}: SUCCESS - {response['id']}")
        prev_id = response['id']
    
    print("\nAll continuations succeeded!")
    return True


def test_stress_test(api, duration_seconds=5):
    """Stress test with continuous requests for N seconds"""
    print(f"\n{'='*60}")
    print(f"Test: Stress Test ({duration_seconds} seconds of continuous requests)")
    print('='*60)
    
    start_time = time.time()
    request_count = 0
    success_count = 0
    error_count = 0
    
    while time.time() - start_time < duration_seconds:
        request_count += 1
        response = api.create(input=f"Stress test request {request_count}")
        
        if "error" in response:
            error_count += 1
            if error_count <= 3:  # Only print first 3 errors
                print(f"   Error {error_count}: {response['error']['message']}")
        else:
            success_count += 1
    
    elapsed = time.time() - start_time
    requests_per_second = request_count / elapsed
    
    print(f"\nResults in {elapsed:.1f} seconds:")
    print(f"   Total requests: {request_count}")
    print(f"   Successes: {success_count}")
    print(f"   Errors: {error_count}")
    print(f"   Requests/second: {requests_per_second:.1f}")
    
    return error_count == 0


def main():
    """Run all transaction tests"""
    print("=== TRANSACTION FIX TEST SUITE ===")
    print("Testing the two-key solution for concurrent requests")
    
    # Initialize API
    api = ResponsesAPI()
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Rapid sequential requests
    if test_rapid_sequential_requests(api):
        tests_passed += 1
        print("✅ Rapid sequential requests: PASSED")
    else:
        print("❌ Rapid sequential requests: FAILED")
    
    # Test 2: Concurrent requests
    if test_concurrent_requests(api):
        tests_passed += 1
        print("✅ Concurrent requests: PASSED")
    else:
        print("❌ Concurrent requests: FAILED")
    
    # Test 3: Mixed store requests
    if test_mixed_store_requests(api):
        tests_passed += 1
        print("✅ Mixed store requests: PASSED")
    else:
        print("❌ Mixed store requests: FAILED")
    
    # Test 4: Conversation continuity
    if test_conversation_continuity(api):
        tests_passed += 1
        print("✅ Conversation continuity: PASSED")
    else:
        print("❌ Conversation continuity: FAILED")
    
    # Test 5: Brief stress test
    if test_stress_test(api, duration_seconds=3):
        tests_passed += 1
        print("✅ Stress test: PASSED")
    else:
        print("❌ Stress test: FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n✅ All transaction tests passed!")
        print("The two-key solution successfully prevents transaction conflicts.")
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed.")
        print("The transaction fix may need further investigation.")
    
    # Cleanup note
    print("\nNote: Remember to implement proper connection cleanup in production!")


if __name__ == "__main__":
    main()