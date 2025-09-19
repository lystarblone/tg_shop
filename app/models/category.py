from sqlalchemy import Column, Integer, String, Text
from app.models.db import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    products = relationship("Product", back_populates="category")