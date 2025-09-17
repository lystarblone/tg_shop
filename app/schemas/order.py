from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemRead(OrderItemBase):
    id: int
    price: float

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: int
    status: str = "pending"
    total_price: float = 0.0
    delivery_address: Optional[str] = None
    contact_phone: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderRead(OrderBase):
    id: int
    created_at: datetime
    items: List[OrderItemRead]

    class Config:
        orm_mode = True
