from dataclasses import dataclass, field
from environs import Env
from typing import List

@dataclass
class DbConfig:
    database: str = "bot.db"

@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    use_redis: bool = False

@dataclass
class AIConfig:
    provider: str = "google"
    model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 500

@dataclass
class Settings:
    bot: TgBot
    db: DbConfig
    ai_provider: str
    ai_api_key: str
    ai: AIConfig = field(default_factory=AIConfig)

def get_settings(path: str = None):
    env = Env()
    env.read_env(path)

    return Settings(
        bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS", []))),
            use_redis=env.bool("USE_REDIS", False),
        ),
        db=DbConfig(
            database=env.str("DATABASE_URL", "bot.db")
        ),
        ai_provider=env.str("AI_PROVIDER", "google"),
        ai_api_key=env.str("AI_API_KEY")
    ) 