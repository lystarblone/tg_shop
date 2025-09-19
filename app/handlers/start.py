# app/handlers/start.py
from aiogram import Router, F
from aiogram.types import Message
from app.services.user_service import get_or_create_user
from app.schemas.user import UserCreate
from app.models.db import async_session
from app.core.redis import get_redis

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    async with async_session() as db:
        user_data = UserCreate(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            name=message.from_user.full_name,
            is_admin=False
        )
        user = await get_or_create_user(db, user_data)
        redis_client = get_redis()
        redis_client.set(f"user:{user.telegram_id}", user.name)

    await message.answer(
        "👋 Привет!\n\n"
        "📦 Ты можешь просматривать товары, добавлять их в корзину и оформлять заказы.\n\n"
        "Для начала выбери категорию!"
    )