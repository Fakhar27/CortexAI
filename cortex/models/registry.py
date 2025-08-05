"""Model registry containing all supported LLM configurations"""

MODELS = {
    "cohere": {
        "provider": "cohere",
        "model_name": "command-r",
        "temperature": 0.7
    },
    # Future models can be added here:
    # "gpt-4": {
    #     "provider": "openai",
    #     "model_name": "gpt-4",
    #     "temperature": 0.7
    # },
    # "claude": {
    #     "provider": "anthropic", 
    #     "model_name": "claude-3-sonnet",
    #     "temperature": 0.7
    # }
}