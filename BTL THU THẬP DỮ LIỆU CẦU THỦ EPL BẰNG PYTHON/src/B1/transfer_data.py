import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sqlite3
import time

#Đọc từ player_data1.sqlite
DB_NAME = 'player_data1.sqlite'
conn = sqlite3.connect(DB_NAME)

#Chọn cột Player từ player_data1.sqlite
player_list = pd.read_sql("SELECT Player FROM player_data1", conn)
conn.close()
players_i1 = player_list["Player"].drop_duplicates().tolist()
print(f"Đọc được {len(players_i1)} cầu thủ từ bảng player_data1.sqlite")

#Cấu hình bằng Selenium sử dụng Chrome:
options = webdriver.ChromeOptions()
#Tự động tải phiên bản Chrome phù hợp và đảm bảo rằng phiên bản cài đặt phù hợp, nếu lỗi thì in thông báo:
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

players = []
prices = []
#Duyệt qua 16 trang cầu thủ có giá chuyển nhượng trong mùa giải 2024-2025 tại Ngoại hạng Anh
for page in range(1, 17):
    if page == 1:
        url = "https://www.footballtransfers.com/en/transfers/confirmed/most-recent/2024-2025/uk-premier-league"
    elif(page >= 2):
        url = f"https://www.footballtransfers.com/en/transfers/confirmed/most-recent/2024-2025/uk-premier-league/{page}"
    print(f"Đang cào trang {page}")
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody#player-table-body")))
    except:
        print(f"Không tìm thấy bảng dữ liệu ở trang {page}")
        continue

#Sử dụng BeautifulSoup trích xuất HTML và xử lý dữ liệu:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("tbody#player-table-body tr")
    for row in rows:
        name_tag = row.select_one("td.td-player span.d-none")
        player_name = name_tag.get_text(strip=True) if name_tag else "N/a"
        price_tag = row.select_one("td.td-price span")
        price = price_tag.get_text(strip=True) if price_tag else "N/a"
        if player_name != "N/a":
            players.append(player_name)
            prices.append(price)
driver.quit()

# Gộp thêm bảng player_data1.sqlite3:
df_transfer = pd.DataFrame({
    "Player": players,
    "Price": prices
}).drop_duplicates(subset="Player")
print(f"Cào được tổng cộng là {len(df_transfer)} cầu thủ có dữ liệu giá chuyển nhượng")
final_df = pd.merge(player_list, df_transfer, on="Player", how="left")
# Điền các cầu thủ không có giá bằng 'N/a'
final_df["Price"] = final_df["Price"].fillna("N/a")
print(f"Tổng số cầu thủ: {len(final_df)}")

#Ghi ra player_transfer_data.sqlite3
conn = sqlite3.connect(DB_NAME)
final_df.to_sql("player_transfer_data", conn, if_exists="replace", index=False)
conn.close()
print("Ghi giá chuyển nhượng vào bảng player_transfer_data.sqlite thành công!")
