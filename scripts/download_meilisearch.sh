#!/usr/bin/env bash
set -euo pipefail

# Install Meilisearch
curl -L https://install.meilisearch.com | sh

# Move the binary to ../api/meili
mkdir -p ../api/meili
mv -f meilisearch ../api/meili/meilisearch
chmod +x ../api/meili/meilisearch
