from pydantic import BaseModel
from typing import Optional, List
from attributes.schemas import AttributeCreate, AttributeOut


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    attributes: Optional[List[AttributeCreate]] = []


class ProductOut(ProductCreate):
    id: int
    attributes: List[AttributeOut] = []

    class Config:
        from_attributes = True

