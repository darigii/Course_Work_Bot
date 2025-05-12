from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

# Путь до базы
DB_PATH = os.path.join("database", "db.sqlite3")

app = Flask(__name__)
CORS(app)  

@app.route("/products")
def get_products():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, image_url, category FROM products")
        rows = cursor.fetchall()

    products = [
        {
            "name": row[0],
            "price": row[1],
            "image_url": row[2],
            "category": row[3]
        }
        for row in rows
    ]
    return jsonify(products)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)


