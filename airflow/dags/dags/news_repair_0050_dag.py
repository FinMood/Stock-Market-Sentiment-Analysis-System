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
        from datetime import datetime, timedelta

        from crawler.get_0050_stocks import get_0050_stocks
        from crawler.news_repository import get_completed_stock_ids

        celery_app = Celery(
            "airflow_repair",
            broker="pyamqp://worker:worker@rabbitmq:5672/"
        )

        # ========================================
        # Repair 日期區間
        # ========================================

        start_date = "2026-04-29"
        end_date = "2026-05-24"

        current_date = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        )

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        )

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
        # 統計
        # ========================================

        total_missing = 0
        total_sent = 0
        checked_days = 0

        # ========================================
        # 每一天檢查
        # ========================================

        while current_date <= end:

            crawl_date = current_date.strftime(
                "%Y-%m-%d"
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

            checked_days += 1
            total_missing += len(missing_stock_ids)

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

                total_sent += 1

                print(
                    f"🔧 補派 | "
                    f"{stock_id} | "
                    f"{crawl_date} | "
                    f"{result.id}"
                )

            # ========================================
            # ★ 關鍵：前進下一天
            # ========================================

            current_date += timedelta(days=1)

        # ========================================
        # 全部日期完成後才 return
        # ========================================

        print()
        print("=" * 70)
        print("🎯 Repair 檢查完成")
        print(f"📅 區間：{start_date} ~ {end_date}")
        print(f"📆 檢查天數：{checked_days}")
        print(f"❌ 發現缺漏：{total_missing}")
        print(f"📨 實際補派：{total_sent}")
        print("=" * 70)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "checked_days": checked_days,
            "missing": total_missing,
            "sent": total_sent
        }

    repair_missing()


news_repair_0050()