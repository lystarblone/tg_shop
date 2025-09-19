from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 Добро пожаловать в наш E-COMMERCE бот!\n\n"
        "Я помогу вам удобно покупать товары прямо здесь! Вы можете:\n\n"
        "🛍 Просматривать каталог товаров\n"
        "🛒 Добавлять товары в корзину\n"
        "📦 Оформлять заказы  и отслеживать их статус\n\n"
        "Чтобы начать выбирать товары, нажмите /catalog"
    )
    await message.answer(welcome_text)