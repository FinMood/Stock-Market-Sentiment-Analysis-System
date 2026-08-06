import os
import pandas as pd
import sqlite3

def save_stock_to_sqlite(df, db_path="taiwan50_sentiment.db"):
    print(f"正在連線至 SQLite 資料庫 ({db_path})...")
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
    
    df.to_sql("stock_data", conn, if_exists="replace", index=False)
    
    cursor.execute("SELECT COUNT(*) FROM stock_data")
    total_rows = cursor.fetchone()[0]
    print(f"🎉 股價資料庫重新覆蓋成功！目前 `stock_data` 表內共有 {total_rows} 筆正確資料。")
    conn.close()

def main():
    stock_fname = "source/0050_price.csv"
    if not os.path.exists(stock_fname):
        print(f"找不到股價檔案 {stock_fname}")
        return
        
    # 1. 讀取原始 CSV
    stock_df = pd.read_csv(stock_fname, encoding="utf-8-sig")
    stock_df.columns = stock_df.columns.str.lower()
    
    # 2. 【防呆清洗】過濾掉含有 .TW 或日期欄位為空值的垃圾行（解決第二行型態宣告污染問題）
    if 'date' in stock_df.columns:
        stock_df = stock_df[stock_df['date'].notna() & ~stock_df['date'].astype(str).str.contains(r'\.TW', na=False)]
    
    # 3. 統一日期格式與股票代碼
    stock_df['date'] = pd.to_datetime(stock_df['date']).dt.strftime('%Y-%m-%d')
    stock_df['stock_id'] = '0050'
    stock_df['stock_id'] = stock_df['stock_id'].astype(str)
    
    # 4. 確保數值欄位型態正確
    numeric_cols = ['open', 'close', 'volume']
    for col in numeric_cols:
        if col in stock_df.columns:
            stock_df[col] = pd.to_numeric(stock_df[col], errors='coerce')

    required_columns = ["date", "stock_id", "open", "close", "volume"]
    final_df = stock_df[required_columns].dropna()
    
    save_stock_to_sqlite(final_df)

if __name__ == "__main__":
    main()