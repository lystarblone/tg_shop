from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    async def get_user_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> User | None:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        new_user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            name=user_data.name,
            is_admin=user_data.is_admin,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user