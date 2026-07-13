import sqlite3
import pandas as pd

def main():
    db_path = "taiwan50_sentiment.db"
    print(f"正在連線至 {db_path} 進行 SQL 關聯查詢...")
    
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        s.date AS 交易日期,
        s.stock_id AS 股價代碼,
        s.close AS 大盤收盤價,
        n.stock_id AS 新聞個股代碼,
        n.title AS 新聞標題,
        n.sentiment AS 新聞輿情分數
    FROM 
        stock_data s
    INNER JOIN 
        news_sentiment n ON s.date = n.date
    ORDER BY 
        s.date ASC 
    LIMIT 10;
    """
    
    result_df = pd.read_sql_query(query, conn)
    
    print("\n======= 核心關聯驗證結果 =======")
    if result_df.empty:
        print("💡 依然無交集，可能兩張表的 date 內容完全沒有重疊交易日。")
    else:
        print(result_df.to_string())
        print(f"\n🎉 成功驗證！資料庫已經可以跨表 Join 資料了。")
        
    conn.close()

if __name__ == "__main__":
    main()