import json
import aioredis
from app.core.config import settings

class CartService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def add_item(self, user_id: int, product_id: int, quantity: int = 1):
        cart_key = f"cart:{user_id}"
        current_cart = await self.redis.get(cart_key)
        cart = json.loads(current_cart) if current_cart else {}

        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity

        await self.redis.set(cart_key, json.dumps(cart))

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