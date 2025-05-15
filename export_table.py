import sqlite3
import csv
conn = sqlite3.connect("database/db.sqlite3")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
with open("exported_users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns) 
    writer.writerows(rows)
conn.close()
print("✅ Данные экспортированы в exported_table.csv")
"""
@admin_router.callback_query(F.data == "admin_view")
async def view_products(callback: CallbackQuery):
    products = get_all_products()
    if not products:
        await callback.message.answer("❌ Товаров пока нет.")
        await callback.answer()
        return
    for product in products:
        name, price, image_file_id, category = product[1], product[2], product[3], product[4]
        text = f"📦 {name}\n💰 {price}₽\n🗂 Категория: {category}"
        await callback.message.answer_photo(photo=image_file_id, caption=text)
    await callback.answer()"""