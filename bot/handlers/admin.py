from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot.config import ADMINS, BOT_TOKEN
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.models import add_product, get_all_products
import requests
from database.models import delete_product_by_title  
import httpx
import sqlite3

admin_router = Router()
# проверка на админа 
def true_admin(user_id):
    return user_id in ADMINS
# отправка на сайт с помощью удаленного сервера на pythonanywhere
def save_to_site(product):
    url = "https://darigii.pythonanywhere.com/add"
    try:
        response = requests.post(url, json=product)
        print("Отправка на сайт:", response.status_code, response.text)
    except Exception as e:
        print("Ошибка при отправке на сайт:", e)

class AddProductFSM(StatesGroup):
    waiting_main_category = State()
    waiting_subcategory = State()
    waiting_name = State()
    waiting_price = State()
    waiting_image = State()
    confirm = State()

class DeleteFlow(StatesGroup):
    choosing_category = State()
    entering_subcategory = State()
    entering_name = State()
    confirming = State()

class EditFlow(StatesGroup):
    choosing_category = State()
    entering_subcategory = State()
    entering_name = State()
    choosing_field = State()
    entering_new_value = State()

class ViewFlow(StatesGroup):
    choosing_category = State()
    entering_subcategory = State()
    entering_name = State()

# кнопка админ
@admin_router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if not true_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add")],
        [InlineKeyboardButton(text="✏ Редактировать товар", callback_data="admin_edit")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data="admin_delete")],
        [InlineKeyboardButton(text="📦 Посмотреть товары", callback_data="admin_view")]
    ])
    await callback.message.answer("👩‍💼 Админ-панель. Выберите действие:", reply_markup=admin_keyboard)
    await callback.answer()
# кнопки с категориями 
@admin_router.callback_query(F.data == "admin_add")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍜 Еда", callback_data="cat_Еда")],
        [InlineKeyboardButton(text="🍪 Сладости и снеки", callback_data="cat_Сладости и снеки")],
        [InlineKeyboardButton(text="🧋 Напитки", callback_data="cat_Напитки")],
        [InlineKeyboardButton(text="🧴 Косметика", callback_data="cat_Косметика")],
        [InlineKeyboardButton(text="👚 Одежда", callback_data="cat_Одежда")],
        [InlineKeyboardButton(text="🎵 Альбомы", callback_data="cat_Альбомы")],
        [InlineKeyboardButton(text="📦 Прочее", callback_data="cat_Прочее")]
    ])
    await callback.message.answer("Выберите категорию товара:", reply_markup=keyboard)
    await state.set_state(AddProductFSM.waiting_main_category)
    await callback.answer()
# Добавляем новый товар на сайт (обработка кнопка "Добавить товар")
@admin_router.callback_query(F.data.startswith("cat_"))
async def process_main_category(callback: CallbackQuery, state: FSMContext):
    main_category = callback.data.split("_")[1]
    await state.update_data(main_category=main_category)
    await state.set_state(AddProductFSM.waiting_subcategory)
    await callback.message.answer("Введите подкатегорию (например, Рамён):")
    await callback.answer()
# запрашиваем  данные у пользователя 
@admin_router.message(AddProductFSM.waiting_subcategory)
async def process_subcategory(message: Message, state: FSMContext):
    await state.update_data(subcategory=message.text)
    await state.set_state(AddProductFSM.waiting_name)
    await message.answer("Введите название товара:")

@admin_router.message(AddProductFSM.waiting_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductFSM.waiting_price)
    await message.answer("Введите цену товара:")
# Проверка на число (цена), запрос фото
@admin_router.message(AddProductFSM.waiting_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❗ Пожалуйста, введите число (цену)")
        return
    await state.update_data(price=price)
    await state.set_state(AddProductFSM.waiting_image)
    await message.answer("Пришлите изображение товара (фото):")
# Подтверждение введенных данных перед отправкой на сайт
@admin_router.message(AddProductFSM.waiting_image, F.photo)
async def process_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    bot = Bot(token=BOT_TOKEN)
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    await state.update_data(image_url=image_url)
    await state.update_data(image_file_id=file_id)
    data = await state.get_data()
    preview_text = (
        f"📦 <b>{data['name']}</b>\n"
        f"💲 <b>{data['price']}₽</b>\n"
        f"🗂 <b>{data['main_category']} > {data['subcategory']}</b>\n\n"
        "Подтвердите добавление товара:"
    )
    confirm_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_add"),
         InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_add")]
    ])
    await message.answer_photo(photo=file_id, caption=preview_text, parse_mode="HTML", reply_markup=confirm_markup)
    await state.set_state(AddProductFSM.confirm)

