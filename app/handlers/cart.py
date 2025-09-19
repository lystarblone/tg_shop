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

@router.callback_query(F.data.startswith("changeqty:"))
async def change_quantity(callback: types.CallbackQuery):
    _, product_id, action = callback.data.split(":")
    product_id = int(product_id)
    cart = await cart_service.get_cart(callback.from_user.id)
    
    if str(product_id) not in cart:
        await callback.answer("❌ Товар не найден в корзине")
        return

    if action == "plus":
        await cart_service.add_item(callback.from_user.id, product_id, quantity=1)
    elif action == "minus":
        cart[str(product_id)] -= 1
        if cart[str(product_id)] <= 0:
            await cart_service.remove_item(callback.from_user.id, product_id)
        else:
            await cart_service.set_cart(callback.from_user.id, cart)

    cart = await cart_service.get_cart(callback.from_user.id)
    text = "📦 Ваша корзина:\n\n"
    async with async_session() as db:
        for product_id, quantity in cart.items():
            product = await get_product(db, int(product_id))
            if product:
                text += f"{product.name} × {quantity} = {product.price * quantity} ₽\n"

    kb = InlineKeyboardBuilder()
    for product_id, quantity in cart.items():
        kb.button(text=f"➖ {quantity} ➕", callback_data=f"changeqty:{product_id}:minus")
        kb.button(text=f"➕", callback_data=f"changeqty:{product_id}:plus")
    kb.button(text="Оформить заказ", callback_data="checkout")
    kb.button(text="Очистить корзину", callback_data="clearcart")
    kb.adjust(2)

    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()