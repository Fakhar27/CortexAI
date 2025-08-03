"""Debug the import issue"""
import os
import sys

# Add cortex to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports step by step...")

try:
    print("1. Importing BaseMessage...")
    from langchain_core.messages import BaseMessage, add_messages
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("2. Importing HumanMessage...")
    from langchain_core.messages import HumanMessage
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("3. Importing ResponsesState...")
    from cortex.responses.state import ResponsesState
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("4. Importing ResponsesAPI...")
    from cortex import ResponsesAPI
    print("   ✓ Success")
    
    print("\n5. Creating API instance...")
    api = ResponsesAPI()
    print("   ✓ Success")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()