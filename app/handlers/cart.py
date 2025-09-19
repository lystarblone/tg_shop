from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
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

@router.message(Command("cart"))
async def show_cart(message: types.Message):
    cart = await cart_service.get_cart(message.from_user.id)
    if not cart:
        await message.answer("🛒 Ваша корзина пуста")
        return

    text = "📦 Ваша корзина:\n\n"
    total = 0.0
    async with async_session() as db:
        for product_id, quantity in cart.items():
            product = await get_product(db, int(product_id))
            if product:
                item_price = float(product.price) * quantity
                text += f"{product.name} × {quantity} = {item_price} ₽\n"
                total += item_price

    kb = InlineKeyboardBuilder()
    kb.button(text="Оформить заказ", callback_data="checkout")
    kb.button(text="Очистить корзину", callback_data="clearcart")
    kb.adjust(1)

    await message.answer(text + f"\nИтого: {total} ₽", reply_markup=kb.as_markup())

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
    total = 0.0
    async with async_session() as db:
        for p_id, qty in cart.items():
            prod = await get_product(db, int(p_id))
            if prod:
                item_price = float(prod.price) * qty
                text += f"{prod.name} × {qty} = {item_price} ₽\n"
                total += item_price

    kb = InlineKeyboardBuilder()
    for p_id, qty in cart.items():
        kb.button(text=f"➖ {qty} ➕", callback_data=f"changeqty:{p_id}:minus")
        kb.button(text="➕", callback_data=f"changeqty:{p_id}:plus")
    kb.button(text="Оформить заказ", callback_data="checkout")
    kb.button(text="Очистить корзину", callback_data="clearcart")
    kb.adjust(2)

    await callback.message.edit_text(text + f"\nИтого: {total} ₽", reply_markup=kb.as_markup())
    await callback.answer()