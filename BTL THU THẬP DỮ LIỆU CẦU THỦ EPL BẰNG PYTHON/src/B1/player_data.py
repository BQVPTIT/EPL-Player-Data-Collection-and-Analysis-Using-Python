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

merged_dataframe = pd.DataFrame()
goalkeeping_dataframe = pd.DataFrame()
DB_NAME = 'player_data1.sqlite'

table_links = {
# Các bảng Advanced Goalkeeping, Pass Types, Playing Time, Miscellaneous không sử dụng
    'Standard Stats': ('https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats', 'stats_standard'),
    'Goalkeeping': ('https://fbref.com/en/comps/9/2024-2025/keepers/2024-2025-Premier-League-Stats', 'stats_keeper'),
    'Shooting': ('https://fbref.com/en/comps/9/2024-2025/shooting/2024-2025-Premier-League-Stats', 'stats_shooting'),
    'Passing': ('https://fbref.com/en/comps/9/2024-2025/passing/2024-2025-Premier-League-Stats', 'stats_passing'),
    'Goal and Shot Creation': ('https://fbref.com/en/comps/9/2024-2025/gca/2024-2025-Premier-League-Stats', 'stats_gca'),
    'Defense': ('https://fbref.com/en/comps/9/2024-2025/defense/2024-2025-Premier-League-Stats', 'stats_defense'),
    'Possession': ('https://fbref.com/en/comps/9/2024-2025/possession/2024-2025-Premier-League-Stats', 'stats_possession'),
}

# Danh sách thuộc tính tự lựa chọn của từng bảng:
required_columns = [
    #Trong bảng Standard Stats:
    'Player', 'Nation', 'Squad', 'Pos', 'Age', 'Playing Time Min', 'Playing Time MP', 'Playing Time Starts',
    'Performance Gls', 'Performance Ast', 'Performance Crdy', 'Performance Crdr',
    'Expected xG', 'Expected xAG', 'Progression PrgC', 'Progression PrgP', 'Progression PrgR',
    'Per 90 Minutes Gls', 'Per 90 Minutes Ast', 'Per 90 Minutes xG', 'Per 90 Minutes xAG',
    #Trong bảng Goalkeeping:
    'Performance GA90', 'Performance Save%', 'Performance CS%', 'Penalty Kicks Save%',
    #Trong bảng Shooting:
    'Standard SoT%', 'Standard SoT/90', 'Standard G/Sh', 'Standard Dist',
    #Trong bảng Passing:
    'Total Cmp', 'Total Cmp%', 'Total TotDist', 'Short Cmp', 'Medium Cmp', 'Long Cmp',
    'KP', 'Passing 1/3', 'PPA', 'CrSPA', 'PrgP',
    #Trong bảng Goal and Shot Creation:
    'SCA', 'SCA SCA90', 'GCA', 'GCA GCA90',
    #Trong bảng Defense:
    'Tackles Tkl', 'Tackles TklW', 'Challenges Att', 'Challenges Lost',
    'Blocks', 'Blocks Sh', 'Blocks Pass', 'Int',
    #Trong bảng Possession:
    'Touches', 'Touches Def Pen', 'Touches Def 3rd', 'Touches Mid 3rd', 'Touches Att 3rd', 'Touches Att Pen',
    'Take-Ons Att', 'Take-Ons Succ%', 'Take-Ons Tkld%',
    'Carries', 'Carries PrgDist', 'Carries PrgC', 'Carries 1/3', 'Carries CPA', 'Carries Mis', 'Carries Dis',
    'Receiving Rec', 'Receiving PrgR',
]

#Cào dữ liệu trên fbref.com:
def scrape_fbref():
    #Thu thập dữ liệu thống kê cầu thủ từ FBref bằng Selenium, khởi tạo Webdriver:
    global merged_dataframe, goalkeeping_dataframe
    options = webdriver.ChromeOptions()
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Lỗi khởi tạo WebDriver: {e}")
        return False
    # Duyệt qua từng bảng thống kê, với mỗi bảng truy cập url tương ứng:
    for name, (url, table_id) in table_links.items():
        print(f'\nĐang cào bảng: {name} (ID: {table_id})')
        driver.get(url)
        time.sleep(2) 
        try:
            # Chờ bảng chính được tải:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, table_id)))
        except Exception as e:
            print(f'Lỗi (Timeout) load bảng {name} hoặc không tìm thấy ID: {e}')
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', id=table_id)
        if table is None:
            print(f"Lỗi: Không tìm thấy thẻ 'table' với id='{table_id}' cho bảng {name}")
            continue
        try:
            dataframe = pd.read_html(StringIO(str(table)))[0]
        except ValueError:
            print(f"Lỗi: Không thể đọc bảng {name} bằng pandas.")
            continue

        # Xử lý MultiIndex thành cột đơn:
        if isinstance(dataframe.columns, pd.MultiIndex):
            new_cols = []
            for col in dataframe.columns:
                group = col[0].strip() if col[0].strip() and 'Unnamed' not in col[0] else ''
                subgroup = col[1].strip() if col[1].strip() else col[0].strip()
                col_name = f"{group} {subgroup}" if group and group != subgroup else subgroup
                new_cols.append(col_name.strip())
            dataframe.columns = new_cols
        else:
            dataframe.columns = [col.strip() for col in dataframe.columns]

        # Tìm và chuẩn hóa cột Player:
        player_col = next((col for col in dataframe.columns if 'player' in col.lower() and 'rk' not in col.lower()), None)
        if not player_col:
            print(f"Lỗi: Không tìm thấy cột 'Player' trong {name}")
            continue
        dataframe = dataframe.loc[dataframe[player_col].notna() & (dataframe[player_col] != player_col)].drop_duplicates(subset=player_col)
        dataframe = dataframe.rename(columns={player_col: 'Player'})
        # Xử lý đổi tên cột đặc biệt:
        if name == 'Passing' and '1/3' in dataframe.columns:
            dataframe = dataframe.rename(columns={'1/3': 'Passing 1/3'})
        # Cột G-xG thường có trong bảng 'Expected', nếu có thì chuẩn hóa tên:
        if 'G-xG' in dataframe.columns:
             dataframe = dataframe.rename(columns={'G-xG': 'Expected G-xG'})
        # Hợp nhất các bảng:
        if name == 'Goalkeeping':
            goalkeeping_dataframe = dataframe.copy()
        else:
            if merged_dataframe.empty:
                merged_dataframe = dataframe
            else:
                # Loại bỏ các cột trùng lặp (trừ cột 'Player') trước khi merge:
                cols_to_drop = [col for col in dataframe.columns if col in merged_dataframe.columns and col != 'Player']
                dataframe = dataframe.drop(columns=cols_to_drop, errors='ignore')
                merged_dataframe = pd.merge(merged_dataframe, dataframe, on='Player', how='outer')
    driver.quit()
    print("\n--- Hoàn thành cào dữ liệu fbref.com ---")
    return True

