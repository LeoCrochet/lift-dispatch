import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(proxy=settings.TELEGRAM_PROXY_URL) if settings.TELEGRAM_PROXY_URL else AiohttpSession()
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = str(message.from_user.id)
    
    # Открываем сессию БД
    db = SessionLocal()
    try:
        # Ищем пользователя по telegram_id
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if user:
            await message.answer(
                f"С возвращением, {user.full_name}!\n"
                f"Твоя роль: {user.role}.\n"
                "Скоро здесь появятся твои заявки."
            )
        else:
            await message.answer(
                "Я тебя не узнаю. 😕\n"
                f"Твой Telegram ID: {telegram_id}\n"
                "Передай этот ID диспетчеру, чтобы он добавил тебя в систему."
            )
    finally:
        db.close()

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())

