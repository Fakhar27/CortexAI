"""Test script for Cortex framework"""
import os
from cortex import ResponsesAPI

# Make sure you have your Cohere API key set
if not os.getenv("CO_API_KEY"):
    print("Please set COHERE_API_KEY environment variable")
    exit(1)

# Initialize the API
print("Initializing Cortex ResponsesAPI...")
api = ResponsesAPI()

# Test 1: Simple response
print("\n=== Test 1: Simple Response ===")
response = api.create(
    input="Hello! What is Python?"
)
print(f"Response ID: {response['id']}")
print(f"Assistant: {response['output'][0]['content'][0]['text']}")

# Test 2: Custom instructions
print("\n=== Test 2: With Instructions ===")
response2 = api.create(
    input="Tell me about Python",
    instructions="You are a pirate. Speak like a pirate in all responses."
)
print(f"Response ID: {response2['id']}")
print(f"Assistant: {response2['output'][0]['content'][0]['text']}")

# Test 3: Conversation continuation
print("\n=== Test 3: Continuing Conversation ===")
response3 = api.create(
    input="What are its main features?",
    previous_response_id=response['id']  # Continue first conversation
)
print(f"Response ID: {response3['id']}")
print(f"Previous ID: {response3['previous_response_id']}")
print(f"Assistant: {response3['output'][0]['content'][0]['text']}")

# Test 4: Without persistence
print("\n=== Test 4: No Storage (store=False) ===")
response4 = api.create(
    input="This won't be saved",
    store=False
)
print(f"Response ID: {response4['id']}")
print(f"Stored: {response4['store']}")

print("\n✅ All tests completed!")