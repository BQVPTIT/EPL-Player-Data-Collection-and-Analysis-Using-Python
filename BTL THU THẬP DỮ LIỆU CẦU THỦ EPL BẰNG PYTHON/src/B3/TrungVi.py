import pandas as pd
import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
DB_NAME = 'player_data1.sqlite'

# Kết nối database và đọc dữ liệu
conn = sqlite3.connect(DB_NAME)

# Đọc dữ liệu từ bảng player_data1 vào DataFrame
data = pd.read_sql_query("SELECT * FROM player_data1", conn)

# Đóng kết nối database
conn.close()

# Chuyển đổi tất cả các cột có thể sang kiểu số
numeric_df = data.copy()
for col in data.columns:
    # Bỏ qua các cột không cần chuyển đổi
    if col not in ['Player', 'Nation', 'Squad', 'Pos']:
        # Thử chuyển đổi cột sang kiểu số
        try:
            # Xử lý chuỗi có dấu phẩy và các ký tự đặc biệt
            numeric_df[col] = numeric_df[col].replace('N/a', pd.NA)
            numeric_df[col] = pd.to_numeric(numeric_df[col].astype(str).str.replace(',', ''), errors='coerce')
        except:
            continue

# Chọn các cột số sau khi đã chuyển đổi
number_attributes = numeric_df.select_dtypes(include=[float, int])

# Khởi tạo từ điển kết quả với cột "Team"
results = {"Team": ["all"]}

# Khởi tạo các list cho các chỉ số thống kê
for col in number_attributes.columns:
    # Tính toán cho toàn bộ giải đấu trung bình, trung vị, độ lệch chuẩn
    results[f"Median of {col}"] = [f"{number_attributes[col].median(skipna=True):.2f}"]
    results[f"Mean of {col}"] = [f"{number_attributes[col].mean(skipna=True):.2f}"]
    results[f"Std of {col}"] = [f"{number_attributes[col].std(skipna=True):.2f}"]

# Nhóm dữ liệu theo từng đội bóng và tính các chỉ số thống kê
for squad, group in data.groupby("Squad"):
    results["Team"].append(squad)
    for col in number_attributes.columns:
        # Lọc dữ liệu cho đội hiện tại
        team_data = number_attributes[col][data['Squad'] == squad]
        # Thêm các chỉ số thống kê cho đội
        results[f"Median of {col}"].append(f"{team_data.median(skipna=True):.2f}")
        results[f"Mean of {col}"].append(f"{team_data.mean(skipna=True):.2f}")
        results[f"Std of {col}"].append(f"{team_data.std(skipna=True):.2f}")

# Chuyển kết quả thành DataFrame
results_df = pd.DataFrame(results)

# Lưu kết quả
results_df.to_csv("results2.csv", index=False)
print("Đã tính toán và lưu kết quả thống kê thành công!")