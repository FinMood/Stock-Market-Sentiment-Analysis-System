# 補足缺少的資料
# uv run python -m crawler.producer_backfill

from crawler.tasks_news import get_news


# ========================================
# 缺少的 股票 × 日期
# ========================================

missing_tasks = {
"2026-03-6": [
        "1216",
        "1303",
        "2059",
        "2301",
        "2303",
        "2308",
        "2317",
        "2327",
        "2330",
        "2344",
        "2345",
        "2357",
        "2360",
        "2382",
        "2383",
        "2408",
        "2412",
        "2454",
        "2880",
        "2881",
        "2882",
        "2883",
        "2884",
        "2885",
        "2886",
        "2887",
        "2890",
        "2891",
        "2892",
        "3008",
        "3017",
        "3037",
        "3045",
        "3231",
        "3711",
        "4958",
        "5880",
        "6505",
        "6669"
    ]

}


# ========================================
# 發送 Backfill Task
# ========================================

task_count = 0

for date, stock_list in missing_tasks.items():

    for stock_id in stock_list:

        get_news.delay(
            stock_id,
            date
        )

        task_count += 1

        print(
            f"📨 Backfill Task："
            f"{stock_id} / {date}"
        )


print()
print("=" * 60)
print("🚀 Backfill Producer 完成")
print(f"📨 總共發送：{task_count} 個 Task")
print("=" * 60)