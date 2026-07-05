# 沒辦法運作

import requests
import pandas as pd

from crawler.worker import app

stock_id = [2330]

@app.task()
def crawler_finmind_news(stock_id):
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockNews",
        "data_id": stock_id,
        "start_date": "2026-06-23",
        "end_date": "2026-07-01",
    }
    resp = requests.get(url, params=parameter)
    data = resp.json()
    if resp.status_code == 200:
        df = pd.DataFrame(data["data"])
        print(df)
        df.to_csv(f"finmind_{stock_id}.csv", index=False, encoding='utf-8-sig')
    else:
        print(data["msg"])

if __name__ == "__main__":
    print("🚀 正在發送爬蟲任務給 Celery...")
    
    # 這裡要把 [2330] 當作參數傳給 .delay()
    crawler_finmind_news.delay(stock_id=[2330])
    
    print("✅ 任務已成功送入 RabbitMQ 佇列！")