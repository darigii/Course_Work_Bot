from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
app = Flask(__name__)
CORS(app, supports_credentials=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "db.sqlite3")

@app.route("/products")
def get_products():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, image_url, file_id, category FROM products")
        rows = cursor.fetchall()

    structured = {}
    for name, price, image_url, file_id, category_str in rows:
        try:
            main_cat, sub_cat = category_str.split(" > ")
        except ValueError:
            main_cat, sub_cat = category_str, "Без подкатегории"

        structured.setdefault(main_cat, {})
        structured[main_cat].setdefault(sub_cat, [])  # ← важно!
        structured[main_cat][sub_cat].append({
            "name": name,
            "price": price,
            "image_url": image_url,
            "file_id": file_id
        })

    return jsonify(structured)

@app.route("/add", methods=["POST"])
def add_product():
    data = request.json
    name = data["name"]
    price = data["price"]
    image_url = data["image_url"]
    file_id = data["file_id"]
    main = data["category"]
    sub = data["subcategory"]
    category = f"{main.strip()} > {sub.strip()}"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, image_url, file_id, category) VALUES (?, ?, ?, ?, ?)",
            (name, price, image_url, file_id, category)
        )
        conn.commit()

    return jsonify({"status": "ok"})

@app.route("/delete", methods=["POST"])
def delete_product():
    data = request.json
    product_id = data.get("id")
    title = data.get("title")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if product_id:
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        elif title:
            cursor.execute("DELETE FROM products WHERE name = ?", (title,))
        else:
            return jsonify({"success": False, "error": "No ID or title provided"}), 400

        conn.commit()
        deleted = cursor.rowcount

    if deleted:
        return jsonify({"success": True, "deleted": deleted})
    return jsonify({"success": False, "error": "Product not found"}), 404

@app.route("/update_product", methods=["POST"])
def update_product():
    data = request.json
    title = data.get("title")
    category = data.get("category")
    image_url = data.get("image_url")
    file_id = data.get("file_id")
    field = data.get("field")
    new_value = data.get("new_value")
    if not title or not category:
        return jsonify({"success": False, "error": "Missing title or category"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        if image_url and file_id:
            cursor.execute(
                "UPDATE products SET image_url = ?, file_id = ? WHERE name = ? AND category = ?",
                (image_url, file_id, title, category)
            )

        elif field and new_value:
            if field not in ("name", "price"):
                return jsonify({"success": False, "error": "Invalid field"}), 400
            cursor.execute(
                f"UPDATE products SET {field} = ? WHERE name = ? AND category = ?",
                (new_value, title, category)
            )

        else:
            return jsonify({"success": False, "error": "No valid data provided"}), 400

        conn.commit()
        updated = cursor.rowcount

    if updated:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Product not found"}), 404

@app.route("/submit_order", methods=["POST"])
def submit_order():
    data = request.json
    cart_items = data.get("cart", [])
    cart_text = ""
    for item in cart_items:
        name = item.get("name", "товар")
        price = item.get("price", 0)
        count = item.get("count", 1)
        subtotal = price * count
        cart_text += f"• {name} × {count} = {subtotal}₽\n"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (telegram_id, name, phone, address, payment_method, cart_json, total_price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            data["telegram_id"],
            data["name"],
            data["phone"],
            data["address"],
            data["payment_method"],
            str(cart_items),
            data["total_price"]
        ))
        conn.commit()

    # Уведомление в Telegram
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        chat_id = data.get("telegram_id")
        if BOT_TOKEN and chat_id:
            text = (
                f"📦 <b>Ваш заказ подтверждён!</b>\n\n"
                f"👤 Имя: {data.get('name')}\n"
                f"📱 Телефон: {data.get('phone')}\n"
                f"🏡 Адрес: {data.get('address')}\n"
                f"💳 Оплата: {data.get('payment_method')}\n"
                f"🛒 Товары:\n{cart_text}\n"
                f"💰 Итого: {data.get('total_price')}₽"
            )
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            )
    except Exception as e:
        print("Ошибка при отправке сообщения:", e)

    return jsonify({"status": "ok"})

"""
if __name__ == "__main__":
    app.run(debug=True) # вариант для запуска на pythonanywhere
"""
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
