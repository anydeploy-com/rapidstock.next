import os

# Database configuration
DATABASE_URL = "sqlite:///../data/sqlite/rapidstock.db"

# Meilisearch configuration
MEILI_URL = os.getenv("MEILI_URL", "http://127.0.0.1:7700")
# Prefer MEILI_MASTER_KEY if set; fall back to MEILI_API_KEY for compatibility
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")
MEILI_KEY = MEILI_MASTER_KEY or MEILI_API_KEY or ""

# Meilisearch indexes
PRODUCT_INDEX = "products"
CATEGORY_INDEX = "categories"
ATTRIBUTE_INDEX = "attributes"

# App configuration
APP_TITLE = "RapidStock API"
APP_DESCRIPTION = "FastAPI backend for RapidStock"
APP_VERSION = "1.0.0"
