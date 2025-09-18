from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Category
from app.schemas import CategoryCreate
from typing import List

async def get_all_categories(db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category))
    return result.scalars().all()

async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    db_category = Category(name=category.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category