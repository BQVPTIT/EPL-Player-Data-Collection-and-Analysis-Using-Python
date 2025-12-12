from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import sqlite3
import pandas as pd

app = Flask(__name__)
api = Api(app)

# Đường dẫn và tên bảng trùng với phần I.1
DB_PATH = "player_data1.sqlite"
TABLE_NAME = "player_data1"

# --- Hàm truy vấn chung ---
def query_database(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# --- API tra cứu cầu thủ ---
class PlayerLookup(Resource):
    def get(self):
        player_name = request.args.get("name")
        if not player_name:
            return {"error": "Thiếu tham số ?name=<tên cầu thủ>"}, 400

        try:
            df = query_database(
                f"SELECT * FROM {TABLE_NAME} WHERE Player LIKE ?", (f"%{player_name}%",)
            )
        except Exception as e:
            return {"error": f"Lỗi truy vấn cơ sở dữ liệu: {e}"}, 500

        if df.empty:
            return {"message": f"Không tìm thấy cầu thủ '{player_name}'"}, 404

        return df.to_dict(orient="records"), 200

# --- API tra cứu câu lạc bộ ---
class ClubLookup(Resource):
    def get(self):
        club_name = request.args.get("club")
        if not club_name:
            return {"error": "Thiếu tham số ?club=<tên câu lạc bộ>"}, 400

        try:
            df = query_database(
                f"SELECT * FROM {TABLE_NAME} WHERE Squad LIKE ?", (f"%{club_name}%",)
            )
        except Exception as e:
            return {"error": f"Lỗi truy vấn cơ sở dữ liệu: {e}"}, 500

        if df.empty:
            return {"message": f"Không tìm thấy câu lạc bộ '{club_name}'"}, 404

        return df.to_dict(orient="records"), 200

# --- Đăng ký các endpoint ---
api.add_resource(PlayerLookup, "/player")
api.add_resource(ClubLookup, "/club")

if __name__ == "__main__":
    print("Server Flask đang chạy tại http://127.0.0.1:5000")
    print("Tra cứu cầu thủ: http://127.0.0.1:5000/player?name=<Tên_cầu_thủ>")
    print("Tra cứu CLB: http://127.0.0.1:5000/club?club=<Tên_câu_lạc_bộ>")
    app.run(debug=True)

