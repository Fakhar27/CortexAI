"""LLM selection and configuration for Responses API"""
from langchain_cohere import ChatCohere
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
            return ChatCohere(
                model=config["model_name"],
                temperature=config.get("temperature", 0.7)
            )
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