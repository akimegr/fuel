"""
Главный файл запуска бота FuelRadarBot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.models import init_db
from handlers import start, prices, admin, profile, fuel, compare, discounts

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Проверка токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return

    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных инициализирована")

    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(fuel.router)
    dp.include_router(compare.router)
    dp.include_router(discounts.router)
    dp.include_router(prices.router)  # Старые команды для совместимости
    dp.include_router(admin.router)

    logger.info("Бот запущен и готов к работе!")

    # Запуск polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

