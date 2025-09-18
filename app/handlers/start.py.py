from aiogram import Router, F
from aiogram.types import Message
from app.services.user_service import get_or_create_user
from app.schemas import UserCreate
from app.core.db import async_session

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    async with async_session() as db:
        user_data = UserCreate(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        await get_or_create_user(db, user_data)

    await message.answer(
        "👋 Привет!\n\n"
        "📦 Ты можешь просматривать товары, добавлять их в корзину и оформлять заказы.\n\n"
        "Для начала выбери категорию!"
    )