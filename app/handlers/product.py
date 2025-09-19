from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(..., ge=0, description="Цена товара")
    image_url: Optional[str] = Field(None, description="Ссылка на изображение")

class ProductCreate(ProductBase):
    category_id: int = Field(..., description="ID категории")

class ProductRead(ProductBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True