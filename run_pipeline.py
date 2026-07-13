import os
import pandas as pd
import jieba
import sqlite3
from sentiment_analyzer import calculate_sentiment_score

def save_to_sqlite(df, db_path="taiwan50_sentiment.db"):
    """
    自動建立 SQLite 資料庫與表格，並將 DataFrame 資料寫入
    """
    print(f"正在連線至 SQLite 資料庫 ({db_path})...")
    # 連線到資料庫（若檔案不存在會自動建立）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 建立新聞情緒資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_sentiment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        stock_id TEXT,
        title TEXT,
        sentiment REAL
    )
    """)
    conn.commit()
    
    # 將資料寫入資料庫（if_exists='append' 代表每次執行是附加新資料，不覆蓋舊資料）
    # 如果你想每次執行都清空重來，可以改成 if_exists='replace'
    df.to_sql("news_sentiment", conn, if_exists="replace", index=False)
    
    # 驗證是否寫入成功
    cursor.execute("SELECT COUNT(*) FROM news_sentiment")
    total_rows = cursor.fetchone()[0]
    print(f"🎉 SQLite 資料庫更新成功！目前 `news_sentiment` 表內共有 {total_rows} 筆資料。")
    
    conn.close()

def main():
    # 1. 載入 NTUSD 情感詞典
    pos_fpath = "NTUSD/正面詞無重複_9365詞.txt"
    neg_fpath = "NTUSD/負面詞無重複_11230詞.txt"
    
    print("正在載入 NTUSD 情感詞典 (UTF-8)...")
    pos_df = pd.read_csv(pos_fpath, header=None, names=["word"], encoding="utf-8")
    neg_df = pd.read_csv(neg_fpath, header=None, names=["word"], encoding="utf-8")
    
    pos_set = set(pos_df["word"].tolist())
    neg_set = set(neg_df["word"].tolist())

    # 2. 載入新聞標題 CSV
    news_title_fname = "source/TaiwanStockNews_test.csv"
    if not os.path.exists(news_title_fname):
        print(f"找不到新聞檔案 {news_title_fname}，請確認檔案在 source 資料夾內。")
        return
        
    news_df = pd.read_csv(news_title_fname)
    print(f"成功載入新聞，共 {len(news_df)} 筆。開始整理時間格式...")

    # 資料清洗：將時間精簡為純日期 (YYYY-MM-DD)
    news_df['date'] = pd.to_datetime(news_df['date']).dt.strftime('%Y-%m-%d')

    # 3. 擴充自訂財經詞庫
    finance_words = ["台積電", "聯發科", "營收創新高", "未達預期", "台股", "翻紅", "翻黑"]
    for word in finance_words:
        jieba.add_word(word)

    # 4. 批次計算分數
    print("開始進行精確情緒評分...")
    sentiments = []
    for title in news_df["title"]:
        score = calculate_sentiment_score(title, pos_set, neg_set)
        sentiments.append(score)
        
    news_df["sentiment"] = sentiments
    
    # 5. 篩選標準欄位
    final_columns = ["date", "stock_id", "title", "sentiment"]
    output_df = news_df[final_columns]

    # 6. 建立 data 資料夾並儲存 CSV 備份
    os.makedirs("data", exist_ok=True)
    output_fname = "data/news_sentiment_processed.csv"
    output_df.to_csv(output_fname, index=False, encoding="utf-8")
    print(f"💾 加工 CSV 備份已儲存至：{output_fname}")

    # 7. 自動寫入 SQLite 資料庫
    save_to_sqlite(output_df)

if __name__ == "__main__":
    main()