# uv run crawler/producer.py 另一個視窗執行

# Producer (生產者): 負責把任務送進 RabbitMQ 佇列
# 對應的 Consumer (消費者) 就是 worker.py 啟動的 Celery worker
# 流程: producer.py → RabbitMQ (訊息佇列) → worker 取出並執行任務

# 注意這裡不是直接呼叫函式, 而是把它當作「任務」送出去
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 1. 取得專案根目錄 (Stock-Market-Sentiment-Analysis-System)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 解決 ModuleNotFoundError：讓 Python 找得到平行的 crawler 資料夾
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 3. 解決 FileNotFoundError：用絕對路徑精準定位平行的 source 資料夾
CSV_PATH = BASE_DIR / "source" / "0050_list.csv"

# ----------------- 確保路徑設定完後，再執行匯入 -----------------
from crawler.get_0050_stocks import get_0050_stocks
from crawler.tasks_news import get_news
# from crawler.tasks_news import test_mysql #測試連線用

# ========================================
# 取得 0050 成分股
# ========================================
# 這裡傳入剛剛設定好的絕對路徑字串
df_clean = get_0050_stocks(csv_path=str(CSV_PATH))

stock_list = (
    df_clean["商品代碼"]
    .str.strip()
    .tolist()
)    

# ========================================
# 建立日期
# ========================================

def generate_date_range(
    start_date,
    end_date
):

    dates = []

    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )

    while start <= end:

        dates.append(
            start.strftime("%Y-%m-%d")
        )

        start = start + timedelta(
            days=1
        )

    return dates


# ========================================
# 日期範圍
# ========================================

dates = generate_date_range(
    "2026-02-26",
    "2026-02-26"
)


# ========================================
# 建立 Celery 任務
# ========================================

task_count = 0
for stock_id in stock_list:

    for date in dates:

        get_news.delay(
            stock_id,
            date
        )

        task_count = task_count + 1

        print(
            f"📨 已發送 Task："
            f"{stock_id} / {date}"
        )

print(f"📨 總共發送：{task_count} 個 Task")

# 驗證單一組股價資料
# stock_id = "8046"  
# date = "2026-02-26"

# get_news.delay(
#     stock_id,
#     date
# )

# task_count = task_count + 1

# print(
#     f"📨 已發送 Task："
#     f"{stock_id} / {date}"
# )

# 測試連線用
# test_mysql.delay()

# task_count = task_count + 1

# print("📨 已發送 MySQL 測試 Task")

print("=" * 60)

print(
    "🚀 Producer 完成"
)

print(
    f"📨 總共發送："
    f"{task_count} 個 Task"
)

print("=" * 60)