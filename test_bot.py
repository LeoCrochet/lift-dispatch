import asyncio
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from app.core.config import settings

async def main():
    print(f"Прокси: {settings.TELEGRAM_PROXY_URL}")
    
    session = AiohttpSession(proxy=settings.TELEGRAM_PROXY_URL) if settings.TELEGRAM_PROXY_URL else AiohttpSession()
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
    
    try:
        print("Пытаемся подключиться к Telegram...")
        me = await bot.get_me()
        print(f"✅ Успех! Бот подключен: @{me.username}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {type(e).__name__}: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())