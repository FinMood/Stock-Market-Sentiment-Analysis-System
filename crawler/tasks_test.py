# 驗證可以印出50檔個股資料，後續要接回myaql

import os
import time
import pandas as pd
import requests

from celery import Celery


# ========================================
# Celery Broker
# ========================================

CELERY_BROKER = os.getenv(
    "CELERY_BROKER",
    "amqp://worker:worker@127.0.0.1:5672//"
)


app = Celery(
    "news_tasks",
    broker=CELERY_BROKER,
    imports=["crawler.tasks"]
)


# ========================================
# Celery Worker 設定
# ========================================

app.conf.update(

    # 同一個 Worker 最多同時處理 5 個 Task
    worker_concurrency=5,

    # 每分鐘最多 120 次 API Request
    task_annotations={
        "tasks.get_news": {
            "rate_limit": "120/m"
        }
    },

    # 每個 Worker 一次只預取 1 個 Task
    worker_prefetch_multiplier=1
)


# ========================================
# FinMind API
# ========================================

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"


# ========================================
# Celery Task
#
# 重要：
# 1 Task = 1 股票 = 1 API Request
# ========================================

@app.task(
    name="tasks.get_news"
)
def get_news(stock_id, date):

    print()
    print("=" * 70)
    print(f"🚀 Task 開始")
    print(f"📌 股票代碼：{stock_id}")
    print(f"📅 日期：{date}")
    print("=" * 70)

    # ========================================
    # FinMind API Parameters
    # ========================================

    parameter = {
        "dataset": "TaiwanStockNews",
        "data_id": stock_id,
        "start_date": date,
        "end_date": date,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36"
        )
    }

    max_retry = 1

    # ========================================
    # API Request
    # ========================================

    for attempt in range(1, max_retry + 1):

        try:

            response = requests.get(
                FINMIND_URL,
                params=parameter,
                headers=headers,
                timeout=10
            )

            # ========================================
            # API 成功
            # ========================================

            if response.status_code == 200:

                data = response.json()

                df = pd.DataFrame(
                    data.get("data", [])
                )

                # ========================================
                # 沒有新聞
                # ========================================

                if df.empty:

                    print(
                        f"⚠️ Task 完成："
                        f"{stock_id} {date} 沒有新聞"
                    )

                    return {
                        "stock_id": stock_id,
                        "date": date,
                        "count": 0,
                        "status": "no_news"
                    }

                # ========================================
                # 加入股票代碼
                # ========================================

                df["stock_id"] = stock_id

                # ========================================
                # 只取第一筆新聞
                # ========================================

                first_news = df.iloc[0]

                print()
                print("✅ ====================================")
                print("✅ 分散式 Task 成功取得新聞")
                print("✅ ====================================")
                print(f"股票代碼 : {stock_id}")
                print(f"日期     : {first_news.get('date')}")
                print(f"來源     : {first_news.get('source')}")
                print(f"標題     : {first_news.get('title')}")
                print(f"連結     : {first_news.get('link')}")
                print("========================================")
                print(
                    f"📊 {stock_id} {date} "
                    f"共取得 {len(df)} 筆新聞"
                )
                print()

                # ========================================
                # 注意：
                # 這個階段故意「不寫 MySQL」
                #
                # 目的：
                # 先驗證 Celery / RabbitMQ
                # 分散式 Task 是否正常
                # ========================================

                return {
                    "stock_id": stock_id,
                    "date": date,
                    "count": len(df),
                    "status": "success",
                    "first_title": first_news.get("title")
                }

            # ========================================
            # API 限流
            # ========================================

            elif response.status_code == 429:

                print(
                    f"⚠️ 429 Too Many Requests "
                    f"{stock_id} {date} "
                    f"第 {attempt} 次"
                )

                time.sleep(8)

            # ========================================
            # 其它 HTTP 錯誤
            # ========================================

            else:

                print(
                    f"⚠️ HTTP {response.status_code} "
                    f"{stock_id} {date} "
                    f"第 {attempt} 次"
                )

                time.sleep(3)

        # ========================================
        # 網路錯誤
        # ========================================

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):

            print(
                f"❌ 網路錯誤 "
                f"{stock_id} {date} "
                f"第 {attempt} 次"
            )

            time.sleep(2)

        # ========================================
        # 其它錯誤
        # ========================================

        except Exception as e:

            print(
                f"❌ Task 發生錯誤 "
                f"{stock_id} {date}"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            return {
                "stock_id": stock_id,
                "date": date,
                "count": 0,
                "status": "error",
                "error": str(e)
            }

    # ========================================
    # Retry 失敗
    # ========================================

    print(
        f"❌ Task 失敗："
        f"{stock_id} {date}"
    )

    return {
        "stock_id": stock_id,
        "date": date,
        "count": 0,
        "status": "failed"
    }