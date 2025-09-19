import pytest
from app.services.cart_service import CartService
from app.services.product_service import get_product
from app.models.db import async_session
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_add_to_cart():
    cart_service = CartService()
    user_id = 123
    product_id = 1
    await cart_service.clear_cart(user_id)
    result = await cart_service.add_item(user_id, product_id, quantity=2)
    assert result is True
    cart = await cart_service.get_cart(user_id)
    assert cart == {"1": 2}

@pytest.mark.asyncio
async def test_get_empty_cart():
    cart_service = CartService()
    user_id = 456
    await cart_service.clear_cart(user_id)
    cart = await cart_service.get_cart(user_id)
    assert cart == {}

@pytest.mark.asyncio
async def test_add_nonexistent_product():
    cart_service = CartService()
    user_id = 789
    product_id = 999
    original_get_product = get_product
    get_product = AsyncMock(return_value=None)
    result = await cart_service.add_item(user_id, product_id)
    assert result is False
    cart = await cart_service.get_cart(user_id)
    assert cart == {}
    get_product = original_get_product