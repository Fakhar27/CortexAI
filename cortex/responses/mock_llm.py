"""Mock LLM for testing when Cohere is not available"""
from typing import List, Any
from langchain_core.messages import BaseMessage, AIMessage


class MockChatModel:
    """Mock chat model for testing"""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """Return a mock response"""
        # Get the last user message
        user_input = messages[-1].content if messages else "Hello"
        
        # Generate a mock response
        mock_response = f"This is a mock response to: '{user_input}'. The Cortex framework is working!"
        
        return AIMessage(content=mock_response)