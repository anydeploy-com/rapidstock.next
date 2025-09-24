from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from products.model import Product
from categories.model import Category
from attributes.model import Attribute
from products.schemas import ProductCreate, ProductOut
from services.meili import meili_service

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Validate category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category id {product.category_id} does not exist")

    db_product = Product(name=product.name, description=product.description, category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Add attributes
    new_attribute_docs = []
    for attr in product.attributes:
        db_attr = Attribute(name=attr.name, value=attr.value, product_id=db_product.id)
        db.add(db_attr)
        db.flush()  # get id before commit
        new_attribute_docs.append({
            "id": db_attr.id,
            "name": db_attr.name,
            "value": db_attr.value,
            "product_id": db_attr.product_id
        })
    db.commit()
    db.refresh(db_product)

    # Index in Meilisearch
    product_data = {
        "id": db_product.id,
        "name": db_product.name,
        "description": db_product.description,
        "category_id": db_product.category_id
    }
    meili_service.add_product(product_data)
    if new_attribute_docs:
        meili_service.add_attributes(new_attribute_docs)

    return db_product


@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category id {product.category_id} does not exist")

    # Update product fields
    db_product.name = product.name
    db_product.description = product.description
    db_product.category_id = product.category_id

    # Remove old attributes
    db.query(Attribute).filter(Attribute.product_id == product_id).delete(synchronize_session=False)
    db.flush()

    # Add new attributes
    new_attribute_docs = []
    for attr in product.attributes:
        db_attr = Attribute(name=attr.name, value=attr.value, product_id=db_product.id)
        db.add(db_attr)
        db.flush()
        new_attribute_docs.append({
            "id": db_attr.id,
            "name": db_attr.name,
            "value": db_attr.value,
            "product_id": db_attr.product_id
        })
    db.commit()
    db.refresh(db_product)

    # Upsert in Meilisearch
    product_data = {
        "id": db_product.id,
        "name": db_product.name,
        "description": db_product.description,
        "category_id": db_product.category_id
    }
    meili_service.add_product(product_data)
    if new_attribute_docs:
        meili_service.add_attributes(new_attribute_docs)

    return db_product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Collect related attribute IDs before deletion
    attribute_ids = [a.id for a in product.attributes]

    # Delete attributes then product
    db.query(Attribute).filter(Attribute.product_id == product_id).delete(synchronize_session=False)
    db.delete(product)
    db.commit()

    # Update Meilisearch indexes
    meili_service.delete_product(product_id)
    if attribute_ids:
        meili_service.delete_attributes(attribute_ids)

    return Response(status_code=204)

