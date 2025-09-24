from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="attributes")
