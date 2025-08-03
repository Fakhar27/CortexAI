"""Simple test without pip install"""
import os
import sys

# Add cortex to Python path (temporary solution)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import
from cortex import ResponsesAPI

# Test it
print("Testing Cortex without pip install...")
api = ResponsesAPI()

response = api.create(input="Hello, what is Python?")
print(f"\nResponse: {response['output'][0]['content'][0]['text'][:100]}...")
print(f"Response ID: {response['id']}")
print("\n✅ It works!")