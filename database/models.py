import sqlite3
from datetime import datetime
DB_PATH = "database/db.sqlite3"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
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
        conn.commit()

def get_user_by_telegram_id(telegram_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()
def register_user(telegram_id, full_name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (telegram_id, full_name, email, registered_at, has_discount)
            VALUES (?, ?, ?, ?, 1)
        """, (telegram_id, full_name, "", datetime.now().isoformat()))
        conn.commit()
def save_email_to_user(telegram_id, email):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE telegram_id = ?", (email, telegram_id))
        conn.commit()
