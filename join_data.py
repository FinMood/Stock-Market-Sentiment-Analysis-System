"""
join_data.py — 資料整合層
將 Table2 (stock_data) 與 Table3 (news_sentiment) 整合為 Table4 (sentiment_stock_merged)。

整合邏輯：
  1. 讀取 news_sentiment → 按 (date, stock_id) 聚合：計算日均情緒分數 & 新聞數量
  2. 讀取 stock_data → 股價資料
  3. 以 (date, stock_id) 為 Key 做 LEFT JOIN
  4. 寫入 SQLite sentiment_stock_merged 表 + CSV 備份

用法：
    uv run python join_data.py
    uv run python join_data.py --stock 2330
    uv run python join_data.py --db taiwan50_sentiment.db
"""

import argparse
import os
import sqlite3
import pandas as pd


DB_PATH = "taiwan50_sentiment.db"


def load_news_sentiment(conn: sqlite3.Connection, stock_id: str | None = None) -> pd.DataFrame:
    """
    從 SQLite 讀取 news_sentiment (Table3)，
    按 (date, stock_id) 聚合為每日摘要。
    """
    query = "SELECT date, stock_id, sentiment FROM news_sentiment"
    if stock_id:
        query += f" WHERE stock_id = '{stock_id}'"

    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("⚠️ news_sentiment 無資料")
        return pd.DataFrame()

    # 聚合：每日每檔股票的平均情緒 + 新聞數
    agg_df = (
        df.groupby(["date", "stock_id"])
        .agg(
            avg_sentiment=("sentiment", "mean"),
            news_count=("sentiment", "count"),
        )
        .reset_index()
    )
    agg_df["avg_sentiment"] = agg_df["avg_sentiment"].round(4)
    return agg_df


def load_stock_data(conn: sqlite3.Connection, stock_id: str | None = None) -> pd.DataFrame:
    """從 SQLite 讀取 stock_data (Table2)"""
    query = "SELECT date, stock_id, open, close, volume FROM stock_data"
    if stock_id:
        query += f" WHERE stock_id = '{stock_id}'"

    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("⚠️ stock_data 無資料")

    return df


def merge_tables(stock_df: pd.DataFrame, news_agg_df: pd.DataFrame) -> pd.DataFrame:
    """
    LEFT JOIN：以股價為主表，補上當日情緒資料。
    沒有新聞的交易日，avg_sentiment = 0, news_count = 0。
    """
    # 統一 stock_id 型別為字串，避免 int vs str 造成 merge 失敗
    stock_df = stock_df.copy()
    news_agg_df = news_agg_df.copy()
    stock_df["stock_id"] = stock_df["stock_id"].astype(str)
    news_agg_df["stock_id"] = news_agg_df["stock_id"].astype(str)

    merged = pd.merge(
        stock_df,
        news_agg_df,
        on=["date", "stock_id"],
        how="left",
    )
    merged["avg_sentiment"] = merged["avg_sentiment"].fillna(0.0)
    merged["news_count"] = merged["news_count"].fillna(0).astype(int)
    merged = merged.sort_values("date").reset_index(drop=True)
    return merged


def save_table4(df: pd.DataFrame, conn: sqlite3.Connection):
    """寫入 SQLite sentiment_stock_merged 表 (Table4)"""
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sentiment_stock_merged (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        stock_id TEXT,
        open REAL,
        close REAL,
        volume INTEGER,
        avg_sentiment REAL,
        news_count INTEGER
    )
    """)
    conn.commit()

    df.to_sql("sentiment_stock_merged", conn, if_exists="replace", index=False)

    cursor.execute("SELECT COUNT(*) FROM sentiment_stock_merged")
    total = cursor.fetchone()[0]
    print(f"🎉 Table4 (sentiment_stock_merged) 寫入完成，共 {total} 筆")


def main():
    parser = argparse.ArgumentParser(description="資料整合層：Table2 + Table3 → Table4")
    parser.add_argument("--stock", default=None, help="篩選特定股票代碼 (預設: 全部)")
    parser.add_argument("--db", default=DB_PATH, help="SQLite DB 路徑")
    args = parser.parse_args()

    print(f"📦 正在整合資料 (DB: {args.db})...")
    conn = sqlite3.connect(args.db)

    # Step 1: 讀取 & 聚合新聞情緒
    print("📰 載入 news_sentiment (Table3)...")
    news_agg = load_news_sentiment(conn, args.stock)
    if news_agg.empty:
        conn.close()
        return

    print(f"   → 聚合後 {len(news_agg)} 筆 (日×股票)")

    # Step 2: 讀取股價
    print("📊 載入 stock_data (Table2)...")
    stock_df = load_stock_data(conn, args.stock)
    if stock_df.empty:
        conn.close()
        return

    print(f"   → {len(stock_df)} 筆股價")

    # Step 3: JOIN
    print("🔗 合併中...")
    merged = merge_tables(stock_df, news_agg)
    print(f"   → 合併後 {len(merged)} 筆")
    print()
    print(merged.head(10).to_string())

    # Step 4: 寫入
    save_table4(merged, conn)

    # Step 5: CSV 備份
    os.makedirs("data", exist_ok=True)
    csv_path = "data/sentiment_stock_merged.csv"
    merged.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"💾 CSV 備份 → {csv_path}")

    conn.close()
    print("✅ 資料整合完成！")


if __name__ == "__main__":
    main()
