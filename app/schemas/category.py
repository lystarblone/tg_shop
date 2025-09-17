from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., description="Название категории")

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True