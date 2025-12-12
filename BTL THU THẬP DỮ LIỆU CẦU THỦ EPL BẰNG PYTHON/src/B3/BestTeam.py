import pandas as pd
import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
DB_NAME = 'player_data1.sqlite'

# Kết nối database và đọc dữ liệu
conn = sqlite3.connect(DB_NAME)

# Đọc dữ liệu từ bảng player_data1 vào DataFrame
df = pd.read_sql_query("SELECT * FROM player_data1", conn)

# Đóng kết nối database
conn.close()

# Chuyển đổi tất cả các cột có thể sang kiểu số
for col in df.columns:
    # Bỏ qua các cột không cần chuyển đổi
    if col not in ['Player', 'Nation', 'Squad', 'Pos']:
        # Thử chuyển đổi cột sang kiểu số
        try:
            df[col] = df[col].replace('N/a', pd.NA)
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        except:
            continue

# Nhóm dữ liệu theo cột 'Squad'
teams = df.groupby('Squad')
# Khởi tạo DataFrame rỗng để lưu kết quả
best_teams = pd.DataFrame(columns=['Attribute', 'Best Team', 'Value'])
# Lọc ra các cột chứa dữ liệu dạng số
number_columns = df.select_dtypes(include=[float, int]).columns

# Tìm đội có điểm số cao nhất cho từng chỉ số
for column in number_columns:
    # Tính giá trị trung bình của mỗi đội cho cột đang xét
    team_means = teams[column].mean()
    # Loại bỏ các giá trị NaN
    team_means = team_means.dropna()
    if not team_means.empty:
        best_team = team_means.idxmax()
        best_value = team_means.max()

        # Tạo một hàng dữ liệu mới
        row = pd.DataFrame({'Attribute': [column], 'Best Team': [best_team], 'Value': [f"{best_value:.2f}"]})
        # Thêm hàng này vào best_teams
        best_teams = pd.concat([best_teams, row], ignore_index=True)

# In kết quả ra màn hình
print("Kết quả thống kê:")
print(best_teams)

# Lưu kết quả vào file CSV
best_teams.to_csv('results_BestTeam.csv', index=False)
print("\nĐã lưu kết quả vào file 'results_BestTeam.csv'")