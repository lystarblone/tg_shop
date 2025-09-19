from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from app.models.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    total_price = Column(Float, nullable=False)
    delivery_address = Column(String(255))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")