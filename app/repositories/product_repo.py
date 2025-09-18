from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        q = await self.session.execute(select(Product).where(Product.id == product_id))
        return q.scalars().first()

    async def list(self, limit: int = 20, offset: int = 0):
        q = await self.session.execute(select(Product).limit(limit).offset(offset))
        return q.scalars().all()

    async def create(self, **data) -> Product:
        product = Product(**data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product, **data) -> Product:
        for k, v in data.items():
            setattr(product, k, v)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product: Product):
        await self.session.delete(product)
        await self.session.commit()