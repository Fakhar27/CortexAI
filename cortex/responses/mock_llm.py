"""Mock LLM for testing when providers are not installed"""
from typing import Any, List, Optional, Dict
from langchain_core.messages import AIMessage, BaseMessage


class MockChatModel:
    """
    Mock chat model that mimics LangChain chat model interface
    Used when actual provider libraries are not installed
    """
    
    def __init__(self, **kwargs):
        """Initialize mock with any parameters"""
        self.model = kwargs.get("model_name", "mock-model")
        self.temperature = kwargs.get("temperature", 0.7)
        self.config = kwargs
    
    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """
        Mock invoke method that returns a simple response
        
        Args:
            messages: List of messages (ignored in mock)
            **kwargs: Additional parameters (ignored)
            
        Returns:
            AIMessage with mock content
        """
        # Return a mock response indicating which provider would be used
        provider = self.config.get("provider", "unknown")
        model_name = self.config.get("model_name", self.model)
        
        mock_content = (
            f"Mock response from {provider} provider using {model_name}. "
            f"Install the appropriate package to use real LLM:\n"
            f"- OpenAI: pip install langchain-openai\n"
            f"- Google: pip install langchain-google-genai\n"
            f"- Cohere: pip install langchain-cohere"
        )
        
        return AIMessage(content=mock_content)
    
    def __call__(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Support calling the model directly"""
        return self.invoke(messages, **kwargs)
    
    def bind(self, **kwargs) -> "MockChatModel":
        """Mock bind method for compatibility"""
        # Create new instance with merged config
        new_config = {**self.config, **kwargs}
        return MockChatModel(**new_config)
    
    async def ainvoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Mock async invoke for compatibility"""
        return self.invoke(messages, **kwargs)
    
    def stream(self, messages: List[BaseMessage], **kwargs):
        """Mock streaming for compatibility"""
        # Yield the response in chunks to simulate streaming
        response = self.invoke(messages, **kwargs)
        for word in response.content.split():
            yield AIMessage(content=word + " ")
    
    async def astream(self, messages: List[BaseMessage], **kwargs):
        """Mock async streaming for compatibility"""
        response = self.invoke(messages, **kwargs)
        for word in response.content.split():
            yield AIMessage(content=word + " ")
    
    def get_num_tokens(self, text: str) -> int:
        """Mock token counting"""
        # Simple approximation: 1 token per 4 characters
        return len(text) // 4
    
    def __repr__(self) -> str:
        """String representation"""
        return f"MockChatModel(model={self.model}, temperature={self.temperature})"