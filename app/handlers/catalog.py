from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from app.services.product_service import get_categories, get_products_in_category, get_product
from app.models.db import async_session

router = Router()

@router.message(Command("catalog"))
async def show_categories(message: types.Message):
    async with async_session() as db:
        categories = await get_categories(db)

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c.name, callback_data=f"category:{c.id}")
    kb.adjust(2)

    await message.answer("📂 Выберите категорию:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("category:"))
async def show_products(callback: types.CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    async with async_session() as db:
        products = await get_products_in_category(db, category_id)

    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=p.name, callback_data=f"product:{p.id}")
    kb.adjust(1)

    await callback.message.answer("🛒 Товары:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    async with async_session() as db:
        product = await get_product(db, product_id)

    if product:
        kb = InlineKeyboardBuilder()
        kb.button(text="Добавить в корзину", callback_data=f"addcart:{product.id}")
        if product.photo_url and product.photo_url.strip():
            try:
                await callback.message.answer_photo(
                    photo=product.photo_url,
                    caption=f"<b>{product.name}</b>\n\n{product.description}\n\n💰 Цена: {product.price} ₽",
                    reply_markup=kb.as_markup(),
                )
            except Exception as e:
                await callback.message.answer(
                    f"<b>{product.name}</b>\n\n{product.description}\n\n💰 Цена: {product.price} ₽\n\n⚠️ Ошибка загрузки фото: {str(e)}",
                    reply_markup=kb.as_markup(),
                )
        else:
            await callback.message.answer(
                f"<b>{product.name}</b>\n\n{product.description}\n\n💰 Цена: {product.price} ₽\n\n⚠️ Фото отсутствует",
                reply_markup=kb.as_markup(),
            )
    await callback.answer()