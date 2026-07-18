"""
fetch_stock_price.py
從 FinMind API 抓取個股每日股價，寫入 SQLite stock_data 表。

用法：
    uv run python fetch_stock_price.py              # 預設抓 2330
    uv run python fetch_stock_price.py --stock 2454  # 指定個股
"""

import argparse
import os
import sqlite3
import pandas as pd
import requests


FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"


def fetch_price(stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """從 FinMind API 拉取 TaiwanStockPrice"""
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(FINMIND_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        print(f"⚠️ FinMind 回傳空資料 ({stock_id} {start_date}~{end_date})")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    return df


def save_to_sqlite(df: pd.DataFrame, db_path: str = "taiwan50_sentiment.db"):
    """寫入 SQLite stock_data 表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        stock_id TEXT,
        open REAL,
        close REAL,
        volume INTEGER
    )
    """)
    conn.commit()

    # 追加寫入（不覆蓋，方便後續加入更多個股）
    df.to_sql("stock_data", conn, if_exists="append", index=False)

    cursor.execute("SELECT COUNT(*) FROM stock_data")
    total = cursor.fetchone()[0]
    print(f"🎉 stock_data 表目前共 {total} 筆")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="從 FinMind 抓取個股股價")
    parser.add_argument("--stock", default="2330", help="股票代碼 (預設: 2330)")
    parser.add_argument("--start", default="2026-02-23", help="起始日期")
    parser.add_argument("--end", default="2026-03-11", help="結束日期")
    parser.add_argument("--db", default="taiwan50_sentiment.db", help="SQLite DB 路徑")
    args = parser.parse_args()

    print(f"📡 正在下載 {args.stock} 股價 ({args.start} ~ {args.end})...")
    raw_df = fetch_price(args.stock, args.start, args.end)

    if raw_df.empty:
        print("❌ 沒有取得任何股價資料")
        return

    # 只保留需要的欄位，確保 stock_id 是字串
    df = raw_df[["date", "stock_id", "open", "close", "Trading_Volume"]].copy()
    df = df.rename(columns={"Trading_Volume": "volume"})
    df["stock_id"] = df["stock_id"].astype(str)

    print(f"✅ 取得 {len(df)} 筆股價資料")
    print(df.head())

    # 同時存一份 CSV 備份
    os.makedirs("source", exist_ok=True)
    csv_path = f"source/{args.stock}_price.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"💾 CSV 備份 → {csv_path}")

    # 寫入 SQLite
    save_to_sqlite(df, args.db)


if __name__ == "__main__":
    main()
