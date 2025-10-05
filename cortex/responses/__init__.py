"""Responses package exports client API and ASGI app."""

from .api import ResponsesAPI

try:  # Expose ASGI app for thin servers
    from .server import app as app
except Exception:  # pragma: no cover - optional
    app = None  # type: ignore

# Convenience alias
Client = ResponsesAPI

__version__ = "0.1.0"
__all__ = ["ResponsesAPI", "Client", "app"]
