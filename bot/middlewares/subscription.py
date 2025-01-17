from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database.models import User
from handlers.base import get_or_create_user, FREE_MESSAGES_LIMIT

class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        super().__init__()
        self.session_pool = session_pool
    
    async def on_process_message(self, message: types.Message, data: dict):
        if message.text and message.text.startswith('/'):  # Пропускаем команды
            return
            
        async with self.session_pool() as session:
            user = await get_or_create_user(session, message.from_user)
            
            if not user.is_premium:
                # Сброс счетчика сообщений, если прошел день
                if user.last_message_date.date() < datetime.now().date():
                    user.messages_today = 0
                
                if user.messages_today >= FREE_MESSAGES_LIMIT:
                    await message.answer(
                        "⚠️ Вы достигли дневного лимита бесплатных сообщений.\n"
                        "Оформите подписку командой /subscribe для продолжения общения."
                    )
                    return False  # Прерываем обработку сообщения 