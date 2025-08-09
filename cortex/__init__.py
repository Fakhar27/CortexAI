"""Cortex - Open-source alternative to OpenAI APIs"""

from .responses.api import ResponsesAPI

# Convenience alias for better UX
Client = ResponsesAPI

__version__ = "0.1.0"
__all__ = ["ResponsesAPI", "Client"]