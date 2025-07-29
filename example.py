"""Example usage of Cortex ResponsesAPI"""
from cortex import ResponsesAPI

# Initialize the API (you'll need a Cohere API key)
api = ResponsesAPI(llm_provider="cohere")

# Create a response
print("First message:")
response = api.create(
    input="What is Python?",
    instructions="You are a helpful programming tutor. Keep responses concise."
)
print(f"Assistant: {response['message']['content']}")
print(f"Conversation ID: {response['conversation_id']}")

# Continue the conversation
print("\nSecond message:")
response2 = api.create(
    input="What are decorators?",
    previous_response_id=response["conversation_id"]
)
print(f"Assistant: {response2['message']['content']}")

# Start a new conversation with different instructions
print("\nNew conversation:")
response3 = api.create(
    input="I'm feeling stressed about my job",
    instructions="You are a supportive career coach. Be empathetic and helpful."
)
print(f"Assistant: {response3['message']['content']}")