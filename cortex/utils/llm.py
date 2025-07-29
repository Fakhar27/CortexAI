"""LLM provider utilities"""
from typing import Any
from langchain_cohere import ChatCohere
from langchain_core.language_models import BaseChatModel


def get_llm(provider: str = "cohere", **kwargs) -> BaseChatModel:
    """
    Get LLM instance based on provider
    
    Args:
        provider: LLM provider name (cohere, openai, etc.)
        **kwargs: Additional arguments for the LLM
    
    Returns:
        LLM instance
    """
    if provider == "cohere":
        # Free Cohere API
        return ChatCohere(
            model="command-r-plus",
            temperature=0.7,
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")