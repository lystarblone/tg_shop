from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Никнейм Telegram")
    full_name: Optional[str] = Field(None, description="Полное имя")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True