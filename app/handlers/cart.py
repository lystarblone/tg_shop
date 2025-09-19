from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.cart_service import CartService
from app.services.product_service import get_product
from app.services.order_service import create_order
from app.services.user_service import get_or_create_user
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.models.db import async_session

router = Router()
cart_service = CartService()

class CheckoutStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_delivery = State()

@router.callback_query(F.data.startswith("addcart:"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    await cart_service.add_item(callback.from_user.id, product_id, quantity=1)
    
    async with async_session() as db:
        product = await get_product(db, product_id)
        if not product:
            await callback.message.edit_text("⚠️ Товар не найден.", reply_markup=None)
            await callback.answer()
            return

    confirmation_text = f"✅ Товар \"{product.name}\" успешно добавлен в корзину!"
    try:
        await callback.message.edit_text(confirmation_text, reply_markup=None, parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(
            f"{confirmation_text}\n\n⚠️ Ошибка: {str(e)}",
            reply_markup=None,
            parse_mode="HTML"
        )

    await callback.answer()

@router.message(Command("cart"))
async def show_cart(message: types.Message, state: FSMContext):
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

    sent_message = await message.answer(text + f"\nИтого: {total} ₽", reply_markup=kb.as_markup())
    await state.update_data(cart_message_id=sent_message.message_id)

@router.callback_query(F.data == "clearcart")
async def clear_cart(callback: types.CallbackQuery, state: FSMContext):
    await cart_service.clear_cart(callback.from_user.id)
    await callback.message.edit_text("🗑 Корзина очищена!", reply_markup=None)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    cart = await cart_service.get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🛒 Ваша корзина пуста", reply_markup=None)
        await callback.answer()
        return

    await callback.message.edit_text("📝 Введите ваше имя:", reply_markup=None)
    await state.set_state(CheckoutStates.waiting_for_name)
    await callback.answer()

@router.message(CheckoutStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Введите номер телефона:")
    await state.set_state(CheckoutStates.waiting_for_phone)

@router.message(CheckoutStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📍 Введите адрес доставки:")
    await state.set_state(CheckoutStates.waiting_for_address)

@router.message(CheckoutStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Курьер", callback_data="delivery:courier")
    kb.button(text="Самовывоз", callback_data="delivery:pickup")
    kb.adjust(1)

    sent_message = await message.answer("🚚 Выберите способ доставки:", reply_markup=kb.as_markup())
    await state.update_data(delivery_message_id=sent_message.message_id)
    await state.set_state(CheckoutStates.waiting_for_delivery)

@router.callback_query(F.data.startswith("delivery:"))
async def process_delivery(callback: types.CallbackQuery, state: FSMContext):
    delivery_method = callback.data.split(":")[1]
    user_data = await state.get_data()
    delivery_message_id = user_data.get("delivery_message_id")

    cart = await cart_service.get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🛒 Корзина пуста", reply_markup=None)
        await callback.answer()
        return

    async with async_session() as db:
        user_data_schema = UserCreate(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username or "unknown",
            name=f"{callback.from_user.first_name or ''} {callback.from_user.last_name or ''}".strip() or None,
            is_admin=False
        )
        user = await get_or_create_user(db, user_data_schema)

        order_items = []
        total_price = 0.0
        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            product = await get_product(db, product_id)
            if product:
                order_items.append(OrderItemCreate(product_id=product.id, quantity=quantity))
                total_price += float(product.price) * quantity
            else:
                await callback.message.edit_text("⚠️ Товар не найден.", reply_markup=None)
                await callback.answer()
                return

        order_data = OrderCreate(
            user_id=user.id,
            delivery_address=user_data.get('address'),
            contact_phone=user_data.get('phone'),
            items=order_items,
            total_price=total_price,
            status="pending",
            delivery_method=delivery_method
        )
        order = await create_order(db, order_data)

    confirmation_text = (
        f"✅ Заказ #{order.id} успешно оформлен!\n\n"
        f"Имя: {user_data.get('name')}\n"
        f"Телефон: {user_data.get('phone')}\n"
        f"Адрес: {user_data.get('address')}\n"
        f"Способ доставки: {'Курьер' if delivery_method == 'courier' else 'Самовывоз'}\n"
        f"Сумма: {total_price} ₽"
    )

    try:
        await callback.message.bot.edit_message_text(
            text=confirmation_text,
            chat_id=callback.message.chat.id,
            message_id=delivery_message_id,
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"{confirmation_text}\n\n⚠️ Ошибка: {str(e)}",
            parse_mode="HTML"
        )

    await cart_service.clear_cart(callback.from_user.id)
    await state.clear()
    await callback.answer()