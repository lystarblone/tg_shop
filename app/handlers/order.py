from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.cart_service import CartService
from app.services.order_service import create_order
from app.services.product_service import get_product
from app.models.db import async_session
from app.utils.helpers import generate_order_number
from app.schemas.order import OrderCreate, OrderItemCreate

router = Router()
cart_service = CartService()

class OrderStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_delivery = State()

@router.callback_query(F.data == "checkout")
async def process_checkout(callback: types.CallbackQuery, state: FSMContext):
    cart = await cart_service.get_cart(callback.from_user.id)
    if not cart:
        await callback.message.answer("🛒 Корзина пуста")
        await callback.answer()
        return

    await callback.message.answer("📝 Введите ваше имя:")
    await state.set_state(OrderStates.waiting_for_contact)
    await callback.answer()

@router.message(OrderStates.waiting_for_contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact_name=message.text)
    await message.answer("📞 Введите номер телефона:")
    await state.set_state(OrderStates.waiting_for_phone)

@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(contact_phone=message.text)
    await message.answer("📍 Введите адрес доставки:")
    await state.set_state(OrderStates.waiting_for_address)

@router.message(OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(delivery_address=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="Курьер", callback_data="delivery:courier")
    kb.button(text="Самовывоз", callback_data="delivery:pickup")
    await message.answer("🚚 Выберите способ доставки:", reply_markup=kb.as_markup())
    await state.set_state(OrderStates.waiting_for_delivery)

@router.callback_query(F.data.startswith("delivery:"))
async def process_delivery(callback: types.CallbackQuery, state: FSMContext):
    delivery_type = callback.data.split(":")[1]
    data = await state.get_data()

    cart = await cart_service.get_cart(callback.from_user.id)
    order_items = []
    total_price = 0.0

    async with async_session() as db:
        try:
            for product_id, quantity in cart.items():
                product = await get_product(db, int(product_id))
                if product:
                    order_items.append(OrderItemCreate(product_id=product.id, quantity=quantity))
                    total_price += float(product.price) * quantity
                else:
                    await callback.message.answer(f"⚠️ Товар с ID {product_id} не найден.")
                    await callback.answer()
                    return

            order_data = OrderCreate(
                user_id=callback.from_user.id,
                delivery_address=data["delivery_address"],
                contact_phone=data.get("contact_phone", ""),
                items=order_items,
                total_price=total_price
            )
            order = await create_order(db, order_data)
        except Exception as e:
            await callback.message.answer(f"❌ Ошибка при оформлении заказа: {str(e)}")
            await callback.answer()
            await state.clear()
            return

    await cart_service.clear_cart(callback.from_user.id)
    order_number = generate_order_number(callback.from_user.id)
    await callback.message.answer(
        f"✅ Заказ #{order_number} оформлен!\n"
        f"Имя: {data['contact_name']}\n"
        f"Телефон: {data.get('contact_phone', 'Не указан')}\n"
        f"Адрес: {data['delivery_address']}\n"
        f"Доставка: {delivery_type}\n"
        f"Сумма: {total_price} ₽"
    )
    await state.clear()
    await callback.answer()