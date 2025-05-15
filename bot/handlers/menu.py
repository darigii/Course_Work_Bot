from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Зарегистрироваться", callback_data="register")],
        [InlineKeyboardButton(text="🛍 Перейти к покупкам", web_app=WebAppInfo(url="https://lucky-naiad-2d5815.netlify.app/"))],
        [InlineKeyboardButton(text="Админ-панель", callback_data="admin")]
    ])
