#!/usr/bin/env bash
set -euo pipefail

# Simple SSE smoke test for /chat/stream
# Usage:
#   ./scripts/smoke_sse.sh [URL]
# Default URL: http://localhost:8000

URL=${1:-http://localhost:8000}

echo "Checking health at $URL/health..."
if ! curl -fsS "$URL/health" >/dev/null; then
  echo "Health check failed at $URL/health" >&2
  exit 1
fi

echo "Hitting $URL/chat/stream (first 40 lines shown):"
curl -N -s \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"message":"SSE smoke test","model":"gpt-4o-mini"}' \
  "$URL/chat/stream" | sed -n '1,40p'

echo
echo "Done."