@admin_router.callback_query(F.data == "confirm_add")
async def confirm_add_product(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_product(
        name=data["name"],
        price=data["price"],
        image_url=data["image_url"],
        file_id=data["image_file_id"],
        category=f"{data['main_category'].strip()} > {data['subcategory'].strip()}"
    )

    save_to_site({
        "name": data["name"],
        "price": data["price"],
        "image_url": data["image_url"],
        "file_id": data["image_file_id"],  
        "category": data["main_category"],
        "subcategory": data["subcategory"]
    })
    await callback.message.edit_caption("✅ Товар добавлен в базу и на сайт.") # проверить 
    await state.clear()
    await callback.answer()
#  разобраться 
@admin_router.callback_query(F.data == "cancel_add")
async def cancel_add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_caption("❌ Добавление товара отменено.")
    await state.clear()
    await callback.answer()
# Удаление товара (обработка кнопка "Удалить товар")
@admin_router.callback_query(F.data == "admin_delete")
async def start_deleting(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Выберите категорию товара:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=cat, callback_data=f"del_cat_{cat}")]
                for cat in ["Еда", "Сладости и снеки", "Напитки", "Косметика", "Одежда", "Альбомы", "Прочее"]
            ]
        )
    )
    await state.set_state(DeleteFlow.choosing_category)
    await callback.answer()
# запрашиваем  данные у пользователя 
@admin_router.callback_query(DeleteFlow.choosing_category, F.data.startswith("del_cat_"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("del_cat_", "")
    await state.update_data(category=category)
    await callback.message.answer("Введите подкатегорию:")
    await state.set_state(DeleteFlow.entering_subcategory)
    await callback.answer()

@admin_router.message(DeleteFlow.entering_subcategory)
async def get_subcategory(message: Message, state: FSMContext):
    await state.update_data(subcategory=message.text)
    await message.answer("Введите название товара:")
    await state.set_state(DeleteFlow.entering_name)
# Проверка на удаление 
@admin_router.message(DeleteFlow.entering_name)
async def confirm_deletion(message: Message, state: FSMContext):
    data = await state.get_data()
    category = f"{data['category']} > {data['subcategory']}"
    name = message.text
    for prod in get_all_products():
        pid, pname, price, url, file_id, cat = prod
        if pname.lower() == name.lower() and cat == category:
            await state.update_data(
                to_delete_id=pid,
                to_delete_title=pname  
            )
            text = f"Вы уверены, что хотите удалить товар:\n<b>{pname}</b>\n💰 {price}₽\n🗂 {cat}"
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Удалить", callback_data="confirm_delete")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")]
            ])
            try:
                await message.answer_photo(photo=file_id, caption=text, parse_mode="HTML", reply_markup=markup)
            except:
                await message.answer(text, parse_mode="HTML", reply_markup=markup)
            await state.set_state(DeleteFlow.confirming)
            return
    await message.answer("❌ Товар не найден. Попробуйте снова.")

# удаление товара из базы данных 
@admin_router.callback_query(DeleteFlow.confirming, F.data == "confirm_delete")
async def do_delete(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_title = data["to_delete_title"]
    delete_product_by_title(product_title)
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://darigii.pythonanywhere.com/delete",
            json={"title": product_title}
        )
    if res.status_code == 200 and res.json().get("success"):
        await callback.message.answer(f"✅ Товар «{product_title}» удалён из базы и с сайта.")
    else:
        await callback.message.answer("На сайте удалить не удалось, но локально удалено.")
    await state.clear()
    await callback.answer()

@admin_router.callback_query(DeleteFlow.confirming, F.data == "cancel_delete")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Удаление отменено.")
    await callback.answer()
    await state.clear()

# Обработка кнопки редактирования товара 
@admin_router.callback_query(F.data == "admin_edit")
async def start_edit(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"edit_cat:{cat}")]
        for cat in ["🍜 Еда", "🍪 Сладости и снеки", "🧋 Напитки", "🧴 Косметика", "👚 Одежда", "🎵 Альбомы", "📦 Прочее"]
    ])
    await callback.message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(EditFlow.choosing_category)
    await callback.answer()
# запрашиваем  данные у пользователя 
@admin_router.callback_query(EditFlow.choosing_category, F.data.startswith("edit_cat:"))
async def handle_edit_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("edit_cat:")[1]
    await state.update_data(category=category)
    await callback.message.answer("Введите подкатегорию:")
    await state.set_state(EditFlow.entering_subcategory)
    await callback.answer()

@admin_router.message(EditFlow.entering_subcategory)
async def enter_name_to_edit(message: Message, state: FSMContext):
    await state.update_data(subcategory=message.text.strip())
    await message.answer("Введите название товара, который хотите изменить:")
    await state.set_state(EditFlow.entering_name)

