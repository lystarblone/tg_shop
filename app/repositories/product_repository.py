from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models import Product
from app.schemas import ProductCreate
from typing import List

async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

async def get_products_by_category(db: AsyncSession, category_id: int) -> List[Product]:
    result = await db.execute(select(Product).where(Product.category_id == category_id))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        category_id=product.category_id,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product(db: AsyncSession, product_id: int, product_data: ProductCreate):
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(**product_data.dict(exclude_unset=True))
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    return await get_product_by_id(db, product_id)