import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sqlite3
import matplotlib.pyplot as plt

# Kết nối đến cơ sở dữ liệu SQLite
DB_NAME = 'player_data1.sqlite'

# Kết nối database và đọc dữ liệu
conn = sqlite3.connect(DB_NAME)
data = pd.read_sql_query("SELECT * FROM player_data1", conn)
conn.close()

# Chọn các chỉ số quan trọng để phân cụm
features = [
    'Age',                      # Tuổi
    'Playing Time MP',          # Số trận đấu
    'Playing Time Min',         # Số phút thi đấu
    'Performance Gls',          # Số bàn thắng
    'Performance Ast',          # Số kiến tạo
    'Expected xG',              # Chỉ số xG
    'Expected xAG',             # Chỉ số xAG
    'Per 90 Minutes Gls',       # Bàn thắng/90 phút
    'Per 90 Minutes Ast'        # Kiến tạo/90 phút
]

# Chuẩn bị dữ liệu
X = data[features].copy()

# Xử lý dữ liệu thiếu và chuyển đổi sang kiểu số
for col in X.columns:
    X[col] = pd.to_numeric(X[col].astype(str).str.replace(',', ''), errors='coerce')
X = X.fillna(X.mean())

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Tìm k tối ưu bằng phương pháp Elbow
wcss = []
K = range(1, 11)
for k in K:
    kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=42)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

# Vẽ biểu đồ Elbow
plt.figure(figsize=(10, 6))
plt.plot(K, wcss, 'bx-')
plt.xlabel('Số lượng cụm (k)')
plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
plt.title('Phương pháp Elbow để xác định số cụm tối ưu')
plt.xticks(K)
plt.grid(True)
plt.show()