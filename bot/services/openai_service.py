import openai
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
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
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except openai.error.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            return "⚠️ Извините, превышен лимит запросов к AI. Попробуйте позже."
            
        except openai.error.AuthenticationError:
            logger.error("OpenAI API authentication failed")
            return "⚠️ Ошибка аутентификации AI. Обратитесь к администратору."
            
        except openai.error.InsufficientQuotaError:
            logger.error("OpenAI API insufficient quota")
            return "⚠️ Извините, закончилась квота AI. Обратитесь к администратору."
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"⚠️ Произошла ошибка при обработке сообщения. Попробуйте позже." 