#!/usr/bin/env bash
set -euo pipefail

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000