import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.utils.logger import setup_logger
from app.handlers import all_routers

async def main():
    setup_logger()
    logging.info("Запуск бота")

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")