from fastapi import APIRouter
from services.meili import meili_service

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/products/")
def search_products(q: str):
    return meili_service.search_products(q)

@router.get("/categories/")
def search_categories(q: str):
    return meili_service.search_categories(q)

@router.get("/attributes/")
def search_attributes(q: str):
    return meili_service.search_attributes(q)
