from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.models import get_user_by_telegram_id, register_user, save_email_to_user
import re

registration_router = Router()

class EmailFSM(StatesGroup):
    waiting_for_email = State()
@registration_router.callback_query(F.data == "register")
async def handle_register_callback(callback: CallbackQuery, state: FSMContext):
    user = get_user_by_telegram_id(callback.from_user.id)
    if user:
        await callback.message.edit_text("📌 Вы уже зарегистрированы.")
        menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Перейти к покупкам", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))],
        [InlineKeyboardButton(text=" Админ-панель", callback_data="admin")]])
        await callback.message.answer("📦 Вот наш каталог:", reply_markup=menu)
        await callback.answer()
    else:
        register_user(callback.from_user.id, callback.from_user.full_name)
        await callback.message.edit_text("📩 Пожалуйста, введите ваш e-mail для получения скидок и новостей:")
        await state.set_state(EmailFSM.waiting_for_email)
    await callback.answer("Регистрация прошла успешно!\n")

@registration_router.message(EmailFSM.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    valid_tlds = {"ru", "com", "net", "org", "edu", "gov", "info", "biz", "ua", "kz"}
    match = re.fullmatch(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(\w{2,})", email)
    if not match:
        await message.answer("E-mail выглядит некорректным. Пример: example@mail.ru")
        return
    
    tld = match.group(1)
    if tld not in valid_tlds:
        await message.answer(f" Домен '.{tld}' не поддерживается. Попробуй, например, .ru или .com.")
        return
    
    save_email_to_user(message.from_user.id, email)

    await state.clear()
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Перейти к покупкам", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))],
        [InlineKeyboardButton(text=" Админ-панель", callback_data="admin")]])
    await message.answer("📬 E-mail сохранён! Вот наш каталог:", reply_markup=menu)

@registration_router.callback_query(F.data == "skip_registration")
async def handle_skip_registration(callback: CallbackQuery):
    await callback.message.edit_text("Вы отказались от регистрации. Каталог доступен ниже 👇")
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Перейти к покупкам", web_app=WebAppInfo(url="https://lambent-tartufo-95748f.netlify.app/"))],
        [InlineKeyboardButton(text=" Админ-панель", callback_data="admin")]])
    await callback.message.answer("📦 Вот наш каталог:", reply_markup=menu)
    await callback.answer()
