from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

user_repository = UserRepository()

async def get_or_create_user(db, user_data: UserCreate):
    user = await user_repository.get_user_by_telegram_id(db, user_data.telegram_id)
    if not user:
        user = await user_repository.create_user(db, user_data)
    return user