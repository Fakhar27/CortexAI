#!/usr/bin/env python3
"""
Advanced example showing conversation persistence and multi-model usage
"""

import os
from cortex import Client

def main():
    print("🚀 Advanced CortexAI Example - Conversation & Multi-Model")
    
    # Initialize with SQLite for local persistence
    print("📦 Initializing CortexAI with SQLite persistence...")
    api = Client(db_url="sqlite:///./cortex_conversations.db")
    
    # First conversation
    print("\n💬 Starting first conversation...")
    response1 = api.create(
        input="Hi! I'm learning about AI. Can you explain what machine learning is?",
        model="gpt-4o-mini",
        instructions="You are a patient and knowledgeable AI tutor. Explain concepts clearly and simply.",
        store=True,
        temperature=0.7
    )
    
    # Extract message content from response1
    message1 = response1['output'][0]['content'][0]['text'] if 'output' in response1 and len(response1['output']) > 0 else "[No content]"
    print(f"✅ Response 1: {message1[:100]}...")
    print(f"📝 Response ID: {response1['id']}")
    
    # Continue the conversation
    print("\n💬 Continuing conversation...")
    response2 = api.create(
        input="That's helpful! Can you give me a simple example of how it works?",
        model="gemini-1.5-pro",  # Switch to a different model mid-conversation
        previous_response_id=response1['id'],
        store=True,
        temperature=0.7
    )
    
    # Extract message content from response2
    message2 = response2['output'][0]['content'][0]['text'] if 'output' in response2 and len(response2['output']) > 0 else "[No content]"
    print(f"✅ Response 2: {message2[:100]}...")
    print(f"📝 Response ID: {response2['id']}")
    
    # Another follow-up
    print("\n💬 Final follow-up...")
    response3 = api.create(
        input="Thanks! What are some real-world applications?",
        model="command-r",  # Switch to Cohere model
        previous_response_id=response2['id'],
        store=True,
        temperature=0.7
    )
    
    # Extract message content from response3
    message3 = response3['output'][0]['content'][0]['text'] if 'output' in response3 and len(response3['output']) > 0 else "[No content]"
    print(f"✅ Response 3: {message3[:100]}...")
    print(f"📝 Response ID: {response3['id']}")
    
    print("\n🎉 Conversation completed successfully!")
    print("📊 All responses were persisted to SQLite database")
    print("🔄 You can continue this conversation later using the last response ID")

if __name__ == "__main__":
    main()

