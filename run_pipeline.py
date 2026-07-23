import os
import glob
import re
import pandas as pd
from difflib import SequenceMatcher
from sentiment_analyzer import analyze_and_save_csv

# ==================== 1. 新聞檔案自動搜尋 ====================
def find_news_csv():
    candidate_paths = [
        "TaiwanStockNews_test.csv",
        "./data/TaiwanStockNews_test.csv",
        "TaiwanStockNews.csv",
        "./data/TaiwanStockNews.csv",
        "raw_news.csv",
        "./data/raw_news.csv",
        "news.csv",
        "./data/news.csv"
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            print(f"🎯 [自動偵測] 成功找到新聞檔案：{path}")
            return path

    search_dirs = [".", "./data"]
    all_csvs = []
    for d in search_dirs:
        if os.path.exists(d):
            all_csvs.extend(glob.glob(os.path.join(d, "*.csv")))

    input_csvs = [
        f for f in all_csvs 
        if "results" not in f and "comparison" not in f and "cache" not in f and "output" not in f
    ]

    if input_csvs:
        selected_file = input_csvs[0]
        print(f"🔍 [自動搜尋] 自動採用找到的第一個 CSV：{selected_file}")
        return selected_file

    return None


def load_news_data() -> pd.DataFrame:
    csv_path = find_news_csv()

    if csv_path:
        for encoding in ['utf-8-sig', 'utf-8', 'big5']:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✅ 成功載入 {len(df)} 筆新聞資料（編碼：{encoding}）")
                return df
            except UnicodeDecodeError:
                continue

    print("⚠️ 未找到任何 valid 的新聞 CSV 檔案，將啟用預設範例資料執行。")
    return pd.DataFrame([
        {"id": 1, "date": "2026-06-20", "title": "台積電創新高，股價大漲"},
        {"id": 2, "date": "2026-06-21", "title": "市場恐懼情緒蔓延，大盤爆量下跌"},
        {"id": 3, "date": "2026-06-22", "title": "聯準會宣布按兵不動，觀望氣氛濃"}
    ])


# ==================== 2. 跨平台類似標題去重機制 ====================
def clean_title(title):
    """移除媒體前後綴標籤與標點符號，純化文字進行相似度比對"""
    title = re.sub(r'【.*?】|\[.*?\]|\(.*?\)|「.*?」', '', str(title))
    title = re.sub(r'[^\w\s]', '', title)
    return title.strip()


def filter_similar_titles(df, threshold=0.85):
    """依照模糊相似度對改寫新聞去重"""
    if 'title' not in df.columns or len(df) == 0:
        return df

    unique_rows = []
    seen_cleaned_titles = []

    for _, row in df.iterrows():
        raw_title = row['title']
        cleaned = clean_title(raw_title)

        if not cleaned:
            continue

        is_similar = False
        for seen in seen_cleaned_titles:
            # 計算 Jaccard / Sequence 比對
            ratio = SequenceMatcher(None, cleaned, seen).ratio()
            if ratio >= threshold:
                is_similar = True
                break

        if not is_similar:
            seen_cleaned_titles.append(cleaned)
            unique_rows.append(row)

    filtered_df = pd.DataFrame(unique_rows).reset_index(drop=True)
    print(f"🧹 [相似標題過濾] 原資料 {len(df)} 筆 -> 去重後剩餘 {len(filtered_df)} 筆新聞 (相似門檻: {threshold*100:.0f}%)")
    return filtered_df


# ==================== 3. 主流程邏輯 ====================
def run_pipeline():
    print("========================================")
    print("🚀 開始執行台股新聞情緒分析 Pipeline")
    print("========================================\n")

    # 1. 建立輸出目錄
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # 2. 讀取新聞資料
    df_news = load_news_data()

    # 3. 跨平台改寫類似新聞去重
    df_news = filter_similar_titles(df_news, threshold=0.85)

    # 4. 設定特定期間篩選
    START_DATE = "2026-02-23"
    END_DATE   = "2026-03-23"

    if 'date' in df_news.columns:
        df_news['date_dt'] = pd.to_datetime(df_news['date'], errors='coerce')
            # mask = (df_news['date_dt'] >= START_DATE) & (df_news['date_dt'] <= END_DATE)
            # df_news = df_news[mask].drop(columns=['date_dt']).reset_index(drop=True)
        print(f"📅 [特定期間篩選] （{START_DATE} ~ {END_DATE}），符合條件剩餘新聞：{len(df_news)} 筆\n")
    else:
        print("⚠️ 未發現 'date' 欄位，將跳過日期過濾處理全數資料。\n")

    # 5. 執行增量情緒分析並匯出 CSV
    df_dict, df_llm = analyze_and_save_csv(df_news, output_dir=output_dir)

    print("\n========================================")
    print("🎉 Pipeline 執行完成！")
    print(f"📁 輸出檔案已存放在：{os.path.abspath(output_dir)}")
    print("  ├─ dictionary_results.csv  (字典結果)")
    print("  ├─ llm_results.csv         (LLM 結果)")
    print("  ├─ sentiment_comparison.csv(對比結果)")
    print("  └─ sentiment_cache.csv     (歷史快取庫)")
    print("========================================")

if __name__ == "__main__":
    run_pipeline()