from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Attribute
from schemas import AttributeCreate, AttributeOut
from services.meili import meili_service

router = APIRouter(prefix="/attributes", tags=["attributes"])

@router.post("/", response_model=AttributeOut)
def create_attribute(attribute: AttributeCreate, product_id: int, db: Session = Depends(get_db)):
    db_attr = Attribute(name=attribute.name, value=attribute.value, product_id=product_id)
    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)

    # Index in Meilisearch
    attribute_data = [{
        "id": db_attr.id,
        "name": db_attr.name,
        "value": db_attr.value,
        "product_id": db_attr.product_id
    }]
    meili_service.add_attributes(attribute_data)

    return db_attr
