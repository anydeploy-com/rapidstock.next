import os
from pathlib import Path

# Base directories
API_DIR = Path(__file__).resolve().parent.parent  # api/
DATA_SQLITE_DIR = API_DIR.parent / "data" / "sqlite"
DATA_SQLITE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_SQLITE_DIR / "rapidstock.db"

# Database configuration
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

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
