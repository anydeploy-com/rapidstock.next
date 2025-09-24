from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryOut(CategoryCreate):
    id: int
    class Config:
        from_attributes = True
