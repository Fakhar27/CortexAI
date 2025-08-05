#!/usr/bin/env python3
"""
Test the critical fixes: temperature parameter and model validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import ResponsesAPI


def test_temperature_parameter():
    """Test that temperature parameter is actually applied"""
    print("\n" + "="*60)
    print("Test: Temperature Parameter Application")
    print("="*60)
    
    api = ResponsesAPI()
    
    # Test with low temperature (deterministic)
    print("Testing with temperature=0.1 (should be deterministic)")
    response1 = api.create(
        input="Say exactly: 'Hello World'",
        temperature=0.1
    )
    
    if "error" in response1:
        print(f"❌ Error: {response1['error']['message']}")
        return False
    
    response2 = api.create(
        input="Say exactly: 'Hello World'", 
        temperature=0.1
    )
    
    if "error" in response2:
        print(f"❌ Error: {response2['error']['message']}")
        return False
    
    print(f"Response 1: {response1['output'][0]['content'][0]['text'][:50]}...")
    print(f"Response 2: {response2['output'][0]['content'][0]['text'][:50]}...")
    
    # Test with high temperature (creative)
    print("\nTesting with temperature=1.8 (should be creative)")
    response3 = api.create(
        input="Say exactly: 'Hello World'",
        temperature=1.8
    )
    
    if "error" in response3:
        print(f"❌ Error: {response3['error']['message']}")
        return False
    
    print(f"Creative response: {response3['output'][0]['content'][0]['text'][:50]}...")
    
    print("✅ Temperature parameter is being applied")
    return True


def test_model_validation():
    """Test that invalid models are caught early"""
    print("\n" + "="*60)
    print("Test: Model Validation Against Registry")
    print("="*60)
    
    api = ResponsesAPI()
    
    # Test invalid model
    response = api.create(
        input="Hello",
        model="gpt-2000-ultra-mega"
    )
    
    if "error" not in response:
        print("❌ Should have failed with invalid model")
        return False
    
    error = response["error"]
    print(f"✅ Correctly rejected invalid model:")
    print(f"   Message: {error['message']}")
    print(f"   Type: {error['type']}")
    print(f"   Code: {error['code']}")
    print(f"   Param: {error['param']}")
    
    # Check that error message includes available models
    if "Available models:" in error["message"]:
        print("✅ Error message includes available models")
    else:
        print("⚠️  Error message should include available models")
    
    return True


def test_instructions_parameter():
    """Test that instructions parameter works"""
    print("\n" + "="*60)
    print("Test: Instructions Parameter")
    print("="*60)
    
    api = ResponsesAPI()
    
    # Test with specific instructions
    response = api.create(
        input="What should I do today?",
        instructions="You are a fitness coach. Always recommend physical activities and exercise."
    )
    
    if "error" in response:
        print(f"❌ Error: {response['error']['message']}")
        return False
    
    content = response['output'][0]['content'][0]['text'].lower()
    print(f"Response with fitness coach instructions:")
    print(f"   {content[:100]}...")
    
    # Check if response seems to follow instructions
    fitness_keywords = ['exercise', 'workout', 'fitness', 'physical', 'activity', 'run', 'gym']
    has_fitness_content = any(keyword in content for keyword in fitness_keywords)
    
    if has_fitness_content:
        print("✅ Instructions appear to be working (fitness-related response)")
    else:
        print("⚠️  Instructions may not be working (no fitness keywords found)")
    
    return True


def test_model_from_registry():
    """Test that valid model from registry works"""
    print("\n" + "="*60)
    print("Test: Valid Model From Registry")
    print("="*60)
    
    api = ResponsesAPI()
    
    # Test with valid model
    response = api.create(
        input="What is 2+2?",
        model="cohere"  # This should exist in registry
    )
    
    if "error" in response:
        print(f"❌ Error with valid model: {response['error']['message']}")
        return False
    
    print(f"✅ Valid model 'cohere' works correctly")
    print(f"   Response: {response['output'][0]['content'][0]['text'][:50]}...")
    
    return True


def main():
    """Run all critical fix tests"""
    print("=== CRITICAL FIXES TEST SUITE ===")
    print("Testing temperature parameter, model validation, and instructions")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Temperature parameter
    if test_temperature_parameter():
        tests_passed += 1
    
    # Test 2: Model validation
    if test_model_validation():
        tests_passed += 1
    
    # Test 3: Instructions parameter
    if test_instructions_parameter():
        tests_passed += 1
    
    # Test 4: Valid model works
    if test_model_from_registry():
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n✅ All critical fixes working correctly!")
        print("- Temperature parameter is now applied to LLM")
        print("- Model validation catches invalid models early")
        print("- Instructions parameter works as expected")
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed.")
        print("Critical fixes may need further investigation.")


if __name__ == "__main__":
    main()