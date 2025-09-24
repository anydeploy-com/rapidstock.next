#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT/api" || { echo "api directory doesn't exist, exiting"; exit 1; }

# Activate virtualenv if present
if [ -f venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

export MEILI_URL="http://127.0.0.1:7700"
export MEILI_API_KEY="masterKey"

echo "[api_dev] Starting FastAPI on http://0.0.0.0:8000 (expects Meilisearch at $MEILI_URL)"
exec uvicorn main:app --reload --host 0.0.0.0 --port 8000
