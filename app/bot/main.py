import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.models.request import Request, RequestEvent
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Настройка сессии и бота
session = AiohttpSession(proxy=settings.TELEGRAM_PROXY_URL) if settings.TELEGRAM_PROXY_URL else AiohttpSession()
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, session=session)
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_db_user(telegram_id: str):
    """Ищет пользователя в базе по его Telegram ID"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    finally:
        db.close()

def get_user_requests(user_id: int):
    """Возвращает список активных заявок, назначенных на пользователя"""
    db = SessionLocal()
    try:
        # Берем заявки, где assignee_id = user_id и статус не 'resolved' и не 'closed'
        return db.query(Request).filter(
            Request.assignee_id == user_id,
            Request.status.notin_(["resolved", "closed"])
        ).order_by(Request.created_at.desc()).all()
    finally:
        db.close()

def get_request_details(request_id: int):
    """Получает заявку и данные о лифте"""
    db = SessionLocal()
    try:
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            return None
        # Получаем адрес лифта (для красивого вывода)
        from app.models.elevator import Elevator, Building
        elevator = db.query(Elevator).filter(Elevator.id == req.elevator_id).first()
        building = db.query(Building).filter(Building.id == elevator.building_id).first() if elevator else None
        return req, elevator, building
    finally:
        db.close()

# --- ХЕНДЛЕРЫ ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = str(message.from_user.id)
    user = get_db_user(telegram_id)
    
    if user:
        # Простая клавиатура с кнопкой "Мои заявки"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои активные заявки", callback_data="list_requests")]
        ])
        await message.answer(
            f"С возвращением, {user.full_name}!\n"
            "Нажми на кнопку ниже, чтобы посмотреть свои заявки.",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "Я тебя не узнаю. 😕\n"
            f"Твой Telegram ID: {telegram_id}\n"
            "Передай этот ID диспетчеру, чтобы он добавил тебя в систему."
        )

@dp.callback_query(F.data == "list_requests")
async def list_requests(callback: CallbackQuery):
    user = get_db_user(str(callback.from_user.id))
    if not user:
        await callback.message.answer("Ошибка: пользователь не найден.")
        return

    requests = get_user_requests(user.id)
    if not requests:
        await callback.message.edit_text("У тебя нет активных заявок! 🎉")
        return

    # Формируем сообщение со списком
    text = "Твои активные заявки:\n\n"
    for req in requests:
        # Преобразуем тип заявки в эмодзи
        emoji = "🚨" if req.type == "emergency" else "🔧" if req.type == "fault" else "⚙️"
        text += f"{emoji} Заявка #{req.id} (Лифт ID: {req.elevator_id})\n"
        text += f"Статус: {req.status}\n\n"
    
    # Создаем кнопки для каждой заявки
    buttons = []
    for req in requests:
        buttons.append([InlineKeyboardButton(
            text=f"Заявка #{req.id} (Лифт {req.elevator_id})", 
            callback_data=f"view_request_{req.id}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("view_request_"))
async def view_request(callback: CallbackQuery):
    request_id = int(callback.data.split("_")[-1])
    result = get_request_details(request_id)
    if not result:
        await callback.answer("Заявка не найдена.")
        return
    
    req, elevator, building = result
    address = building.address if building else "Адрес не найден"
    entrance = elevator.entrance if elevator else "?"
    
    text = (
        f"📄 Заявка #{req.id}\n"
        f"📍 Адрес: {address}, подъезд {entrance}\n"
        f"🛗 Лифт ID: {req.elevator_id}\n"
        f"❗ Тип: {req.type}\n"
        f"📝 Описание: {req.description or 'Нет описания'}\n"
        f"📊 Текущий статус: {req.status}\n"
    )
    
    # Кнопки для смены статуса (в зависимости от текущего)
    buttons = []
    if req.status == "assigned":
        buttons.append([InlineKeyboardButton(text="✅ Принять в работу", callback_data=f"set_status_{req.id}_accepted")])
    elif req.status == "accepted":
        buttons.append([InlineKeyboardButton(text="🚗 Выехал", callback_data=f"set_status_{req.id}_en_route")])
    elif req.status == "en_route":
        buttons.append([InlineKeyboardButton(text="📍 На месте", callback_data=f"set_status_{req.id}_on_site")])
    elif req.status == "on_site":
        buttons.append([InlineKeyboardButton(text="🏁 Устранено", callback_data=f"set_status_{req.id}_resolved")])
        
    buttons.append([InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="list_requests")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("set_status_"))
async def set_status(callback: CallbackQuery):
    # Парсим callback_data: set_status_1_resolved
    parts = callback.data.split("_")
    request_id = int(parts[2])
    new_status = parts[3]
    
    db = SessionLocal()
    try:
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            await callback.answer("Заявка не найдена.")
            return
            
        req.status = new_status
        if new_status == "resolved":
            req.resolved_at = datetime.utcnow()
            
        # Пишем в лог (аудит)
        event = RequestEvent(
            request_id=req.id,
            status=new_status,
            comment=f"Механик изменил статус на {new_status} через Telegram"
        )
        db.add(event)
        db.commit()
        
        await callback.answer(f"Статус изменен на {new_status}!")
        # Перерисовываем карточку заявки с новым статусом
        await view_request(callback)
    except Exception as e:
        db.rollback()
        await callback.answer(f"Ошибка: {e}")
    finally:
        db.close()

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())