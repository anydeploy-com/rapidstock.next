from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from db.session import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    products = relationship("Product", backref="category")

