import argparse
import requests
import json
import pandas as pd

BASE_URL = "http://127.0.0.1:5000"

parser = argparse.ArgumentParser(description="Tra cứu dữ liệu cầu thủ hoặc câu lạc bộ (Premier League)")
parser.add_argument("--name", help="Tên cầu thủ cần tra cứu")
parser.add_argument("--club", help="Tên câu lạc bộ cần tra cứu")
args = parser.parse_args()

if not args.name and not args.club:
    print(" Bạn cần nhập ít nhất một tham số: --name <tên> hoặc --club <tên>")
    exit()

# Xác định endpoint và file CSV
if args.name:
    endpoint = "/player"
    params = {"name": args.name}
    filename = args.name.replace(" ", "_") + ".csv"
elif args.club:
    endpoint = "/club"
    params = {"club": args.club}
    filename = args.club.replace(" ", "_") + ".csv"

url = BASE_URL + endpoint
print(f" Đang gửi request tới: {url} với tham số {params}\n")

try:
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Lỗi truy vấn ({response.status_code})")
        print(response.text)
        exit()

    data = response.json()

    # In ra dạng pretty-printed JSON
    print("Kết quả dạng JSON:")
    print(json.dumps(data, indent=4, ensure_ascii=False))

    # Ghi ra file CSV (nếu có dữ liệu)
    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"\n Đã lưu kết quả vào file: {filename}")
    else:
        print("Không có dữ liệu để lưu vào CSV.")

except requests.exceptions.RequestException as e:
    print(f" Lỗi khi gửi request: {e}")


