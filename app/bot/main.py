import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

if settings.TELEGRAM_PROXY_URL:
    session = AiohttpSession(proxy=settings.TELEGRAM_PROXY_URL)
    print(f"Используется прокси: {settings.TELEGRAM_PROXY_URL}")
else:
    session = AiohttpSession()
    print("Прокси не используется")

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Я бот диспетчерской службы."
    )

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())

