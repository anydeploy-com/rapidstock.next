from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Category
from schemas import CategoryCreate, CategoryOut
from services.meili import meili_service

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
        "description": db_category.description
    }
    meili_service.add_category(category_data)

    return db_category
