from aiogram import Dispatcher
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from database.models import User, Subscription
from services.ai_service import AIService

# Константы
FREE_MESSAGES_LIMIT = 10  # Лимит бесплатных сообщений в день

async def get_or_create_user(session: AsyncSession, user: types.User):
    result = await session.execute(
        select(User).where(User.tg_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    if db_user is None:
        db_user = User(
            tg_id=user.id,
            username=user.username,
            full_name=user.full_name
        )
        session.add(db_user)
        await session.commit()
    
    return db_user

async def cmd_start(message: types.Message, session: AsyncSession):
    user = await get_or_create_user(session, message.from_user)
    
    welcome_text = (
        f"Сәлем, {message.from_user.full_name}! 👋\n\n"
        "Мен қазақ тілін үйренуге көмектесетін бот!\n"
        "Я бот для изучения казахского языка!\n\n"
        "Доступные команды:\n"
        "/help - Помощь\n"
        "/subscribe - Оформить подписку"
    )
    
    await message.answer(welcome_text)

async def cmd_help(message: types.Message):
    help_text = (
        "🤖 Как пользоваться ботом:\n\n"
        "1. Просто напишите мне сообщение на русском или казахском\n"
        "2. Я помогу вам с переводом и объяснением\n"
        "3. Бесплатно доступно 10 сообщений в день\n"
        "4. Для полного доступа оформите подписку командой /subscribe\n\n"
        "Команды:\n"
        "/start - Начать сначала\n"
        "/help - Это сообщение\n"
        "/subscribe - Оформить подписку\n"
        "/profile - Информация о профиле"
    )
    
    await message.answer(help_text)

async def cmd_profile(message: types.Message, session: AsyncSession):
    user = await get_or_create_user(session, message.from_user)
    
    subscription_status = "Активна" if user.is_premium else "Отсутствует"
    messages_left = FREE_MESSAGES_LIMIT - user.messages_today if not user.is_premium else "∞"
    
    profile_text = (
        f"👤 Профиль\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"Подписка: {subscription_status}\n"
        f"Сообщений осталось сегодня: {messages_left}"
    )
    
    await message.answer(profile_text)

async def handle_message(message: Message, ai_service: AIService):
    try:
        response = await ai_service.process_message(message.text)
        await message.reply(response)
    except Exception as e:
        await message.reply("Произошла ошибка при обработке сообщения")

def register_base_handlers(dp: Dispatcher, session_pool, ai_service: AIService):
    dp.register_message_handler(
        lambda message: handle_message(message, ai_service),
        content_types=['text']
    ) 