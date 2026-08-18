# uv run python -m crawler.finmind_news.py
# 把資料存入mysql資料庫中

import os
import time
import pandas as pd
import requests

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from crawler.get_0050_stocks import get_0050_stocks
from crawler.news_repository import save_news_to_mysql

# ============================
# 股票清單
# ============================
df_clean = get_0050_stocks(csv_path="source/0050_list.csv")
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
    "2026-02-24"
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

    max_retry = 5

    for attempt in range(1, max_retry + 1):

        try:

            response = requests.get(
                url,
                params=parameter,
                headers=headers,
                timeout=5
            )

            # API 正常
            if response.status_code == 200:

                data = response.json()
                df = pd.DataFrame(data.get("data", []))

                if not df.empty:
                    df["stock_id"] = stock_id
                    print(f"⚡ [成功] {stock_id} {date} -> {len(df)} 筆")
                    return df

                # 當天沒有新聞
                return pd.DataFrame()

            # API 限流
            elif response.status_code == 429:

                print(
                    f"⚠️ 429 Too Many Requests "
                    f"{stock_id} {date} "
                    f"第 {attempt} 次重試"
                )

                time.sleep(8)

            # 其它 HTTP 錯誤
            else:

                print(
                    f"⚠️ HTTP {response.status_code} "
                    f"{stock_id} {date} "
                    f"第 {attempt} 次重試"
                )

                time.sleep(3)

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):

            print(
                f"❌ Timeout "
                f"{stock_id} {date} "
                f"第 {attempt} 次重試"
            )

            time.sleep(2)

        except Exception as e:

            print(
                f"❌ {stock_id} {date} "
                f"{type(e).__name__}: {e}"
            )

            time.sleep(2)

    print(
        f"❌ 放棄下載：{stock_id} {date}"
    )

    return pd.DataFrame()


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
with ThreadPoolExecutor(max_workers=5) as executor:
    for df in executor.map(get_news, tasks):

        # 下載與儲存分開
        if not df.empty:
            save_news_to_mysql(df)
