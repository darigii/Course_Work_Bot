import sqlite3
from datetime import datetime
DB_PATH = "database/db.sqlite3"
# создание таблиц
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # для хранения пользователей 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                full_name TEXT,
                email TEXT,
                registered_at TEXT,
                has_discount INTEGER DEFAULT 0
            )
        """)
        # для хранения товара
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT,
                file_id TEXT,
                category TEXT
            )
        """)
        # для хранения заказов 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                phone TEXT,
                address TEXT,
                payment_method TEXT,
                cart_json TEXT,
                total_price REAL,
                created_at TEXT
            )
        """)
        conn.commit()
# получает данные пользователя из базы по его telegram id 
def get_user_by_telegram_id(telegram_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()
# регистрирует пользователя, если он ещё не существует, и сразу выдаёт скидку
def register_user(telegram_id, full_name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (telegram_id, full_name, email, registered_at, has_discount)
            VALUES (?, ?, ?, ?, 1)
        """, (telegram_id, full_name, "", datetime.now().isoformat()))
        conn.commit()
# Сохраняет email пользователя в базу по id
def save_email_to_user(telegram_id, email):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE telegram_id = ?", (email, telegram_id))
        conn.commit()
# Добавляет новый товар в таблицу products
def add_product(name, price, image_url, file_id, category):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, image_url, file_id, category) VALUES (?, ?, ?, ?, ?)",
            (name, price, image_url, file_id, category)
        )
        conn.commit()
# Возвращает список всех товаров из таблицы products
def get_all_products():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, image_url, file_id, category FROM products")
        return cursor.fetchall()
# Удаляет товар по названию и категории
def delete_product_by_details(name, subcategory, main_category):
    category = f"{main_category.strip()} > {subcategory.strip()}"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM products WHERE name = ? AND category = ?",
            (name, category)
        )
        conn.commit()
        return cursor.rowcount > 0
# Удаляет товар по точному названию из таблицы products
def delete_product_by_title(title):
    with sqlite3.connect("database/db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE name = ?", (title,))
        conn.commit()
