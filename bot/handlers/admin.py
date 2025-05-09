from aiogram import Router, F 
from aiogram.types import  CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import ADMINS

admin_router = Router()

def true_admin(user_id):
    for admin_id in ADMINS:
        if user_id == admin_id:
            return True
        else:
            return False

@admin_router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if not true_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add")],
        [InlineKeyboardButton(text="✏ Изменить цену", callback_data="admin_edit_price")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_delete")],
        [InlineKeyboardButton(text="📦 Посмотреть товары", callback_data="admin_view")]
    ])
    await callback.message.answer("👩‍💼 Админ-панель. Выберите действие:", reply_markup=admin_keyboard)
    await callback.answer()