@admin_router.message(EditFlow.entering_name)
async def choose_edit_field(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text.strip())
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название", callback_data="edit_field:name")],
        [InlineKeyboardButton(text="Цена", callback_data="edit_field:price")],
        [InlineKeyboardButton(text="Фото", callback_data="edit_field:image")]
    ])
    await message.answer("Что вы хотите изменить?", reply_markup=keyboard)
    await state.set_state(EditFlow.choosing_field)

@admin_router.callback_query(EditFlow.choosing_field, F.data.startswith("edit_field:"))
async def enter_new_value(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]
    await state.update_data(field_to_edit=field)
    if field == "image":
        await callback.message.answer("Отправьте новое изображение.")
    elif field == "price":
        await callback.message.answer("Введите новую цену:")
    else:
        await callback.message.answer("Введите новое название:")
    await callback.answer()
    await state.set_state(EditFlow.entering_new_value)
# редактирование товара в базе
@admin_router.message(EditFlow.entering_new_value)
async def apply_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["field_to_edit"]
    old_title = data["product_name"]
    category = f"{data['category']} > {data['subcategory']}"
    if field == "image":
        if not message.photo:
            await message.answer("Пожалуйста, отправьте изображение.")
            return
        file_id = message.photo[-1].file_id
        bot = Bot(token=BOT_TOKEN)
        file = await bot.get_file(file_id)
        image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        with sqlite3.connect("database/db.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET file_id = ?, image_url = ? WHERE name = ? AND category = ?",
                (file_id, image_url, old_title, category)
            )
            conn.commit()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://darigii.pythonanywhere.com/update_product",
                json={
                    "title": old_title,
                    "category": category,
                    "image_url": image_url,
                    "file_id": file_id
                }
            )

    else:
        # проверка 
        new_value = message.text.strip()
        if field == "price" and not new_value.isdigit():
            await message.answer("Цена должна быть числом.")
            return
        with sqlite3.connect("database/db.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE products SET {field} = ? WHERE name = ? AND category = ?",
                (new_value, old_title, category)
            )
            conn.commit()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://darigii.pythonanywhere.com/update_product",
                json={
                    "title": old_title,
                    "category": category,
                    "field": field,
                    "new_value": new_value
                }
            )
    if res.status_code == 200 and res.json().get("success"):
        await message.answer("✅ Товар успешно обновлён в базе и на сайте.")
    else:
        await message.answer("⚠️ В базе обновлено, но на сайт не получилось отправить.")

    await state.clear()

# Просмотр товара
@admin_router.callback_query(F.data == "admin_view")
async def start_viewing(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"view_cat:{cat}")]
        for cat in ["🍜 Еда", "🍪 Сладости и снеки", "🧋 Напитки", "🧴 Косметика", "👚 Одежда", "🎵 Альбомы", "📦 Прочее"]
    ])
    await callback.message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(ViewFlow.choosing_category)
    await callback.answer()
# запрашиваем  данные у пользователя 
@admin_router.callback_query(ViewFlow.choosing_category, F.data.startswith("view_cat:"))
async def view_choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("view_cat:")[1]
    await state.update_data(category=category)
    await callback.message.answer("Введите подкатегорию:")
    await state.set_state(ViewFlow.entering_subcategory)
    await callback.answer()

@admin_router.message(ViewFlow.entering_subcategory)
async def view_subcategory(message: Message, state: FSMContext):
    await state.update_data(subcategory=message.text.strip())
    await message.answer("Введите название товара:")
    await state.set_state(ViewFlow.entering_name)
# берем товар с сайта и отправляем пользователю 
@admin_router.message(ViewFlow.entering_name)
async def view_product_info(message: Message, state: FSMContext):
    data = await state.get_data()
    category = f"{data['category']} > {data['subcategory']}"
    title = message.text.strip()
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get("https://darigii.pythonanywhere.com/products")
            products_data = res.json()
        except Exception as e:
            await message.answer("❌ Не удалось получить данные с сайта.")
            await state.clear()
            return
    # Ищем нужный товар
    product = None
    cat_data = products_data.get(data['category'], {}).get(data['subcategory'], [])
    for item in cat_data:
        if item["name"].lower() == title.lower():
            product = item
            break
    if not product:
        await message.answer("❌ Товар не найден.")
        await state.clear()
        return
    caption = (
        f"📦 <b>{product['name']}</b>\n"
        f"💰 <b>{product['price']}₽</b>\n"
        f"🗂 <b>{category}</b>"
    )
    try:
        file_id = product.get("file_id", "")
        if file_id:
            await message.answer_photo(
                photo=file_id,
                caption=caption,
                parse_mode="HTML"
            )
        else:
            raise ValueError("no image")
    except Exception:
        await message.answer("У товара нет изображения.\n\n" + caption, parse_mode="HTML")
    await state.clear()
