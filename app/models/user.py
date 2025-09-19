from sqlalchemy import Column, Integer, String, Boolean
from app.models.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    username = Column(String(255))
    name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user")