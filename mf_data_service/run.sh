#!/bin/bash
set -e

cd "$(dirname "$0")"

# Load .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8100}"

echo "Starting MFDataService on ${HOST}:${PORT}"
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
