import os
import time
import pandas as pd
import requests

from celery import Celery

from crawler.news_repository import (
    save_news_to_mysql,
    save_crawl_progress,
    is_crawl_completed,
)


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
# 1 Task = 1 股票
# 1 Task = 1 API Request
# ========================================

@app.task(
    name="tasks.get_news"
)
def get_news(stock_id, date):

    print()
    print("=" * 70)
    print("🚀 Task 開始")
    print(f"📌 股票代碼：{stock_id}")
    print(f"📅 日期：{date}")
    print("=" * 70)


        # ========================================
    # Crawl Progress 檢查
    #
    # success / no_news 已存在
    # → 代表這個股票 + 日期已經查過
    # → 不再呼叫 FinMind API
    # ========================================

    if is_crawl_completed(
        stock_id,
        date
    ):

        print()
        print("⏭️ ====================================")
        print("⏭️ Crawl Progress 已完成")
        print("⏭️ 跳過 FinMind API")
        print("⏭️ ====================================")
        print(f"股票代碼：{stock_id}")
        print(f"日期：{date}")
        print("========================================")

        return {
            "stock_id": stock_id,
            "date": date,
            "count": 0,
            "status": "skipped"
        }

    # ========================================
    # 2. FinMind API Parameters
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

                    save_crawl_progress(
                        stock_id=stock_id,
                        crawl_date=date,
                        status="no_news",
                        news_count=0
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
                # 印出第一筆新聞
                # ========================================

                first_news = df.iloc[0]

                print()
                print("✅ ====================================")
                print("✅ FinMind API 成功")
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

                # ========================================
                # 寫入 MySQL
                # ========================================

                try:

                    # ========================================
                    # 先寫新聞
                    # ========================================

                    inserted_count = save_news_to_mysql(
                        df
                    )

                    print(
                        f"💾 news_raw 完成 | "
                        f"{stock_id} {date} | "
                        f"API={len(df)} | "
                        f"新增={inserted_count}"
                    )

                    # ========================================
                    # 新聞寫入成功後
                    # 才標記 Crawl Progress
                    # ========================================

                    save_crawl_progress(
                        stock_id=stock_id,
                        crawl_date=date,
                        status="success",
                        news_count=len(df)
                    )

                    print(
                        f"📍 crawl_progress 完成 | "
                        f"{stock_id} | "
                        f"{date} | "
                        f"success | "
                        f"news_count={len(df)}"
                    )

                except Exception as e:

                    print(
                        f"❌ MySQL 寫入失敗："
                        f"{stock_id} {date}"
                    )

                    print(
                        f"{type(e).__name__}: {e}"
                    )

                    raise
                except Exception as e:

                    print(
                        f"❌ MySQL 寫入失敗："
                        f"{stock_id} {date}"
                    )

                    print(
                        f"{type(e).__name__}: {e}"
                    )

                    # 重要：
                    # MySQL 失敗 → Task 也視為失敗
                    raise

                # ========================================
                # Task 完成
                # ========================================

                print(
                    f"🎯 Task 完成："
                    f"{stock_id} {date}"
                )

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
                print(
                     f"📨 FinMind 回應：{response.text}"
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

            raise

    # ========================================
    # Retry 失敗
    # ========================================

    error_message = (
        f"FinMind API 下載失敗："
        f"{stock_id} {date}"
    )

    print(f"❌ {error_message}")

    raise RuntimeError(error_message)

# ========================================
# @app.task(name="tasks.test_mysql") # 測試連線用
def test_mysql():

    from crawler.mysql_connection import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    # 先看目前連到哪一台 MySQL
    cursor.execute("""
        SELECT
            @@hostname,
            @@port,
            DATABASE(),
            USER(),
            @@datadir
    """)

    info = cursor.fetchone()

    print("🔍 Worker MySQL 診斷")
    print(f"hostname = {info[0]}")
    print(f"port     = {info[1]}")
    print(f"database = {info[2]}")
    print(f"user     = {info[3]}")
    print(f"datadir  = {info[4]}")

    # 再直接寫一筆測試資料
    sql = """
    INSERT IGNORE INTO news_raw
    (date, stock_id, link, source, title)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            "2026-02-26 12:34:56",
            "TEST8046",
            "https://example.com/mysql-test-8046",
            "TEST",
            "Celery MySQL connection test"
        )
    )

    conn.commit()

    print(f"💾 測試資料新增筆數：{cursor.rowcount}")

    cursor.close()
    conn.close()