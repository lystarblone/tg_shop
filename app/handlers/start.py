from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.product_service import get_categories
from app.models.db import async_session

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет!\nТы можешь просматривать товары, добавлять их в корзину и оформлять заказы.")

    async with async_session() as db:
        categories = await get_categories(db)
        if not categories:
            await message.answer("⚠️ Категории не найдены. Обратитесь к администратору.")
            return

    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"category:{category.id}")
    kb.adjust(1)

    await message.answer("📋 Выбери категорию:", reply_markup=kb.as_markup())