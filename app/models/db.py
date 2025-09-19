from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_models():
    async with engine.begin() as conn:
        from app.models.user import User
        from app.models.product import Product
        from app.models.category import Category
        from app.models.order import Order, OrderItem

        await conn.run_sync(Base.metadata.create_all)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session