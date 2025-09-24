#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
MEILI_DIR="$REPO_ROOT/data/meili"
MEILI_BIN="$MEILI_DIR/meilisearch"
FALLBACK_BIN="$REPO_ROOT/meilisearch/meilisearch"
MEILI_PORT=7700
MEILI_ADDR="127.0.0.1:${MEILI_PORT}"
MASTER_KEY="qRT4skbJgqeeTdsw8oABvC0AF9qcl10cz-1VTYEu_Hs"

mkdir -p "$MEILI_DIR"

if [ ! -x "$MEILI_BIN" ]; then
  if [ -x "$FALLBACK_BIN" ]; then
    echo "[meili_dev] Using existing binary at $FALLBACK_BIN"
    cp -f "$FALLBACK_BIN" "$MEILI_BIN"
    chmod +x "$MEILI_BIN"
  else
    echo "[meili_dev] Meilisearch binary not found. Attempting to download..."
    if ! bash "$REPO_ROOT/scripts/download_meilisearch.sh"; then
      echo "[meili_dev] Download failed. Please place a Meilisearch binary at $FALLBACK_BIN or ensure network access."
      exit 1
    fi
  fi
fi

# Check if port is already in use
if lsof -iTCP:${MEILI_PORT} -sTCP:LISTEN -Pn >/dev/null 2>&1; then
  echo "[meili_dev] Port ${MEILI_PORT} is already in use. Is Meilisearch already running?"
  echo "[meili_dev] If not, free the port or change the port in this script."
  exit 1
fi

cd "$MEILI_DIR"
echo "[meili_dev] Starting Meilisearch on http://${MEILI_ADDR} with master key: ${MASTER_KEY}"
exec "$MEILI_BIN" --master-key="${MASTER_KEY}" --http-addr="${MEILI_ADDR}"
