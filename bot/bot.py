import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import get_settings
from database.models import Base
from handlers import register_handlers
from middlewares.subscription import SubscriptionMiddleware
from services.ai_service import AIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Загрузка настроек
    settings = get_settings()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.bot.token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    
    # Настройка базы данных
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{settings.db.database}",
        echo=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создание сессии для работы с БД
    async_sessionmaker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Инициализация AI сервиса
    ai_service = AIService(settings.ai_provider, settings.ai_api_key)
    
    # Регистрация middleware
    dp.middleware.setup(SubscriptionMiddleware(async_sessionmaker))
    
    # Обновленная регистрация хендлеров
    register_handlers(dp, async_sessionmaker, settings, ai_service)
    
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 