import os
import pandas as pd
import sqlite3

def save_stock_to_sqlite(df, db_path="taiwan50_sentiment.db"):
    print(f"正在連線至 SQLite 資料庫 ({db_path})...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 建立股價資料表（文字型態的 stock_id）
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
    
    # if_exists="replace" 會直接把舊的錯誤資料表覆蓋清空
    df.to_sql("stock_data", conn, if_exists="replace", index=False)
    
    cursor.execute("SELECT COUNT(*) FROM stock_data")
    total_rows = cursor.fetchone()[0]
    print(f"🎉 股價資料庫重新覆蓋成功！目前 `stock_data` 表內共有 {total_rows} 筆正確資料。")
    conn.close()

def main():
    stock_fname = "source/0050.csv"
    if not os.path.exists(stock_fname):
        print(f"找不到股價檔案 {stock_fname}")
        return
        
    stock_df = pd.read_csv(stock_fname)
    stock_df.columns = stock_df.columns.str.lower()
    stock_df['date'] = pd.to_datetime(stock_df['date']).dt.strftime('%Y-%m-%d')
    
    # 強制將 stock_id 設定為字串 "0050" 避免變成 50.0
    stock_df['stock_id'] = '0050'
    stock_df['stock_id'] = stock_df['stock_id'].astype(str)
    
    required_columns = ["date", "stock_id", "open", "close", "volume"]
    final_df = stock_df[required_columns].dropna() # 自動剔除 None 空白列
    
    save_stock_to_sqlite(final_df)

if __name__ == "__main__":
    main()