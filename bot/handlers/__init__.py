from aiogram import Dispatcher
from .base import register_base_handlers

def register_handlers(dp: Dispatcher, session_pool, config, openai_service):
    register_base_handlers(dp, session_pool, openai_service) 