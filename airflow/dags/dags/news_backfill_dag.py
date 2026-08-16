# 測試可以從0050拿取清單, 執行2026-2-23 爬蟲

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="news_backfill_0050_test",
    schedule=None,
    start_date=datetime(2026, 2, 23),
    catchup=False,
    tags=["crawler", "0050", "backfill"],
)
def news_backfill_0050_test():

    @task
    def send_news_tasks():

        from celery import Celery

        from crawler.get_0050_stocks import get_0050_stocks

        celery_app = Celery(
            "airflow_producer",
            broker="pyamqp://worker:worker@rabbitmq:5672/"
        )

        date = "2026-02-23"

        df = get_0050_stocks(
            csv_path="/opt/airflow/source/0050.csv"
        )

        stock_list = (
            df["商品代碼"]
            .astype(str)
            .str.strip()
            .tolist()
        )

        print("=" * 60)
        print(f"日期：{date}")
        print(f"股票數量：{len(stock_list)}")
        print("=" * 60)

        task_ids = []

        for stock_id in stock_list:

            result = celery_app.send_task(
                "tasks.get_news",
                args=[
                    stock_id,
                    date
                ]
            )

            task_ids.append(result.id)

            print(
                f"📨 已派送："
                f"{stock_id} / {date} / "
                f"task_id={result.id}"
            )

        print("=" * 60)
        print(f"✅ 共派送 {len(task_ids)} 個 Celery Tasks")
        print("=" * 60)

        return {
            "date": date,
            "task_count": len(task_ids)
        }

    send_news_tasks()


news_backfill_0050_test()