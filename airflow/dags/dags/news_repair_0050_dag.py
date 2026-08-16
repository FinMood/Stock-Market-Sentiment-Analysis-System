from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="news_repair_0050",
    schedule=None,
    start_date=datetime(2026, 2, 23),
    catchup=False,
    tags=["crawler", "0050", "repair"],
)
def news_repair_0050():

    @task
    def repair_missing():

        from celery import Celery

        from crawler.get_0050_stocks import get_0050_stocks
        from crawler.news_repository import get_completed_stock_ids

        celery_app = Celery(
            "airflow_repair",
            broker="pyamqp://worker:worker@rabbitmq:5672/"
        )

        # ========================================
        # 先固定測試日期
        # ========================================

        crawl_date = "2026-03-07"

        # ========================================
        # 0050 股票清單
        # ========================================

        df = get_0050_stocks(
            csv_path="/opt/airflow/source/0050.csv"
        )

        all_stock_ids = set(
            df["商品代碼"]
            .astype(str)
            .str.strip()
            .tolist()
        )

        # ========================================
        # 已完成清單
        # ========================================

        completed_stock_ids = get_completed_stock_ids(
            crawl_date
        )

        # ========================================
        # 缺漏清單
        # ========================================

        missing_stock_ids = (
            all_stock_ids
            - completed_stock_ids
        )

        print("=" * 70)
        print(f"📅 日期：{crawl_date}")
        print(f"📈 應有：{len(all_stock_ids)}")
        print(f"✅ 完成：{len(completed_stock_ids)}")
        print(f"❌ 缺少：{len(missing_stock_ids)}")
        print("=" * 70)

        # ========================================
        # 只補缺少的
        # ========================================

        for stock_id in sorted(missing_stock_ids):

            result = celery_app.send_task(
                "tasks.get_news",
                args=[
                    stock_id,
                    crawl_date
                ]
            )

            print(
                f"🔧 補派 | "
                f"{stock_id} | "
                f"{crawl_date} | "
                f"{result.id}"
            )

        return {
            "date": crawl_date,
            "total": len(all_stock_ids),
            "completed": len(completed_stock_ids),
            "missing": len(missing_stock_ids)
        }

    repair_missing()


news_repair_0050()