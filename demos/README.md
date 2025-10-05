# 🎬 CortexAI Demo Apps (REST‑only)

These demo apps showcase the CortexAI REST API. They are independent clients that talk over HTTP only — no direct Python imports from the core package.

## Contents

- `chat_ui/` — Modern Material 3 chat interface
  - File: `demos/chat_ui/index.html`
  - Open directly in your browser (no build step)
  - Default Server URL: `http://localhost:8000`

- `server/` — REST API Docker launcher
  - File: `demos/server/run_server.py`
  - Starts the official Cortex REST container locally

- `cli/` — Interactive terminal client
  - File: `demos/cli/cortex_cli.py`
  - Rich CLI with history, models, and settings

---

## Quick Start

1) Start the REST API (Docker)
```bash
python demos/server/run_server.py
```

2) Open the Chat UI
```bash
open demos/chat_ui/index.html
# or double‑click the file
```

3) Try the CLI
```bash
python demos/cli/cortex_cli.py
```

---

## Chat UI — Feature Tour

Overview (desktop)

![Chat UI overview](chat_ui/screens/overview-desktop.png)

What you see:
- Sidebar (left): conversation history with server‑generated titles and message counts.
- Top bar: brand, model picker, and dark‑mode toggle.
- Messages: assistant (left) and user (right) bubbles with compact spacing.
- Input: textarea + send button; status line centered under the input.
- Bottom info bar: compact ID, model, and tokens with icons.

Settings panel

![Settings dialog](chat_ui/screens/settings-desktop.png)

- Server URL: set the REST endpoint (defaults to `http://localhost:8000`).
- System Prompt: optional per‑session instruction.
- Temperature: 0.0–2.0.
- Check Health: pings `/health`.
- Load Models: opens the models modal.

Models modal

![Models modal](chat_ui/screens/models-modal.png)

- Lists reported models by provider via `/models`.
- Click any model name to jump to provider docs.

How chat works
- Send: POST `/chat` with `{ message, model, conversation_id?, system_prompt?, temperature }`.
- Continue a thread: the UI passes the current `conversation_id`; server resolves the latest response and appends.
- Titles: the sidebar shows titles generated server‑side (background job) and cached in DB.
  - Endpoint used by the UI to build the list: GET `/conversations`.
  - Details view uses GET `/conversations/{id}`.

Streaming (SSE)
- Toggle “Enable Streaming (SSE)” in Settings to stream assistant replies.
- Requires a server that supports `/chat/stream` (use `python scripts/example_web_server.py` for the demo).
- Current implementation streams the generated message back in small chunks to provide an interactive feel; the non‑streaming `/chat` endpoint remains unchanged.

Responsive behavior
- Small screens stack the header; model picker becomes full width.
- The status bar uses compact icons and hides token counts under the smallest breakpoint.

Mobile views (examples)

> Note: depending on your viewer, images may be scaled.

```
chat_ui/screens/overview-desktop-2.png   # narrow viewport example
```


---

## CLI — Feature Tour

Run: `python demos/cli/cortex_cli.py`

Core commands
- `models` — list available models from `/models`.
- `history` — show previous turns for the current session.
- `settings` — set server URL, default model, temperature, timestamps, etc. (persisted in `~/.cortexai/settings.json`).
- `clear` — clear the visible console buffer.
- `status` — show current server URL, model, and temperature.
- `save` — save the last assistant reply to a file.
- `quit` — exit the CLI.

Chatting
- Just type to send. The CLI posts to `/chat` and prints the assistant reply.
- When a reply returns usage, it prints a compact token summary.

---

## Server Launcher (Docker)

File: `demos/server/run_server.py`

Environment variables passed through:
- `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `CO_API_KEY`
- `DATABASE_URL` (optional; enables persistent conversations)
- `PORT` (host port, default 8000), `CONTAINER_PORT` (default 8080)
- `CORTEX_IMAGE` (default `reaper27/cortex-api:latest`)

The launcher prints the exact `docker run` command and runs in the foreground. Use `Ctrl+C` to stop.

---

## Troubleshooting

Cannot connect / health check fails
- Ensure the Docker container is running: `docker ps` (look for the cortex API container).
- Verify the port: `PORT=8000 python demos/server/run_server.py` then set the UI Server URL to `http://localhost:8000`.

Conversation list is empty
- If you didn’t set `DATABASE_URL`, you may be on SQLite with a fresh DB; send a few messages and refresh.

Titles show “New conversation”
- Titles are generated asynchronously on the server and cached on first access. Refresh after a moment; or hit `POST /conversations/{id}/generate-title` to compute one immediately.

Dark mode not sticking
- The theme toggle is stored in `localStorage` as `theme`. If you’re in incognito, storage may be cleared between sessions.
