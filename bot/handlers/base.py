from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command
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
        "/profile - Ваш профиль"
    )
    
    await message.answer(welcome_text)

async def cmd_help(message: types.Message):
    help_text = (
        "🤖 Как пользоваться ботом:\n\n"
        "1. Просто напишите мне слово или фразу на русском или казахском\n"
        "2. Я помогу вам с переводом и объяснением грамматики\n"
        "3. Бесплатно доступно 10 сообщений в день\n\n"
        "Команды:\n"
        "/start - Начать сначала\n"
        "/help - Это сообщение\n"
        "/profile - Информация о профиле"
    )
    
    await message.answer(help_text)

async def cmd_profile(message: types.Message, session: AsyncSession):
    user = await get_or_create_user(session, message.from_user)
    
    messages_left = FREE_MESSAGES_LIMIT - user.messages_today if not user.is_premium else "∞"
    
    profile_text = (
        f"👤 Профиль\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"Сообщений сегодня: {user.messages_today}\n"
        f"Осталось сообщений: {messages_left}"
    )
    
    await message.answer(profile_text)

async def handle_message(message: types.Message, session: AsyncSession, ai_service: AIService):
    try:
        # Получаем или создаем пользователя
        user = await get_or_create_user(session, message.from_user)
        
        # Проверяем лимит сообщений
        if not user.is_premium and user.messages_today >= FREE_MESSAGES_LIMIT:
            await message.reply(
                "Достигнут дневной лимит бесплатных сообщений.\n"
                "Попробуйте снова завтра!"
            )
            return
        
        # Обновляем счетчик сообщений
        user.messages_today += 1
        user.last_message_date = datetime.now()
        await session.commit()
        
        # Обрабатываем сообщение через AI
        response = await ai_service.process_message(message.text)
        await message.reply(response)
        
    except Exception as e:
        await message.reply("Произошла ошибка при обработке сообщения")

def register_base_handlers(dp: Dispatcher, session_pool, ai_service: AIService):
    # Регистрируем обработчики команд
    dp.register_message_handler(
        lambda msg: cmd_start(msg, session_pool()),
        Command("start")
    )
    dp.register_message_handler(cmd_help, Command("help"))
    dp.register_message_handler(
        lambda msg: cmd_profile(msg, session_pool()),
        Command("profile")
    )
    
    # Регистрируем обработчик текстовых сообщений
    dp.register_message_handler(
        lambda msg: handle_message(msg, session_pool(), ai_service),
        content_types=['text']
    ) 