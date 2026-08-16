# uv run python -m crawler.check_missing_news
# 找出SQL缺少的股票代碼

from pathlib import Path

from crawler.get_0050_stocks import get_0050_stocks
from crawler.mysql_connection import get_connection


# ========================================
# 專案路徑
# ========================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "source" / "0050.csv"


# ========================================
# 取得 0050 成分股
# ========================================

df = get_0050_stocks(
    csv_path=str(CSV_PATH)
)

expected_stocks = set(
    df["商品代碼"]
    .astype(str)
    .str.strip()
    .tolist()
)


# ========================================
# 要檢查的日期
# ========================================

dates = [
    "2026-03-06",
    "2026-03-06",
]


# ========================================
# MySQL
# ========================================

conn = get_connection()
cursor = conn.cursor()


try:

    for date in dates:

        cursor.execute(
            """
            SELECT DISTINCT stock_id
            FROM news_raw
            WHERE DATE(date) = %s
            """,
            (date,)
        )

        db_stocks = {
            str(row[0]).strip()
            for row in cursor.fetchall()
        }

        missing_stocks = expected_stocks - db_stocks

        print()
        print("=" * 60)
        print(f"📅 日期：{date}")
        print(f"📊 0050 股票數：{len(expected_stocks)}")
        print(f"📦 DB 有新聞股票數：{len(db_stocks)}")
        print(f"❓ DB 沒出現股票數：{len(missing_stocks)}")

        print("股票清單：")

        for stock_id in sorted(missing_stocks):
            print(f"   {stock_id}")

finally:

    cursor.close()
    conn.close()