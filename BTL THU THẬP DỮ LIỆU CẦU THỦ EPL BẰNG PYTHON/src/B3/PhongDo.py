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
    if col not in ['Player', 'Nation', 'Squad', 'Pos']:
        try:
            df[col] = df[col].replace('N/a', pd.NA)
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        except:
            continue

teams = df.groupby("Squad")

# Các chỉ số tấn công và phòng ngự
attack_metrics = ['Performance Gls', 'Performance Ast', 'Expected xG', 'Expected xAG', 'Per 90 Minutes Gls', 'Per 90 Minutes Ast']
defensive_metrics = ['Tackles Tkl', 'Tackles TklW', 'Touches Def 3rd', 'Touches Att 3rd', 'Blocks', 'Blocks Sh', 'Blocks Pass']

# Tính trung bình các chỉ số tấn công và phòng ngự cho từng đội
team_attack_performance = teams[attack_metrics].mean().mean(axis=1)
team_defensive_performance = teams[defensive_metrics].mean().mean(axis=1) / 100

# Tạo bảng tổng hợp điểm phong độ
team_performance = pd.DataFrame({
    'Attack Performance': team_attack_performance,
    'Defensive Performance': team_defensive_performance
})

# Tính điểm phong độ chung bằng trung bình cộng của điểm tấn công và phòng ngự
team_performance['Overall Performance'] = team_performance.mean(axis=1)

# Định dạng các cột số với 2 chữ số thập phân
for col in team_performance.columns:
    team_performance[col] = team_performance[col].apply(lambda x: f"{x:.2f}")

# Sắp xếp theo thứ tự giảm dần của điểm phong độ chung
team_performance = team_performance.sort_values(by='Overall Performance', ascending=False)

# Lưu kết quả vào file results_PhongDo.csv
team_performance.to_csv('results_PhongDo.csv')

print("\nĐiểm phong độ của các đội bóng:")
print(team_performance)

# Tìm đội có phong độ cao nhất
best_team = team_performance.index[0]
best_team_score = float(team_performance.iloc[0]['Overall Performance'])

print(f"\nĐội bóng có phong độ tốt nhất của giải bóng đá Ngoại Hạng Anh mùa 2024-2025 là: {best_team}")
print(f"Với các chỉ số:")
print(f"- Điểm tấn công: {team_performance.loc[best_team, 'Attack Performance']}")
print(f"- Điểm phòng ngự: {team_performance.loc[best_team, 'Defensive Performance']}")
print(f"- Điểm tổng hợp: {team_performance.loc[best_team, 'Overall Performance']}")