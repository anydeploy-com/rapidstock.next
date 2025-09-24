import meilisearch
import logging
import time
from typing import List
from core.config import MEILI_URL, MEILI_KEY, PRODUCT_INDEX, CATEGORY_INDEX, ATTRIBUTE_INDEX

# Logger setup for Meilisearch sync
logger = logging.getLogger("meili_sync")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s [MeiliSync] %(message)s", "%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class MeilisearchService:
    def __init__(self):
        # Use official client; it will send Authorization: Bearer <key> after we patch headers
        self.client = meilisearch.Client(MEILI_URL, MEILI_KEY or None)
        try:
            # Prefer Authorization bearer header for your instance
            if (
                hasattr(self.client, "http")
                and hasattr(self.client.http, "headers")
                and MEILI_KEY
            ):
                self.client.http.headers.pop("X-Meili-API-Key", None)
                self.client.http.headers["Authorization"] = f"Bearer {MEILI_KEY}"
        except Exception:
            # Non-fatal; fallback to default headers
            pass

    def ensure_indexes_exist(self) -> List[str]:
        created_indexes: List[str] = []
        try:
            for idx in [PRODUCT_INDEX, CATEGORY_INDEX, ATTRIBUTE_INDEX]:
                t_idx = time.perf_counter()
                try:
                    self.client.get_index(idx)
                    logger.info(
                        f"Index '{idx}' exists (checked in {(time.perf_counter() - t_idx) * 1000:.1f} ms)"
                    )
                except meilisearch.errors.MeilisearchApiError:
                    self.client.create_index(idx, {"primaryKey": "id"})
                    created_indexes.append(idx)
                    logger.info(
                        f"Created missing index '{idx}' in {(time.perf_counter() - t_idx) * 1000:.1f} ms"
                    )
            return created_indexes
        except Exception as e:
            logger.error(f"Could not connect to Meilisearch at {MEILI_URL}: {e}")
            raise

    def sync_all_data(self, db_session):
        from products.model import Product
        from categories.model import Category
        from attributes.model import Attribute

        logger.info("Beginning full SQLite -> Meilisearch resync")
        t_sync_start = time.perf_counter()

        # Products
        t = time.perf_counter()
        products = db_session.query(Product).all()
        product_docs = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category_id": p.category_id,
            }
            for p in products
        ]
        self.client.index(PRODUCT_INDEX).delete_all_documents()
        if product_docs:
            self.client.index(PRODUCT_INDEX).add_documents(product_docs)
        logger.info(
            f"Synced {len(product_docs)} products in {(time.perf_counter() - t) * 1000:.1f} ms"
        )

        # Categories
        t = time.perf_counter()
        categories = db_session.query(Category).all()
        category_docs = [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in categories
        ]
        self.client.index(CATEGORY_INDEX).delete_all_documents()
        if category_docs:
            self.client.index(CATEGORY_INDEX).add_documents(category_docs)
        logger.info(
            f"Synced {len(category_docs)} categories in {(time.perf_counter() - t) * 1000:.1f} ms"
        )

        # Attributes
        t = time.perf_counter()
        attributes = db_session.query(Attribute).all()
        attribute_docs = [
            {"id": a.id, "name": a.name, "value": a.value, "product_id": a.product_id}
            for a in attributes
        ]
        self.client.index(ATTRIBUTE_INDEX).delete_all_documents()
        if attribute_docs:
            self.client.index(ATTRIBUTE_INDEX).add_documents(attribute_docs)
        logger.info(
            f"Synced {len(attribute_docs)} attributes in {(time.perf_counter() - t) * 1000:.1f} ms"
        )

        total_time = (time.perf_counter() - t_sync_start) * 1000
        return len(product_docs), len(category_docs), len(attribute_docs), total_time

    def add_product(self, product_data):
        try:
            self.client.index(PRODUCT_INDEX).add_documents([product_data])
        except Exception as e:
            logger.warning(
                f"Meilisearch indexing failed for product {product_data.get('id')}: {e}"
            )

    def add_category(self, category_data):
        try:
            self.client.index(CATEGORY_INDEX).add_documents([category_data])
        except Exception as e:
            logger.warning(
                f"Meilisearch indexing failed for category {category_data.get('id')}: {e}"
            )

    def add_attributes(self, attribute_docs):
        try:
            if attribute_docs:
                self.client.index(ATTRIBUTE_INDEX).add_documents(attribute_docs)
        except Exception as e:
            logger.warning(f"Meilisearch indexing failed for attributes: {e}")

    def delete_product(self, product_id):
        try:
            self.client.index(PRODUCT_INDEX).delete_document(product_id)
        except Exception as e:
            logger.warning(
                f"Failed to delete product {product_id} from Meilisearch: {e}"
            )

    def delete_attributes(self, attribute_ids):
        try:
            if attribute_ids:
                self.client.index(ATTRIBUTE_INDEX).delete_documents(attribute_ids)
        except Exception as e:
            logger.warning(
                f"Failed to delete {len(attribute_ids)} attribute docs from Meilisearch: {e}"
            )

    def search_products(self, query):
        results = self.client.index(PRODUCT_INDEX).search(query)
        return results.get("hits", [])

    def search_categories(self, query):
        results = self.client.index(CATEGORY_INDEX).search(query)
        return results.get("hits", [])

    def search_attributes(self, query):
        results = self.client.index(ATTRIBUTE_INDEX).search(query)
        return results.get("hits", [])

    def health_check(self):
        try:
            ms_health = self.client.health()
            return ms_health.get("status", "unknown")
        except Exception:
            return "unavailable"


# Global instance
meili_service = MeilisearchService()
