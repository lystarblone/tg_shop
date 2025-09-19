from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Никнейм Telegram")
    name: Optional[str] = Field(None, description="Полное имя")
    is_admin: bool = Field(False, description="Является ли пользователь администратором")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True