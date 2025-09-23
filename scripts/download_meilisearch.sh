# Install Meilisearch
curl -L https://install.meilisearch.com | sh

# Move the binary to ../api/meilisearch
mkdir -p ../api/meilisearch
mv meilisearch ../api/meilisearch/meilisearch
chmod +x ../api/meilisearch