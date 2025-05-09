from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from database.models import get_user_by_telegram_id
start_router = Router()

@start_router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать в KoreaBox! \n\n"
        "Мы — онлайн-магазин корейских товаров: косметика, еда, альбомы и многое другое.\n"
        "Работаем с любовью к каждому клиенту и доставляем по всей России. 🇰🇷📦\n\n"
        "Если вы впервые в нашем магазине, то при регистрации можно получить скидку 25% на первый заказ!\n\n"
        "Чтобы перейти к функциям, используйте команду /menu.")
    
@start_router.message(Command("menu"))
async def show_menu(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if user:
        menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Зарегистрироваться", callback_data="register")],
            [InlineKeyboardButton(text="🛍 Перейти к покупкам", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))],
            [InlineKeyboardButton(text="Админ-панель", callback_data="admin")]
        ])
    else:
        menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Зарегистрироваться", callback_data="register")],
            [InlineKeyboardButton(text=" Отказаться от регистрации", callback_data="skip_registration")],
            [InlineKeyboardButton(text="Админ-панель", callback_data="admin")]
        ])
    await message.answer("📋 Главное меню:", reply_markup=menu)