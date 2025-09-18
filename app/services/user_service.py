from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import user_repository
from app.schemas import UserCreate
from app.models import User

async def get_or_create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user = await user_repository.get_user_by_telegram_id(db, user_data.telegram_id)
    if not user:
        user = await user_repository.create_user(db, user_data)
    return user