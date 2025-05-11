from flask import Flask, jsonify
from flask_cors import CORS       # ← добавь эту строку
import sqlite3

app = Flask(__name__)
CORS(app)                         # ← и сразу после этого

@app.route("/products")
def get_products():
    with sqlite3.connect("database/db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, image_url, category FROM products")
        rows = cursor.fetchall()

    products = [
        {"name": row[0], "price": row[1], "image_url": row[2], "category": row[3]}
        for row in rows
    ]
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)


