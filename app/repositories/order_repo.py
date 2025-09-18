from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderItem

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **data) -> Order:
        order = Order(**data)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def add_item(self, order: Order, **data) -> OrderItem:
        item = OrderItem(order_id=order.id, **data)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_by_user(self, user_id: int):
        q = await self.session.execute(select(Order).where(Order.user_id == user_id))
        return q.scalars().all()


    async def get_by_number(self, order_number: str) -> Order | None:
        q = await self.session.execute(select(Order).where(Order.order_number == order_number))
        return q.scalars().first()

    async def update_status(self, order: Order, status: str):
        order.status = status
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order