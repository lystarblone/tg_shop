from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.product_service import get_categories
from app.models.db import async_session

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать!\n\nЗдесь ты можешь выбрать товары, добавить их в корзину и оформить заказ.")
    async with async_session() as db:
        categories = await get_categories(db)
        if not categories:
            await message.answer("⚠️ Категории товаров временно недоступны. Пожалуйста, попробуй позже или свяжись с поддержкой.")
            return

    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"category:{category.id}")
    kb.adjust(1)

    await message.answer("📋 Выбери категорию товаров:", reply_markup=kb.as_markup())