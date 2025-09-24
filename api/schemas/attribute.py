from pydantic import BaseModel
from typing import Optional, List

class AttributeCreate(BaseModel):
    name: str
    value: str

class AttributeOut(AttributeCreate):
    id: int
    class Config:
        from_attributes = True
