"""Test store=True/False functionality"""
import os
import sys

# Add cortex to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex import ResponsesAPI

print("=== Testing Store Parameter ===\n")

# Initialize API
api = ResponsesAPI()

# Test 1: Create response with store=True
print("Test 1: Create with store=True")
response1 = api.create(
    input="My name is Alice",
    store=True
)
print(f"Response ID: {response1['id']}")
print(f"Store: {response1['store']}")
print(f"Response: {response1['output'][0]['content'][0]['text'][:100]}...")

# Test 2: Continue conversation with store=True
print("\n\nTest 2: Continue with store=True")
response2 = api.create(
    input="What's my name?",
    previous_response_id=response1['id'],
    store=True
)
if 'error' in response2:
    print(f"ERROR: {response2['error']}")
else:
    print(f"Response ID: {response2['id']}")
    print(f"Previous ID: {response2['previous_response_id']}")
    print(f"Response: {response2['output'][0]['content'][0]['text'][:200]}...")

# Test 3: Private query with store=False
print("\n\nTest 3: Private query with store=False")
response3 = api.create(
    input="I have a medical condition",
    previous_response_id=response2['id'] if 'id' in response2 else response1['id'],
    store=False  # Don't save this
)
if 'error' in response3:
    print(f"ERROR: {response3['error']}")
else:
    print(f"Response ID: {response3['id']}")
    print(f"Store: {response3['store']}")
    print(f"Response: {response3['output'][0]['content'][0]['text'][:100]}...")

# Test 4: Try to continue from store=False response (should error)
print("\n\nTest 4: Try to continue from store=False response")
response4 = api.create(
    input="Tell me more about that",
    previous_response_id=response3['id'] if 'id' in response3 else "resp_fake",
    store=True
)
if 'error' in response4:
    print(f"✅ Expected error: {response4['error']['message']}")
    print(f"   Error type: {response4['error']['type']}")
    print(f"   Error code: {response4['error']['code']}")
else:
    print(f"❌ Should have errored but got response: {response4['id']}")

# Test 5: One-off query with store=False (no previous_response_id)
print("\n\nTest 5: One-off query with store=False")
response5 = api.create(
    input="What is 2+2?",
    store=False
)
if 'error' in response5:
    print(f"ERROR: {response5['error']}")
else:
    print(f"Response ID: {response5['id']}")
    print(f"Store: {response5['store']}")
    print(f"Response: {response5['output'][0]['content'][0]['text'][:100]}...")

print("\n✅ Store parameter tests completed!")