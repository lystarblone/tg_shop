from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, **data) -> User:
        q = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        user = q.scalars().first()
        if user:
            return user
        user = User(telegram_id=telegram_id, **data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        q = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return q.scalars().first()