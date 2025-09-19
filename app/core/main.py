import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings
from app.utils.logger import setup_logger
from app.handlers import all_routers
from aiogram.types import BotCommand

async def main():
    setup_logger()
    logging.info("Запуск бота")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    from app.models.db import init_models
    await init_models()

    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/catalog", description="Показать категории"),
        BotCommand(command="/cart", description="Просмотреть корзину"),
        BotCommand(command="/orders", description="Мои заказы"),
        BotCommand(command="/setstatus", description="Обновить статус заказа (для админов)"),
        BotCommand(command="/addproduct", description="Добавить товар (для админов)"),
        BotCommand(command="/editproduct", description="Редактировать товар (для админов)"),
    ]
    await bot.set_my_commands(commands)

    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")