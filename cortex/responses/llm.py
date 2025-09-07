"""LLM selection and configuration for Responses API"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_cohere import ChatCohere
    COHERE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Cohere not available: {e}")
    COHERE_AVAILABLE = False
    ChatCohere = None

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenAI not available: {e}")
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Google Gemini not available: {e}")
    GOOGLE_AVAILABLE = False
    ChatGoogleGenerativeAI = None

from cortex.models.registry import get_model_config

ERROR_MAPPINGS = {
    "openai": {
        "rate_limit": ["rate_limit_exceeded", "429", "rate limit"],
        "auth": ["invalid_api_key", "401", "unauthorized", "authentication"],
        "model": ["model_not_found", "404", "does not exist"],
        "context": ["context_length_exceeded", "maximum context", "too many tokens"]
    },
    "google": {
        "rate_limit": ["RESOURCE_EXHAUSTED", "quota", "rate limit"],
        "auth": ["UNAUTHENTICATED", "401", "api key"],
        "model": ["NOT_FOUND", "404", "model not found"],
        "context": ["INVALID_ARGUMENT", "too long", "exceeds maximum"]
    },
    "cohere": {
        "rate_limit": ["rate limit", "too many requests", "quota"],
        "auth": ["CO_API_KEY", "unauthorized", "invalid api key"],
        "model": ["model not found", "invalid model"],
        "context": ["too many tokens", "context too long", "exceeds limit"]
    }
}

def validate_api_key(provider: str, api_key_env: str) -> None:
    """
    Validate that required API key is present
    
    Args:
        provider: Provider name
        api_key_env: Environment variable name for API key
        
    Raises:
        ValueError: If API key is missing
    """
    if api_key_env and not os.getenv(api_key_env):
        provider_help = {
            "openai": "Get your API key from https://platform.openai.com/api-keys",
            "google": "Get your API key from https://makersuite.google.com/app/apikey",
            "cohere": "Get your API key from https://dashboard.cohere.com/api-keys"
        }
        
        help_url = provider_help.get(provider, "")
        raise ValueError(
            f"Missing API key for {provider}.\n"
            f"Set {api_key_env} in your environment or .env file.\n"
            f"{help_url}"
        )

def handle_llm_error(error: Exception, provider: str) -> dict:
    """
    Map provider-specific errors to standardized format
    
    Args:
        error: The exception raised
        provider: The provider that raised it
        
    Returns:
        Standardized error response dict
    """
    error_str = str(error).lower()
    mappings = ERROR_MAPPINGS.get(provider, {})
    
    for error_type, patterns in mappings.items():
        if any(p.lower() in error_str for p in patterns):
            messages = {
                "rate_limit": "API rate limit exceeded. Please wait before retrying.",
                "auth": f"Authentication failed. Check your {provider.upper()} API key.",
                "model": f"Model not found or not available for your {provider} account.",
                "context": "Input exceeds maximum context length for this model."
            }
            return {
                "error_type": error_type,
                "message": messages.get(error_type, str(error)),
                "provider": provider,
                "original_error": str(error)
            }
    
    return {
        "error_type": "unknown",
        "message": f"An error occurred with {provider}: {str(error)}",
        "provider": provider,
        "original_error": str(error)
    }

def get_llm(model_str: str, temperature: float = None):
    """
    Get configured LLM instance based on model string
    
    Args:
        model_str: Model identifier (e.g., "gpt-4o-mini", "gemini-1.5-flash", "command-r")
        temperature: Override temperature (if None, uses registry default)
        
    Returns:
        Configured LangChain chat model instance
        
    Raises:
        ValueError: If model not found or provider not supported
    """
    config = get_model_config(model_str)
    
    api_key_env = config.get("api_key_env")
    if api_key_env:
        validate_api_key(config["provider"], api_key_env)
    
    final_temperature = temperature if temperature is not None else config.get("temperature", 0.7)
    
    match config["provider"]:
        case "openai":
            if not OPENAI_AVAILABLE:
                raise ValueError(f"OpenAI provider not available for model '{model_str}'. Install with: pip install langchain-openai")
            
            return ChatOpenAI(
                model=config["model_name"],
                temperature=final_temperature,
                max_tokens=config.get("max_tokens"),
                api_key=os.getenv(api_key_env)
            )
            
        case "google":
            if not GOOGLE_AVAILABLE:
                raise ValueError(f"Google provider not available for model '{model_str}'. Install with: pip install langchain-google-genai")
            
            return ChatGoogleGenerativeAI(
                model=config["model_name"],
                temperature=final_temperature,
                max_output_tokens=config.get("max_tokens"),
                google_api_key=os.getenv(api_key_env)
            )
            
        case "cohere":
            if not COHERE_AVAILABLE:
                raise ValueError(f"Cohere provider not available for model '{model_str}'. Install with: pip install langchain-cohere")
            
            return ChatCohere(
                model=config["model_name"],
                temperature=final_temperature,
                max_tokens=config.get("max_tokens"),
                cohere_api_key=os.getenv(api_key_env)
            )
            
        case _:
            raise ValueError(f"Provider '{config['provider']}' not supported yet")