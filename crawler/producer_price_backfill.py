# 回填過去股價
# uv run python crawler/producer_price_backfill.py 可一次執行所有股價

import os
import sys
from pathlib import Path
from datetime import datetime

from celery import Celery


# ========================================
# 專案根目錄
# ========================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ========================================
# 0050 CSV 路徑
# ========================================

CSV_PATH = BASE_DIR / "source" / "0050.csv"


# ========================================
# Import
# ========================================

from crawler.get_0050_stocks import get_0050_stocks


# ========================================
# RabbitMQ Broker
# ========================================

CELERY_BROKER = os.getenv(
    "CELERY_BROKER",
    "amqp://worker:worker@127.0.0.1:5672//",
)


celery_app = Celery(
    "price_backfill_producer",
    broker=CELERY_BROKER,
)


# ========================================
# Backfill 日期
# ========================================

START_DATE = "2026-02-23"
END_DATE = "2026-08-17"


# ========================================
# 發送 Backfill Tasks
# ========================================

def send_price_backfill_tasks(
    start_date: str,
    end_date: str,
):

    # ----------------------------------------
    # 日期格式驗證
    # ----------------------------------------

    datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )


    if start_date > end_date:
        raise ValueError(
            f"start_date 不可晚於 end_date："
            f"{start_date} > {end_date}"
        )


    # ----------------------------------------
    # 取得 0050 股票清單
    # ----------------------------------------

    df_clean = get_0050_stocks(
        csv_path=str(CSV_PATH)
    )

    stock_list = (
        df_clean["商品代碼"]
        .astype(str)
        .str.strip()
        .tolist()
    )


    print()
    print("=" * 70)
    print("📚 Yahoo Finance 0050 歷史股價 Backfill")
    print("=" * 70)

    print(
        f"📅 日期："
        f"{start_date} ~ {end_date}"
    )

    print(
        f"📊 股票數："
        f"{len(stock_list)}"
    )

    print("=" * 70)


    # ----------------------------------------
    # 發送 Celery Tasks
    #
    # 1 Task
    # =
    # 1 股票 × 整段日期
    # ----------------------------------------

    task_count = 0


    for stock_id in stock_list:

        result = celery_app.send_task(

            "tasks.backfill_stock_price",

            args=[
                stock_id,
                start_date,
                end_date,
            ],
        )


        task_count += 1


        print(
            f"📨 "
            f"[{task_count:02d}/{len(stock_list)}] "
            f"{stock_id} | "
            f"{start_date} ~ {end_date} | "
            f"Task ID={result.id}"
        )


    # ----------------------------------------
    # 完成
    # ----------------------------------------

    print()
    print("=" * 70)

    print(
        f"🚀 Backfill Producer 完成"
    )

    print(
        f"📨 共發送 "
        f"{task_count} 個 Task"
    )

    print("=" * 70)


# ========================================
# Main
# ========================================

if __name__ == "__main__":

    send_price_backfill_tasks(
        START_DATE,
        END_DATE,
    )