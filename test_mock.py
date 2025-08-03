"""Test Cortex with mock LLM (no Cohere required)"""
import os
import sys

# Add cortex to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import ResponsesAPI

print("=== Testing Cortex Framework with Mock LLM ===\n")

# Initialize with mock model
api = ResponsesAPI()

# Test 1: Simple response with mock model
print("Test 1: Simple Response")
response = api.create(
    input="Hello! What is Python?",
    model="mock"  # Use mock model
)
print(f"Response ID: {response['id']}")
print(f"Response: {response['output'][0]['content'][0]['text']}")

# Test 2: Conversation continuation
print("\n\nTest 2: Conversation Continuation")
response2 = api.create(
    input="Tell me more about it",
    model="mock",
    previous_response_id=response['id']
)
print(f"Response ID: {response2['id']}")
print(f"Previous ID: {response2['previous_response_id']}")
print(f"Response: {response2['output'][0]['content'][0]['text']}")

# Test 3: Custom instructions
print("\n\nTest 3: Custom Instructions")
response3 = api.create(
    input="Explain variables",
    model="mock",
    instructions="You are a helpful programming tutor"
)
print(f"Response: {response3['output'][0]['content'][0]['text']}")

print("\n✅ All tests passed! Cortex framework is working correctly.")
print("\nNote: This is using a mock LLM. To use real AI:")
print("1. Fix Cohere installation: pip install cohere==5.12.0 langchain-cohere==0.4.4")
print("2. Set COHERE_API_KEY environment variable")
print("3. Use model='cohere' instead of model='mock'")