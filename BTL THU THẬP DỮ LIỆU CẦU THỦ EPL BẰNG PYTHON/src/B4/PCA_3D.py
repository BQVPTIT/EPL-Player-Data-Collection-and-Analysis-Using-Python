import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import sqlite3
import matplotlib.pyplot as plt

# Kết nối đến cơ sở dữ liệu SQLite
DB_NAME = 'player_data1.sqlite'

# Kết nối database và đọc dữ liệu
conn = sqlite3.connect(DB_NAME)
data = pd.read_sql_query("SELECT * FROM player_data1", conn)
conn.close()

# Chọn các chỉ số quan trọng để phân tích
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

# Áp dụng PCA để giảm chiều dữ liệu xuống 3 chiều
pca = PCA(n_components=3)
principal_components = pca.fit_transform(X_scaled)

# Tính phần trăm phương sai giải thích được
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance_ratio = np.cumsum(explained_variance_ratio)

# Phân cụm với k = 3
kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, n_init=10, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

# Tạo DataFrame cho dữ liệu PCA
data_pca = pd.DataFrame(
    data=principal_components,
    columns=['Principal Component 1', 'Principal Component 2', 'Principal Component 3']
)
data_pca['Cluster'] = clusters
data_pca['Player'] = data['Player']
data_pca['Position'] = data['Pos']
data_pca['Squad'] = data['Squad']

# Tạo biểu đồ 3D
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Định nghĩa màu sắc cho từng cụm
colors = ['#FF9999', '#66B2FF', '#99FF99']

# Vẽ scatter plot 3D với màu sắc theo cụm
for i in range(3):
    cluster_data = data_pca[data_pca['Cluster'] == i]
    ax.scatter(
        cluster_data['Principal Component 1'],
        cluster_data['Principal Component 2'],
        cluster_data['Principal Component 3'],
        c=[colors[i]],
        label=f'Cụm {i+1}',
        alpha=0.6
    )
    
    # Thêm tên một số cầu thủ tiêu biểu trong mỗi cụm
    for idx, row in cluster_data.head(3).iterrows():
        ax.text(
            row['Principal Component 1'],
            row['Principal Component 2'],
            row['Principal Component 3'],
            row['Player'],
            fontsize=8,
            alpha=0.7
        )

# Thêm tiêu đề và nhãn
ax.set_title('Phân cụm cầu thủ trong không gian 3D sau khi giảm chiều dữ liệu bằng PCA', pad=20)
ax.set_xlabel(f'PC1 ({explained_variance_ratio[0]:.1%} variance)')
ax.set_ylabel(f'PC2 ({explained_variance_ratio[1]:.1%} variance)')
ax.set_zlabel(f'PC3 ({explained_variance_ratio[2]:.1%} variance)')

# Thêm legend
ax.legend(title="Phân loại cầu thủ", bbox_to_anchor=(1.05, 1), loc='upper left')

# Điều chỉnh góc nhìn
ax.view_init(elev=20, azim=45)

plt.tight_layout()
plt.show()