# 測試 2330爬2026-02-23 資料是否可存入SQL
from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="news_crawler_test",
    schedule=None,
    start_date=datetime(2026, 8, 1),
    catchup=False,
    tags=["crawler", "celery"],
)
def news_crawler_test():

    @task
    def send_news_task():

        from celery import Celery

        celery_app = Celery(
            "airflow_producer",
            broker="pyamqp://worker:worker@rabbitmq:5672/"
        )

        stock_id = "2330"
        date = "2026-02-23"

        result = celery_app.send_task(
            "tasks.get_news",
            args=[
                stock_id,
                date
            ]
        )

        print("=" * 60)
        print("📨 Celery Task 已送出")
        print(f"股票代碼：{stock_id}")
        print(f"日期：{date}")
        print(f"Celery Task ID：{result.id}")
        print("=" * 60)

        return result.id

    send_news_task()


news_crawler_test()