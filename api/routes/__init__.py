from .products import router as products_router
from .categories import router as categories_router
from .attributes import router as attributes_router
from .search import router as search_router

__all__ = ["products_router", "categories_router", "attributes_router", "search_router"]