# Thực hiện lọc cầu thủ > 90 phút và xử lý dữ liệu thủ môn:
def clean_and_merge_data():
    global merged_dataframe, goalkeeping_dataframe
    # 1. Lọc cầu thủ theo 'Playing Time Min' > 90 ở tất cả các vị trí:
    min_col = next((col for col in merged_dataframe.columns if 'playing time min' in col.lower()), None)
    if min_col:
        merged_dataframe = merged_dataframe[merged_dataframe[min_col].notna()].copy()
        try:
            merged_dataframe.loc[:, min_col] = merged_dataframe[min_col].astype(str).str.replace(',', '', regex=False).astype(float) 
            merged_dataframe = merged_dataframe[merged_dataframe[min_col] > 90].copy()
            print(f"Lọc được {len(merged_dataframe)} cầu thủ chơi > 90 phút.")
        except Exception as e:
            print(f"Lỗi lọc 'Playing Time Min': {e}")
            return False
    else:
        print("Lỗi: Không tìm thấy cột 'Playing Time Min'")
        return False

    # 2. Xử lý dữ liệu thủ môn và merge GK:
    if not goalkeeping_dataframe.empty:
        pos_col = next((col for col in merged_dataframe.columns if 'pos' in col.lower()), None)
        if pos_col:
            # Chỉ giữ lại thủ môn đã chơi > 90 phút:
            goalkeeping_dataframe = goalkeeping_dataframe[goalkeeping_dataframe['Player'].isin(merged_dataframe['Player'])].copy()
            # Lấy vị trí từ bảng chính để lọc chỉ số thủ môn:
            pos_mapping = merged_dataframe.set_index('Player')[pos_col].to_dict()
            # Loại bỏ các chỉ số thủ môn nếu cầu thủ là tiền đạo, tiền vệ, hậu vệ:
            for col in goalkeeping_dataframe.columns:
                if col not in ['Player', 'Pos']:
                    goalkeeping_dataframe.loc[:, col] = goalkeeping_dataframe.apply(
                        lambda row: row[col] if 'GK' in pos_mapping.get(row['Player'], '') else pd.NA, axis=1
                    )
            cols_to_drop_keeper = [col for col in goalkeeping_dataframe.columns if col in merged_dataframe.columns and col != 'Player']
            goalkeeping_dataframe.drop(columns=cols_to_drop_keeper, inplace=True, errors='ignore')
            # Merge dữ liệu thủ môn vào bảng chính
            merged_dataframe = pd.merge(merged_dataframe, goalkeeping_dataframe, on='Player', how='left')
            print(f"Đã xử lý dữ liệu thủ môn.")
        else:
            print("Lỗi: Không tìm thấy cột 'Pos' để xử lý dữ liệu thủ môn")

    # 3. Chọn và sắp xếp các cột cuối cùng
    available_columns = [col for col in required_columns if col in merged_dataframe.columns]
    must_have = ['Player', 'Nation', 'Squad', 'Pos', 'Age']
    final_columns = must_have + [col for col in available_columns if col not in must_have]
    # Giữ lại các cột có trong danh sách final_columns bắt buộc phải có
    merged_dataframe = merged_dataframe[[col for col in final_columns if col in merged_dataframe.columns]]
    # Điền giá trị thiếu bằng 'N/a' theo yêu cầu
    merged_dataframe.fillna('N/a', inplace=True) 
    return True

#Ghi ra player_data1.sqlite3
if __name__ == "__main__":
    if scrape_fbref():
        if clean_and_merge_data():
            conn = sqlite3.connect(DB_NAME)
            merged_dataframe.to_sql('player_data1', conn, if_exists='replace', index=False)
            conn.close()
            print("Ghi cầu thủ vào bảng player_data1.sqlite thành công!")
