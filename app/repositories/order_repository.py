from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Order, OrderItem
from app.schemas import OrderCreate
from app.utils import generate_order_number
from typing import List

async def create_order(db: AsyncSession, order: OrderCreate) -> Order:
    db_order = Order(
        user_id=order.user_id,
        status="pending",
        total_price=order.total_price,
        delivery_address=order.delivery_address,
        contact_phone=order.contact_phone,
    )
    db_order.order_number = generate_order_number(order.user_id)
    db.add(db_order)
    await db.flush()

    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.quantity * 1.0,
        )
        db.add(db_item)

    await db.commit()
    await db.refresh(db_order)
    return db_order

async def get_orders_by_user(db: AsyncSession, user_id: int) -> List[Order]:
    result = await db.execute(select(Order).where(Order.user_id == user_id))
    return result.scalars().all()

async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()

async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order | None:
    order = await get_order_by_id(db, order_id)
    if order:
        order.status = status
        await db.commit()
        await db.refresh(order)
    return order