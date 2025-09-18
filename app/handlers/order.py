from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.cart_service import CartService
from app.services.order_service import create_order
from app.schemas import OrderCreate, OrderItemCreate
from app.core.db import async_session

router = Router()
cart_service = CartService()

class CheckoutForm(StatesGroup):
    phone = State()
    address = State()

@router.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📱 Введите номер телефона:")
    await state.set_state(CheckoutForm.phone)
    await callback.answer()

@router.message(CheckoutForm.phone)
async def enter_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📍 Введите адрес доставки:")
    await state.set_state(CheckoutForm.address)

@router.message(CheckoutForm.address)
async def finish_checkout(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data["phone"]
    address = message.text

    cart = await cart_service.get_cart(message.from_user.id)
    if not cart:
        await message.answer("❌ Корзина пуста")
        return

    async with async_session() as db:
        items = [
            OrderItemCreate(product_id=int(pid), quantity=qty)
            for pid, qty in cart.items()
        ]
        order = OrderCreate(
            user_id=message.from_user.id,
            total_price=0.0,
            delivery_address=address,
            contact_phone=phone,
            items=items,
        )
        new_order = await create_order(db, order)

    await cart_service.clear_cart(message.from_user.id)
    await state.clear()
    await message.answer(f"✅ Заказ №{new_order.id} оформлен!\nМы свяжемся с вами.")