from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from attributes.model import Attribute
from attributes.schemas import AttributeCreate, AttributeOut
from services.meili import meili_service

router = APIRouter(prefix="/attributes", tags=["attributes"])


@router.get("/", response_model=List[AttributeOut])
def list_attributes(db: Session = Depends(get_db)):
    return db.query(Attribute).all()


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


@router.get("/{attribute_id}", response_model=AttributeOut)
def get_attribute(attribute_id: int, db: Session = Depends(get_db)):
    attr = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attr


@router.put("/{attribute_id}", response_model=AttributeOut)
def update_attribute(attribute_id: int, attribute: AttributeCreate, db: Session = Depends(get_db)):
    db_attr = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not db_attr:
        raise HTTPException(status_code=404, detail="Attribute not found")

    db_attr.name = attribute.name
    db_attr.value = attribute.value
    db.commit()
    db.refresh(db_attr)

    meili_service.add_attributes([
        {
            "id": db_attr.id,
            "name": db_attr.name,
            "value": db_attr.value,
            "product_id": db_attr.product_id,
        }
    ])

    return db_attr


@router.delete("/{attribute_id}", status_code=204)
def delete_attribute(attribute_id: int, db: Session = Depends(get_db)):
    db_attr = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if not db_attr:
        raise HTTPException(status_code=404, detail="Attribute not found")

    db.delete(db_attr)
    db.commit()

    meili_service.delete_attributes([attribute_id])
    return None
