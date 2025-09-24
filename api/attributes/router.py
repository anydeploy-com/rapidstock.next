from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from attributes.model import Attribute
from attributes.schemas import AttributeCreate, AttributeOut
from services.meili import meili_service

router = APIRouter(prefix="/attributes", tags=["attributes"])


@router.post("/", response_model=AttributeOut)
def create_attribute(
    attribute: AttributeCreate, product_id: int, db: Session = Depends(get_db)
):
    db_attr = Attribute(
        name=attribute.name, value=attribute.value, product_id=product_id
    )
    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)

    # Index in Meilisearch
    attribute_data = [
        {
            "id": db_attr.id,
            "name": db_attr.name,
            "value": db_attr.value,
            "product_id": db_attr.product_id,
        }
    ]
    meili_service.add_attributes(attribute_data)

    return db_attr
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from categories.model import Category
from categories.schemas import CategoryCreate, CategoryOut
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
        "description": db_category.description,
    }
    meili_service.add_category(category_data)

    return db_category

