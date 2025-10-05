#!/usr/bin/env python3
"""
Thin server wrapper for CortexAI.

This demo script does not implement endpoints — it simply imports the
ASGI `app` exposed by `cortex.responses` and runs it. All functionality
lives in the core package (e.g., `/chat`, `/chat/stream`, `/models`, etc.).
"""

import os
import uvicorn

from cortex.responses import app  # noqa: F401


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("cortex.responses:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
