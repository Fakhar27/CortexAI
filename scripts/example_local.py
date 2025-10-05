#!/usr/bin/env python3
"""
Simple example script to test CortexAI locally
"""

import os
from cortex import Client

def main():
    print("🚀 Testing CortexAI locally...")
    
    # Initialize the client (will use in-memory storage by default)
    print("📦 Initializing CortexAI client...")
    api = Client()
    
    # Test with a simple message
    print("💬 Creating a test response...")
    
    try:
        response = api.create(
            input="Hello! Can you tell me a short joke?",
            model="gpt-4o-mini",  # Using a cost-effective model
            instructions="You are a helpful assistant that tells clean, family-friendly jokes.",
            store=True,
            temperature=0.7
        )
        
        print("✅ Success! Response received:")
        print(f"📝 Response ID: {response['id']}")
        print(f"🤖 Model: {response['model']}")
        
        # Extract message content from the response structure
        if 'output' in response and len(response['output']) > 0:
            message_content = response['output'][0]['content'][0]['text']
            print(f"💭 Message: {message_content}")
        else:
            print("💭 Message: [No content found]")
            
        print(f"📊 Usage: {response['usage']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you have set your API keys as environment variables:")
        print("   export OPENAI_API_KEY='your-openai-key'")
        print("   export GOOGLE_API_KEY='your-google-key'")
        print("   export CO_API_KEY='your-cohere-key'")
        print("2. Check that you have internet connectivity")
        print("3. Verify your API keys are valid and have sufficient credits")

if __name__ == "__main__":
    main()

