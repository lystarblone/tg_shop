import json
import logging
import redis.asyncio as redis
from app.core.config import settings

class CartService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def add_item(self, user_id: int, product_id: int, quantity: int = 1):
        from app.services.product_service import get_product
        from app.models.db import async_session

        async with async_session() as db:
            product = await get_product(db, product_id)
            if not product:
                return False

            cart_key = f"cart:{user_id}"
            try:
                current_cart = await self.redis.get(cart_key)
                cart = json.loads(current_cart) if current_cart else {}
                if str(product_id) in cart:
                    cart[str(product_id)] += quantity
                else:
                    cart[str(product_id)] = quantity
                await self.redis.set(cart_key, json.dumps(cart))
                return True
            except Exception as e:
                logging.error(f"Redis error: {e}")
                return False

    async def get_cart(self, user_id: int) -> dict:
        cart_key = f"cart:{user_id}"
        current_cart = await self.redis.get(cart_key)
        return json.loads(current_cart) if current_cart else {}

    async def remove_item(self, user_id: int, product_id: int):
        cart = await self.get_cart(user_id)
        if str(product_id) in cart:
            del cart[str(product_id)]
        cart_key = f"cart:{user_id}"
        await self.redis.set(cart_key, json.dumps(cart))

    async def clear_cart(self, user_id: int):
        cart_key = f"cart:{user_id}"
        await self.redis.delete(cart_key)

    async def set_cart(self, user_id: int, cart: dict):
        cart_key = f"cart:{user_id}"
        try:
            await self.redis.set(cart_key, json.dumps(cart))
        except Exception as e:
            logging.error(f"Redis error: {e}")