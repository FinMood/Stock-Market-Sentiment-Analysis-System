# 正式程式碼, 按一次可爬出1957, 會被402

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="news_backfill_0050",
    schedule="@daily",
    start_date=datetime(2026, 2, 22),
    end_date=datetime(2026, 3, 18),
    catchup=True,
    max_active_runs=1,
    tags=["crawler", "0050", "backfill"],
)
def news_backfill_0050():

    @task
    def send_news_tasks(ds=None):

        from celery import Celery
        from crawler.get_0050_stocks import get_0050_stocks

        celery_app = Celery(
            "airflow_producer",
            broker="pyamqp://worker:worker@rabbitmq:5672/"
        )

        # Airflow 每個 DAG Run 對應的日期
        date = ds

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
        print(f"📅 Backfill 日期：{date}")
        print(f"📈 股票數量：{len(stock_list)}")
        print("=" * 60)

        task_count = 0

        for stock_id in stock_list:

            result = celery_app.send_task(
                "tasks.get_news",
                args=[
                    stock_id,
                    date
                ]
            )

            task_count += 1

            print(
                f"📨 {task_count:02d} | "
                f"{stock_id} | "
                f"{date} | "
                f"{result.id}"
            )

        print("=" * 60)
        print(
            f"✅ {date} 派送完成 | "
            f"Celery Tasks = {task_count}"
        )
        print("=" * 60)

        return {
            "date": date,
            "task_count": task_count
        }

    send_news_tasks()


news_backfill_0050()