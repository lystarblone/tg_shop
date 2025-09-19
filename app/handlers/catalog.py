from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.product_service import get_categories, get_products_in_category, get_product
from app.models.db import async_session

router = Router()

class CatalogStates(StatesGroup):
    browsing_categories = State()
    browsing_products = State()

@router.message(Command("catalog"))
async def show_categories(message: types.Message, state: FSMContext):
    async with async_session() as db:
        categories = await get_categories(db)
        if not categories:
            await message.answer("⚠️ Категории товаров временно недоступны. Пожалуйста, попробуй позже или свяжись с поддержкой.")
            return

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c.name, callback_data=f"category:{c.id}")
    kb.adjust(1)

    sent_message = await message.answer("📋 Выбери категорию товаров:", reply_markup=kb.as_markup())
    await state.update_data(message_id=sent_message.message_id)
    await state.set_state(CatalogStates.browsing_categories)

@router.callback_query(F.data.startswith("category:"), CatalogStates.browsing_categories)
async def show_products(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    async with async_session() as db:
        products = await get_products_in_category(db, category_id)
        category = [c for c in await get_categories(db) if c.id == category_id][0]

    if not products:
        await callback.message.edit_text("🛒 В этой категории пока нет товаров.", reply_markup=None)
        await callback.answer()
        return

    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p.name} - {p.price} ₽", callback_data=f"product:{p.id}")
    kb.button(text="⬅️ Назад", callback_data="back_to_categories")
    kb.adjust(1)

    await callback.message.edit_text(f"🛒 Товары / {category.name}:", reply_markup=kb.as_markup())
    await state.update_data(category_id=category_id)
    await state.set_state(CatalogStates.browsing_products)
    await callback.answer()

@router.callback_query(F.data == "back_to_categories", CatalogStates.browsing_products)
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    async with async_session() as db:
        categories = await get_categories(db)
        if not categories:
            await callback.message.edit_text("⚠️ Категории товаров временно недоступны.")
            await callback.answer()
            return

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c.name, callback_data=f"category:{c.id}")
    kb.adjust(1)

    await callback.message.edit_text("📋 Выбери категорию товаров:", reply_markup=kb.as_markup())
    await state.set_state(CatalogStates.browsing_categories)
    await callback.answer()

@router.callback_query(F.data.startswith("product:"), CatalogStates.browsing_products)
async def show_product(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    async with async_session() as db:
        product = await get_product(db, product_id)
        data = await state.get_data()
        category_id = data.get("category_id")

    if product:
        kb = InlineKeyboardBuilder()
        kb.button(text="Добавить в корзину", callback_data=f"addcart:{product.id}")
        kb.button(text="⬅️ Назад", callback_data="back_to_products")
        kb.adjust(1)

        text = (
            f"<b>{product.name}</b>\n\n"
            f"{product.description or 'Описание отсутствует'}\n\n"
            f"💰 Цена: {product.price} ₽"
        )
        if not product.photo_url or not product.photo_url.strip():
            text += "\n\n⚠️ Фото отсутствует"

        try:
            await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        except Exception as e:
            await callback.message.edit_text(f"{text}\n\n⚠️ Ошибка: {str(e)}", reply_markup=kb.as_markup(), parse_mode="HTML")
    else:
        await callback.message.edit_text("⚠️ Товар не найден.", reply_markup=None)

    await state.update_data(product_id=product_id)
    await callback.answer()

@router.callback_query(F.data == "back_to_products", CatalogStates.browsing_products)
async def back_to_products(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data.get("category_id")
    if not category_id:
        await callback.message.edit_text("⚠️ Ошибка: категория не найдена.")
        await callback.answer()
        return

    async with async_session() as db:
        products = await get_products_in_category(db, category_id)
        category = [c for c in await get_categories(db) if c.id == category_id][0]

    if not products:
        await callback.message.edit_text("🛒 В этой категории пока нет товаров.", reply_markup=None)
        await callback.answer()
        return

    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p.name} - {p.price} ₽", callback_data=f"product:{p.id}")
    kb.button(text="⬅️ Назад", callback_data="back_to_categories")
    kb.adjust(1)

    await callback.message.edit_text(f"🛒 Товары / {category.name}:", reply_markup=kb.as_markup())
    await callback.answer()