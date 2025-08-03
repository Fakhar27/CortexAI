"""LLM selection and configuration for Responses API"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from langchain_cohere import ChatCohere
    COHERE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Cohere not available: {e}")
    COHERE_AVAILABLE = False
    from .mock_llm import MockChatModel as ChatCohere

# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from cortex.models.registry import MODELS


def get_llm(model_str: str):
    """
    Get configured LLM instance based on model string
    
    Args:
        model_str: Model identifier (e.g., "cohere", "gpt-4")
        
    Returns:
        Configured LangChain chat model instance
        
    Raises:
        ValueError: If model not found or provider not supported
    """
    
    
    if model_str not in MODELS:
        raise ValueError(f"Model '{model_str}' not found in registry")
    
    config = MODELS[model_str]
    
    match config["provider"]:
        case "cohere":
            if not COHERE_AVAILABLE:
                print("Warning: Cohere not available, using mock LLM")
                return ChatCohere(**config)
            return ChatCohere(
                model=config["model_name"],
                temperature=config.get("temperature", 0.7)
            )
        case "mock":
            from .mock_llm import MockChatModel
            return MockChatModel(**config)
        # case "openai":
        #     return ChatOpenAI(
        #         model=config["model_name"],
        #         temperature=config.get("temperature", 0.7)
        #     )
        # case "anthropic":
        #     return ChatAnthropic(
        #         model=config["model_name"],
        #         temperature=config.get("temperature", 0.7)
        #     )
        case _:
            raise ValueError(f"Provider '{config['provider']}' not supported yet")