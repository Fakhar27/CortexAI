"""Model registry containing all supported LLM configurations"""

import warnings

MODELS = {
    # OpenAI Models
    "gpt-4o": {
        "provider": "openai",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4096,
        "api_key_env": "OPENAI_API_KEY"
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 16384,
        "api_key_env": "OPENAI_API_KEY"
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "OPENAI_API_KEY"
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 16384,
        "api_key_env": "OPENAI_API_KEY"
    },
    
    # Google Gemini Models
    "gemini-1.5-flash": {
        "provider": "google",
        "model_name": "gemini-1.5-flash",
        "temperature": 0.7,
        "max_tokens": 1048576,
        "api_key_env": "GOOGLE_API_KEY"
    },
    "gemini-1.5-pro": {
        "provider": "google",
        "model_name": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 2097152,
        "api_key_env": "GOOGLE_API_KEY"
    },
    "gemini-1.0-pro": {
        "provider": "google",
        "model_name": "gemini-1.0-pro",
        "temperature": 0.7,
        "max_tokens": 32768,
        "api_key_env": "GOOGLE_API_KEY"
    },
    
    # Cohere Models (Updated September 2024)
    "command-r-08-2024": {
        "provider": "cohere",
        "model_name": "command-r-08-2024",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY"
    },
    "command-r-plus-08-2024": {
        "provider": "cohere",
        "model_name": "command-r-plus-08-2024",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY"
    },
    "command-a-03-2025": {
        "provider": "cohere",
        "model_name": "command-a-03-2025",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY"
    },
    
    # Anthropic Claude Models
    "claude-3-opus": {
        "provider": "anthropic",
        "model_name": "claude-3-opus-20240229",
        "temperature": 0.7,
        "max_tokens": 200000,
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "claude-3-sonnet": {
        "provider": "anthropic",
        "model_name": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 200000,
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "claude-3-haiku": {
        "provider": "anthropic",
        "model_name": "claude-3-haiku-20240307",
        "temperature": 0.7,
        "max_tokens": 200000,
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    
    # Deprecated models - kept for backward compatibility
    "command-r": {
        "provider": "cohere",
        "model_name": "command-r-08-2024",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY",
        "_deprecated": True,
        "_replacement": "command-r-08-2024"
    },
    "command-r-plus": {
        "provider": "cohere",
        "model_name": "command-r-plus-08-2024",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY",
        "_deprecated": True,
        "_replacement": "command-r-plus-08-2024"
    },
    "command": {
        "provider": "cohere",
        "model_name": "command-a-03-2025",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY",
        "_deprecated": True,
        "_replacement": "command-a-03-2025"
    },
    "cohere": {
        "provider": "cohere",
        "model_name": "command-r-08-2024",
        "temperature": 0.7,
        "max_tokens": 128000,
        "api_key_env": "CO_API_KEY",
        "_deprecated": True,
        "_replacement": "command-r-08-2024"
    }
}

def get_model_config(model_str: str) -> dict:
    """
    Get model configuration with deprecation warnings
    
    Args:
        model_str: Model identifier
        
    Returns:
        Model configuration dict
        
    Raises:
        ValueError: If model not found
    """
    if model_str not in MODELS:
        available = [m for m in MODELS.keys() if not MODELS[m].get("_deprecated")]
        raise ValueError(
            f"Model '{model_str}' not found. Available models: {', '.join(sorted(available))}"
        )
    
    config = MODELS[model_str].copy()
    
    # Handle deprecated models
    if config.get("_deprecated"):
        replacement = config.get("_replacement", "command-r")
        warnings.warn(
            f"Model '{model_str}' is deprecated and will be removed in v2.0. "
            f"Please use '{replacement}' instead.",
            DeprecationWarning,
            stacklevel=2
        )
    
    return config

def list_available_models() -> list:
    """
    List all available models with their configuration status
    
    Returns:
        List of model information dicts
    """
    import os
    models = []
    
    for model_id, config in MODELS.items():
        # Skip deprecated aliases in listing
        if config.get("_deprecated"):
            continue
            
        api_key_env = config.get("api_key_env")
        is_configured = bool(os.getenv(api_key_env)) if api_key_env else True
        
        models.append({
            "model": model_id,
            "provider": config["provider"],
            "configured": is_configured,
            "requires": api_key_env,
            "max_tokens": config.get("max_tokens", "N/A")
        })
    
    return sorted(models, key=lambda x: (x["provider"], x["model"]))