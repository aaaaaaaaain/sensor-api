import mysql.connector
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ── 資料庫連線設定（對應您的 XAMPP）──────────────────────
DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     3306,
    "user":     "root",
    "password": "",           # XAMPP 預設沒有密碼
    "database": "sensor_project"
}

AUTH_TOKEN = "Bearer bf963447-1e9d-4855-81fa-329e84e4bd18"

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ── 接收 Arduino 上傳的感測器資料 ─────────────────────────
@app.route("/api/sensor/upload", methods=["POST"])
def upload():
    # 驗證 Token
    if request.headers.get("Authorization") != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO sensor_data (
            pot_id, ambient_temperature, ambient_humidity,
            atmospheric_pressure, soil_moisture,
            water_flow_rate, water_level
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data["pot_id"],
        data["ambient_temperature"],
        data["ambient_humidity"],
        data["atmospheric_pressure"],
        data["soil_moisture"],
        data["water_flow_rate"],
        data["water_level"]
    ))
    db.commit()
    cursor.close()
    db.close()

    print(f"[{datetime.now()}] 收到資料：{data}")
    return jsonify({"status": "ok"}), 200

# ── 查詢最新資料（方便測試用）────────────────────────────
@app.route("/api/sensor/latest", methods=["GET"])
def latest():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM sensor_data
        ORDER BY received_at DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(rows), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)