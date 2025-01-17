import google.generativeai as genai
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        
        if provider == "google":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        self.system_prompt = """
        Ты - помощник для изучения казахского языка. Твои основные задачи:
        1. Если сообщение на русском - переведи на казахский и объясни грамматику
        2. Если сообщение на казахском - переведи на русский и объясни грамматику
        3. Отвечай кратко и структурированно
        4. Используй эмодзи для лучшего восприятия
        
        Формат ответа:
        🔄 Перевод: [перевод]
        📝 Транскрипция: [транскрипция]
        🔍 Грамматика: [краткое объяснение грамматических особенностей]
        """

    async def process_message(self, user_message: str) -> str:
        try:
            if self.provider == "google":
                response = await self.model.generate_content_async(
                    f"{self.system_prompt}\n\nUser: {user_message}"
                )
                return response.text
                
        except Exception as e:
            logger.error(f"AI API error: {str(e)}")
            return f"⚠️ Произошла ошибка при обработке сообщения. Попробуйте позже." 