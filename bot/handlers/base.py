from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from database.models import User, Subscription
from services.openai_service import OpenAIService

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

async def handle_message(message: types.Message, session: AsyncSession, openai_service: OpenAIService):
    user = await get_or_create_user(session, message.from_user)
    
    # Проверяем лимит сообщений для бесплатных пользователей
    if not user.is_premium:
        if user.messages_today >= FREE_MESSAGES_LIMIT:
            return  # Middleware уже отправил сообщение о лимите
        
        user.messages_today += 1
        user.last_message_date = datetime.now()
        await session.commit()
    
    # Отправляем индикатор набора текста
    await message.answer_chat_action("typing")
    
    # Обрабатываем сообщение через OpenAI
    response = await openai_service.process_message(message.text)
    await message.answer(response)

def register_base_handlers(dp: Dispatcher, session_pool, openai_service: OpenAIService):
    dp.register_message_handler(lambda msg: cmd_start(msg, session_pool()), Command("start"))
    dp.register_message_handler(cmd_help, Command("help"))
    dp.register_message_handler(lambda msg: cmd_profile(msg, session_pool()), Command("profile"))
    dp.register_message_handler(
        lambda msg: handle_message(msg, session_pool(), openai_service)
    ) 