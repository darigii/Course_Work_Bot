from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from database.models import get_user_by_telegram_id
start_router = Router()
@start_router.message(Command("start"))
async def start_handler(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if user:
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Перейти к покупкам 🛍️", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))]],resize_keyboard=True)
        await message.answer("С возвращением! Готовы выбрать товар?", reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Зарегистрироваться")],
                [KeyboardButton(text="Нет, спасибо, перейти к покупкам",web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))]],resize_keyboard=True)
        await message.answer(
            "Добро пожаловать в KoreaBox! 🎉\n"
            "Хотите зарегистрироваться и получить скидку 25% на первый заказ?",
            reply_markup=markup
        )

