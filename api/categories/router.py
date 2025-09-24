from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from categories.model import Category
from categories.schemas import CategoryCreate, CategoryOut
from services.meili import meili_service
from products.model import Product

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    # Index in Meilisearch
    category_data = {
        "id": db_category.id,
        "name": db_category.name,
        "description": db_category.description,
    }
    meili_service.add_category(category_data)

    return db_category


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")

    db_cat.name = category.name
    db_cat.description = category.description
    db.commit()
    db.refresh(db_cat)

    meili_service.add_category({
        "id": db_cat.id,
        "name": db_cat.name,
        "description": db_cat.description,
    })

    return db_cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(Category).filter(Category.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # Prevent deletion if products exist in this category to avoid FK errors
    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category {category_id}: {product_count} products still reference it",
        )

    db.delete(db_cat)
    db.commit()

    meili_service.delete_category(category_id)
    return None
