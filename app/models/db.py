from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

Base = declarative_base()

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_models():
    from app.models.user import User
    from app.models.product import Product
    from app.models.category import Category
    from app.models.order import Order
    from app.models.order_item import OrderItem

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            Base.registry.configure()
    except Exception as e:
        print(f"Ошибка при инициализации моделей: {e}")
        raise

async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            print(f"Ошибка в сессии базы данных: {e}")
            raise
        finally:
            await session.close()