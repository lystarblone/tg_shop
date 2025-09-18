from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import product_repository, category_repository
from app.schemas import ProductCreate, CategoryCreate
from app.models import Product, Category
from typing import List

async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    return await product_repository.get_product_by_id(db, product_id)

async def get_products_in_category(db: AsyncSession, category_id: int) -> List[Product]:
    return await product_repository.get_products_by_category(db, category_id)

async def add_product(db: AsyncSession, product: ProductCreate) -> Product:
    return await product_repository.create_product(db, product)

async def get_categories(db: AsyncSession) -> List[Category]:
    return await category_repository.get_all_categories(db)

async def add_category(db: AsyncSession, category: CategoryCreate) -> Category:
    return await category_repository.create_category(db, category)