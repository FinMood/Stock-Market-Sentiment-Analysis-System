import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta


# ============================
# 股票清單
# ============================

stock_list = [
    "2330",
    "2454",
    "2308"
]


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
# 抓單一天新聞
# ============================

def get_news(task):

    stock_id, date = task

    parameter = {

        "dataset": "TaiwanStockNews",

        "data_id": stock_id,

        "start_date": date,

        "end_date": date
    }


    try:
        response = requests.get(
            url,
            params=parameter,
            timeout=10
        )


        data = response.json()


        if response.status_code == 200 and data.get("data"):
            df = pd.DataFrame(data["data"])
            df["stock_id"] = stock_id
            print(
                f"{stock_id} {date} "
                f"{len(df)}筆"
            )
            return df
        else:
            return pd.DataFrame()


    except Exception as e:
        print(
            stock_id,
            date,
            e
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

news_df = pd.concat(
    result,
    ignore_index=True
)


# ============================
# 儲存
# ============================

# 建立資料夾路徑
output_folder = "source"

os.makedirs(output_folder, exist_ok=True)

# 完整檔案路徑
output_file = os.path.join(output_folder, "TaiwanStockNews_test.csv")

news_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("===================")

print(
    "完成",
    len(news_df),
    "筆新聞"
)