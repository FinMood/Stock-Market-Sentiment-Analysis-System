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


# ============================================================
# Celery Broker
# ============================================================

CELERY_BROKER = os.getenv(
    "CELERY_BROKER",
    "amqp://worker:worker@127.0.0.1:5672//"
)


app = Celery(
    "news_tasks",
    broker=CELERY_BROKER,
)


# ============================================================
# Celery Worker 設定
# ============================================================

app.conf.update(

    # 同一個 Worker 最多同時處理 5 個 Task
    worker_concurrency=5,

    # 每個 Worker 一次只預取 1 個 Task
    worker_prefetch_multiplier=1,
)


# ============================================================
# FinMind API
# ============================================================

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"


# ============================================================
# Celery Task
#
# 1 Task = 1 股票 + 1 日期
#
# rate_limit = 5/m
# 每分鐘最多呼叫 5 次
# ============================================================

@app.task(
    name="tasks.get_news",
    rate_limit="120/m"
)
def get_news(stock_id, date):

    print()
    print("=" * 70)
    print("🚀 Task 開始")
    print(f"📌 股票代碼：{stock_id}")
    print(f"📅 日期：{date}")
    print("=" * 70)

    # ========================================================
    # 1. Crawl Progress 檢查
    #
    # success / no_news 已經完成
    # → 不再重新呼叫 FinMind
    # ========================================================

    try:

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

    except Exception as e:

        print()
        print("❌ crawl_progress 查詢失敗")
        print(f"股票：{stock_id}")
        print(f"日期：{date}")
        print(f"{type(e).__name__}: {e}")

        raise


    # ========================================================
    # 2. FinMind API Parameters
    # ========================================================

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


    # ========================================================
    # 3. Retry 設定
    # ========================================================

    max_retry = 3


    # ========================================================
    # 4. API Request
    # ========================================================

    for attempt in range(
        1,
        max_retry + 1
    ):

        print()
        print(
            f"🌐 FinMind API Request | "
            f"{stock_id} | "
            f"{date} | "
            f"attempt={attempt}/{max_retry}"
        )

        try:

            response = requests.get(
                FINMIND_URL,
                params=parameter,
                headers=headers,
                timeout=10
            )


            # ====================================================
            # HTTP 200
            # ====================================================

            if response.status_code == 200:

                data = response.json()

                df = pd.DataFrame(
                    data.get(
                        "data",
                        []
                    )
                )


                # =================================================
                # 沒有新聞
                # =================================================

                if df.empty:

                    print()
                    print("ℹ️ ====================================")
                    print("ℹ️ 當日沒有新聞")
                    print("ℹ️ ====================================")
                    print(f"股票：{stock_id}")
                    print(f"日期：{date}")
                    print("========================================")

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


                # =================================================
                # 加入 stock_id
                # =================================================

                df["stock_id"] = stock_id


                # =================================================
                # 第一筆新聞
                # =================================================

                first_news = df.iloc[0]

                print()
                print("✅ ====================================")
                print("✅ FinMind API 成功")
                print("✅ ====================================")
                print(f"股票代碼：{stock_id}")
                print(f"日期：{date}")
                print(f"API 筆數：{len(df)}")
                print(
                    f"第一筆日期："
                    f"{first_news.get('date')}"
                )
                print(
                    f"來源："
                    f"{first_news.get('source')}"
                )
                print(
                    f"標題："
                    f"{first_news.get('title')}"
                )
                print(
                    f"連結："
                    f"{first_news.get('link')}"
                )
                print("========================================")


                # =================================================
                # 寫入 MySQL
                # =================================================

                try:

                    # ---------------------------------------------
                    # 先存新聞
                    # ---------------------------------------------

                    inserted_count = save_news_to_mysql(
                        df
                    )

                    print()
                    print(
                        f"💾 news_raw 完成 | "
                        f"{stock_id} | "
                        f"{date} | "
                        f"API={len(df)} | "
                        f"新增={inserted_count}"
                    )


                    # ---------------------------------------------
                    # 新聞存成功後
                    # 才更新 crawl_progress
                    # ---------------------------------------------

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

                    print()
                    print("❌ ====================================")
                    print("❌ MySQL 寫入失敗")
                    print("❌ ====================================")
                    print(f"股票：{stock_id}")
                    print(f"日期：{date}")
                    print(
                        f"{type(e).__name__}: "
                        f"{e}"
                    )
                    print("========================================")

                    # DB 寫入失敗是系統異常
                    # Celery Task 應該真的失敗
                    raise


                # =================================================
                # Task 完成
                # =================================================

                print()
                print("🎯 ====================================")
                print("🎯 Task 完成")
                print("🎯 ====================================")
                print(f"股票：{stock_id}")
                print(f"日期：{date}")
                print(f"新聞數：{len(df)}")
                print("========================================")


                return {
                    "stock_id": stock_id,
                    "date": date,
                    "count": len(df),
                    "status": "success",
                    "first_title": first_news.get(
                        "title"
                    )
                }


            # ====================================================
            # HTTP 402
            #
            # FinMind quota exceeded
            # 不 retry
            # 留給 repair DAG
            # ====================================================

            elif response.status_code == 402:

                print()
                print("🛑 ====================================")
                print("🛑 FinMind API quota 已達上限")
                print("🛑 ====================================")
                print(f"股票：{stock_id}")
                print(f"日期：{date}")
                print(
                    f"HTTP："
                    f"{response.status_code}"
                )
                print(
                    f"回應："
                    f"{response.text}"
                )
                print(
                    "➡️ 不再 retry，"
                    "留給 repair DAG 補抓"
                )
                print("========================================")


                # ---------------------------------------------
                # 寫入 crawl_progress
                # ---------------------------------------------

                save_crawl_progress(
                    stock_id=stock_id,
                    crawl_date=date,
                    status="quota_exceeded",
                    news_count=0
                )


                return {
                    "stock_id": stock_id,
                    "date": date,
                    "count": 0,
                    "status": "quota_exceeded"
                }


            # ====================================================
            # HTTP 429
            #
            # Too Many Requests
            # ====================================================

            elif response.status_code == 429:

                print()
                print("⚠️ ====================================")
                print("⚠️ HTTP 429 Too Many Requests")
                print("⚠️ ====================================")
                print(f"股票：{stock_id}")
                print(f"日期：{date}")
                print(
                    f"attempt："
                    f"{attempt}/{max_retry}"
                )
                print(
                    f"response："
                    f"{response.text}"
                )
                print("========================================")


                # ---------------------------------------------
                # 還能 retry
                # ---------------------------------------------

                if attempt < max_retry:

                    wait_seconds = (
                        60 * attempt
                    )

                    print(
                        f"⏳ 等待 "
                        f"{wait_seconds} 秒後重試"
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue


                # ---------------------------------------------
                # 最後一次仍失敗
                # ---------------------------------------------

                save_crawl_progress(
                    stock_id=stock_id,
                    crawl_date=date,
                    status="failed",
                    news_count=0
                )


                print(
                    f"❌ 429 重試失敗 | "
                    f"{stock_id} | "
                    f"{date}"
                )


                return {
                    "stock_id": stock_id,
                    "date": date,
                    "count": 0,
                    "status": "failed"
                }


            # ====================================================
            # 其它 HTTP Error
            # ====================================================

            else:

                print()
                print("⚠️ ====================================")
                print("⚠️ FinMind HTTP Error")
                print("⚠️ ====================================")
                print(f"股票：{stock_id}")
                print(f"日期：{date}")
                print(
                    f"HTTP："
                    f"{response.status_code}"
                )
                print(
                    f"attempt："
                    f"{attempt}/{max_retry}"
                )
                print(
                    f"response："
                    f"{response.text}"
                )
                print("========================================")


                # ---------------------------------------------
                # 還可以 retry
                # ---------------------------------------------

                if attempt < max_retry:

                    wait_seconds = (
                        10 * attempt
                    )

                    print(
                        f"⏳ 等待 "
                        f"{wait_seconds} 秒後重試"
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue


                # ---------------------------------------------
                # HTTP Error 最終失敗
                # ---------------------------------------------

                save_crawl_progress(
                    stock_id=stock_id,
                    crawl_date=date,
                    status="failed",
                    news_count=0
                )


                return {
                    "stock_id": stock_id,
                    "date": date,
                    "count": 0,
                    "status": "failed"
                }


        # ========================================================
        # Network Error
        # ========================================================

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as e:

            print()
            print("🌐 ====================================")
            print("🌐 網路連線錯誤")
            print("🌐 ====================================")
            print(f"股票：{stock_id}")
            print(f"日期：{date}")
            print(
                f"attempt："
                f"{attempt}/{max_retry}"
            )
            print(
                f"{type(e).__name__}: "
                f"{e}"
            )
            print("========================================")


            # ---------------------------------------------
            # 還可以 retry
            # ---------------------------------------------

            if attempt < max_retry:

                wait_seconds = (
                    5 * attempt
                )

                print(
                    f"⏳ 等待 "
                    f"{wait_seconds} 秒後重試"
                )

                time.sleep(
                    wait_seconds
                )

                continue


            # ---------------------------------------------
            # 網路錯誤最終失敗
            # ---------------------------------------------

            save_crawl_progress(
                stock_id=stock_id,
                crawl_date=date,
                status="failed",
                news_count=0
            )


            return {
                "stock_id": stock_id,
                "date": date,
                "count": 0,
                "status": "failed"
            }


        # ========================================================
        # Request 其它異常
        # ========================================================

        except requests.exceptions.RequestException as e:

            print()
            print("❌ ====================================")
            print("❌ Requests 發生錯誤")
            print("❌ ====================================")
            print(f"股票：{stock_id}")
            print(f"日期：{date}")
            print(
                f"{type(e).__name__}: "
                f"{e}"
            )
            print("========================================")


            if attempt < max_retry:

                wait_seconds = (
                    5 * attempt
                )

                time.sleep(
                    wait_seconds
                )

                continue


            save_crawl_progress(
                stock_id=stock_id,
                crawl_date=date,
                status="failed",
                news_count=0
            )


            return {
                "stock_id": stock_id,
                "date": date,
                "count": 0,
                "status": "failed"
            }


        # ========================================================
        # 非預期 Python Error
        # ========================================================

        except Exception as e:

            print()
            print("❌ ====================================")
            print("❌ Task 發生非預期錯誤")
            print("❌ ====================================")
            print(f"股票：{stock_id}")
            print(f"日期：{date}")
            print(
                f"{type(e).__name__}: "
                f"{e}"
            )
            print("========================================")

            # 非預期錯誤要真的讓 Celery 標紅
            raise


    # ============================================================
    # 理論上正常不會走到這裡
    # 保留作為程式流程防護
    # ============================================================

    error_message = (
        f"Task 流程異常結束："
        f"{stock_id} "
        f"{date}"
    )

    print(
        f"❌ {error_message}"
    )

    raise RuntimeError(
        error_message
    )