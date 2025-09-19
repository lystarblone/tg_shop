from aiogram import Router, types, F
from aiogram.filters import Command
from app.core.config import settings
from app.services.order_service import update_order_status, get_order
from app.services.product_service import add_product, get_product
from app.handlers.product import ProductCreate
from app.models.db import async_session

router = Router()

def is_admin(user_id: int) -> bool:
    return str(user_id) in settings.ADMIN_IDS.split(",")

@router.message(Command("setstatus"))
async def set_status(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return

    try:
        _, order_id, status = message.text.split()
    except ValueError:
        await message.answer("❌ Формат: /setstatus order_id status")
        return

    async with async_session() as db:
        updated = await update_order_status(db, int(order_id), status)

    if updated:
        await message.answer(f"✅ Статус заказа {order_id} обновлён на {status}")
    else:
        await message.answer("❌ Заказ не найден")

@router.message(Command("addproduct"))
async def add_product_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return

    try:
        _, name, price, category_id = message.text.split(maxsplit=3)
        price = float(price)
        category_id = int(category_id)
    except ValueError:
        await message.answer("❌ Формат: /addproduct name price category_id")
        return

    product_data = ProductCreate(name=name, price=price, category_id=category_id)
    async with async_session() as db:
        product = await add_product(db, product_data)
        await message.answer(f"✅ Товар {product.name} добавлен с ID {product.id}")

@router.message(Command("editproduct"))
async def edit_product_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return

    try:
        _, product_id, name, price, category_id = message.text.split(maxsplit=4)
        product_id = int(product_id)
        price = float(price)
        category_id = int(category_id)
    except ValueError:
        await message.answer("❌ Формат: /editproduct product_id name price category_id")
        return

    product_data = ProductCreate(name=name, price=price, category_id=category_id)
    async with async_session() as db:
        product = await get_product(db, product_id)
        if not product:
            await message.answer("❌ Товар не найден")
            return
        from app.repositories.product_repository import update_product
        updated_product = await update_product(db, product_id, product_data)
        await message.answer(f"✅ Товар с ID {product_id} обновлён")