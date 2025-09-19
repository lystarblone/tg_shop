from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.cart_service import CartService
from app.services.product_service import get_product
from app.models.db import async_session

router = Router()
cart_service = CartService()

@router.callback_query(F.data.startswith("addcart:"))
async def add_to_cart(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await cart_service.add_item(callback.from_user.id, product_id, quantity=1)
    await callback.answer("✅ Товар добавлен в корзину!")

@router.message(F.text == "Корзина")
async def show_cart(message: types.Message):
    cart = await cart_service.get_cart(message.from_user.id)
    if not cart:
        await message.answer("🛒 Ваша корзина пуста")
        return

    text = "📦 Ваша корзина:\n\n"
    async with async_session() as db:
        for product_id, quantity in cart.items():
            product = await get_product(db, int(product_id))
            if product:
                text += f"{product.name} × {quantity} = {product.price * quantity} ₽\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="Оформить заказ", callback_data="checkout")
    kb.button(text="Очистить корзину", callback_data="clearcart")

    await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data == "clearcart")
async def clear_cart(callback: types.CallbackQuery):
    await cart_service.clear_cart(callback.from_user.id)
    await callback.message.answer("🗑 Корзина очищена!")
    await callback.answer()