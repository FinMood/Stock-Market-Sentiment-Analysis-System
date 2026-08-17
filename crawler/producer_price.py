# 未來更新用，單日派送

import os
import sys
from pathlib import Path
from datetime import datetime

from celery import Celery

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CSV_PATH = BASE_DIR / "source" / "0050_list.csv"

from crawler.get_0050_stocks import get_0050_stocks

CELERY_BROKER = os.getenv(
    "CELERY_BROKER",
    "amqp://worker:worker@127.0.0.1:5672//",
)

celery_app = Celery("price_producer", broker=CELERY_BROKER)


def send_price_tasks(date: str):
    datetime.strptime(date, "%Y-%m-%d")

    df_clean = get_0050_stocks(csv_path=str(CSV_PATH))
    stock_list = df_clean["商品代碼"].astype(str).str.strip().tolist()

    task_count = 0

    for stock_id in stock_list:
        celery_app.send_task(
            "tasks.get_stock_price",
            args=[stock_id, date],
        )
        task_count += 1
        print(f"📨 已發送股價 Task：{stock_id} / {date}")

    print("=" * 60)
    print(f"🚀 Producer 完成，共發送 {task_count} 個股價 Task")
    print("=" * 60)


if __name__ == "__main__":
    # 第一階段先固定單日測試，確認 Yahoo → Celery → MySQL 全鏈路正常。
    send_price_tasks("2026-08-14")