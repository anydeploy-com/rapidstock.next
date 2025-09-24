#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT/frontend" || { echo "frontend directory doesn't exist, exiting"; exit 1; }

echo "[frontend_dev] Starting Nuxt dev server on http://localhost:3000"
exec npm run dev
