import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings
from app.utils.logger import setup_logger
from app.handlers import all_routers
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramBadRequest

async def main():
    logger = setup_logger()
    logger.info("Запуск бота")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    try:
        from app.models.db import init_models
        await init_models()
        logger.info("Модели базы данных инициализированы")
    except Exception as e:
        logger.error(f"Ошибка инициализации моделей: {e}")
        raise

    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/catalog", description="Показать категории"),
        BotCommand(command="/cart", description="Просмотреть корзину"),
        BotCommand(command="/orders", description="Мои заказы"),
        BotCommand(command="/setstatus", description="Обновить статус заказа (для админов)"),
        BotCommand(command="/addproduct", description="Добавить товар (для админов)"),
        BotCommand(command="/editproduct", description="Редактировать товар (для админов)"),
    ]
    try:
        await bot.set_my_commands(commands)
        logger.info("Команды бота зарегистрированы")
    except TelegramBadRequest as e:
        logger.error(f"Ошибка регистрации команд: {e}")

    for router in all_routers:
        dp.include_router(router)
        logger.info(f"Роутер {router} подключён")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске поллинга: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
    except Exception as e:
        logging.error(f"Необработанная ошибка: {e}")