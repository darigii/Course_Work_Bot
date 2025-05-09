from aiogram import Router, F
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database.models import register_user, save_email_to_user
registration_router = Router()

class EmailForm(StatesGroup):
    waiting_for_email = State()

@registration_router.message(F.text.lower() == "зарегистрироваться")
async def register_handler(message: Message, state: FSMContext):
    register_user(message.from_user.id, message.from_user.full_name)
    await message.answer("🎉 Спасибо за регистрацию!\nВведите ваш e-mail для получения скидок и уведомлений:")
    await state.set_state(EmailForm.waiting_for_email)
@registration_router.message(EmailForm.waiting_for_email)
async def save_email(message: Message, state: FSMContext):
    email = message.text
    save_email_to_user(message.from_user.id, email)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton( text="Перейти к покупкам 🛍️", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))]],resize_keyboard=True)
    await message.answer("📩 Спасибо! Ваш e-mail сохранён.\nМожете перейти к покупкам 👇", reply_markup=markup)
    await state.clear()
@registration_router.message(F.text.lower() == "нет, спасибо, перейти к покупкам")
async def skip_registration(message: Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Перейти к покупкам 🛍️",web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))]],resize_keyboard=True)
    await message.answer("Без проблем 😊 Вот наш каталог 👇", reply_markup=markup)
