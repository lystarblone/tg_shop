from aiogram import Router, types, F
from aiogram.filters import Command
from app.core.config import settings
from app.services.order_service import update_order_status, get_order
from app.core.db import async_session

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
        await message.answer("❌ Формат: /setstatus <order_id> <status>")
        return

    async with async_session() as db:
        updated = await update_order_status(db, int(order_id), status)

    if updated:
        await message.answer(f"✅ Статус заказа {order_id} обновлён на {status}")
    else:
        await message.answer("❌ Заказ не найден")