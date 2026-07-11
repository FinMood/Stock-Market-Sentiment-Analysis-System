import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pandas as pd
import requests


# ============================
# 股票清單
# ============================

from get_0050_stocks import get_0050_stocks

df_clean = get_0050_stocks(csv_path="source/0050.csv")
stock_list = df_clean["商品代碼"].str.strip().tolist()

# ============================
# FinMind API
# ============================

url = "https://api.finmindtrade.com/api/v4/data"


# ============================
# 日期切割
# ============================

def generate_date_range(start_date, end_date):
    dates = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start = start + timedelta(days=1)
    return dates

dates = generate_date_range(
    "2026-02-23",
    "2026-06-23"
)


# ============================
# 抓單一天新聞 (多執行緒安全重試版)
# ============================
def get_news(task):
    stock_id, date = task
    parameter = {
        "dataset": "TaiwanStockNews",
        "data_id": stock_id,
        "start_date": date,
        "end_date": date,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    attempt = 1
    while True:  # 🚀 無限循環防護：沒拿到資料前，這個執行緒絕對不放手
        try:
            # 🚀 設定 timeout=5秒。5秒沒回應立刻判定卡死，中斷並重試
            response = requests.get(
                url, params=parameter, headers=headers, timeout=5
            )

            # 情況 A：被 API 限流 (429 Too Many Requests)
            if response.status_code == 429:
                # 多執行緒猛轟一定會遇到這個，原地退後休眠 8 秒再試
                time.sleep(8)
                attempt += 1
                continue

            # 情況 B：正常取得資料 (200)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data.get("data", []))

                if not df.empty:
                    df["stock_id"] = stock_id
                    print(f"⚡ [成功] {stock_id} {date} -> {len(df)} 筆")
                    return df
                else:
                    # 當天真的沒有新聞，回傳空 DataFrame (這是正確資料，非失敗)
                    return pd.DataFrame()

            # 情況 C：遭遇其他伺服器錯誤 (500, 502 等)
            time.sleep(3)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            # 🚀 解決您之前卡死在 2308 的元兇：5秒一到立刻強行切斷，休眠 2 秒後由同個執行緒重新發起
            print(f"❌ [卡死超時重試] {stock_id} {date} 沒反應，重新請求...")
            time.sleep(2)

        except Exception as e:
            time.sleep(2)

        attempt += 1


# ============================
# 建立下載任務
# ============================

tasks = []

for stock in stock_list:
    for date in dates:
        tasks.append(
            (
                stock,
                date
            )
        )

print(
    "下載任務數:",
    len(tasks)
)



# ============================
# ThreadPool
# 增加cpu的執行緒加快資料抓取
# ============================

with ThreadPoolExecutor(
    max_workers=5
) as executor:
    result = list(
        executor.map(
            get_news,
            tasks
        )
    )


# ============================
# 合併
# ============================

# 濾掉空的表格，加快合併速度
result = [df for df in result if not df.empty]

if result:
    news_df = pd.concat(result, ignore_index=True)

# ============================
# 儲存
# ============================

# 建立資料夾路徑
    output_folder = "source"

    os.makedirs(output_folder, exist_ok=True)

# 完整檔案路徑
    output_file = os.path.join(output_folder, "TaiwanStockNews.csv")

    news_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("===================")
    print("完成", len(news_df), "筆新聞")
else:
    print("===================")
    print("❌ 累計未抓到任何有效新聞")