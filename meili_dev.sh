#!/bin/bash
# Start Meilisearch development server
cd "$(dirname "$0")/api/meilisearch" || exit 1
./meilisearch --master-key=masterKey --http-addr=127.0.0.1:7700

