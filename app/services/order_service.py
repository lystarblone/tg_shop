from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import order_repository
from app.schemas import OrderCreate
from app.models import Order
from typing import List

async def create_order(db: AsyncSession, order: OrderCreate) -> Order:
    return await order_repository.create_order(db, order)

async def get_user_orders(db: AsyncSession, user_id: int) -> List[Order]:
    return await order_repository.get_orders_by_user(db, user_id)

async def get_order(db: AsyncSession, order_id: int) -> Order | None:
    return await order_repository.get_order_by_id(db, order_id)

async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order | None:
    return await order_repository.update_order_status(db, order_id, status)