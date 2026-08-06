import os
import pandas as pd
from sentiment_analyzer import analyze_and_save_csv

def run_news_pipeline():
    print("🚀 [Pipeline] 開始執行輿情自動化處理流程...")
    
    # 1. 路徑設定
    source_dir = "source"
    output_dir = "output"
    temp_dir = "temp_data"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    input_file = os.path.join(source_dir, "TaiwanStockNews_test.csv")
    
    if not os.path.exists(input_file):
        print(f"❌ [錯誤] 找不到原始新聞檔案：{input_file}")
        return

    # 2. 讀取原始資料
    print(f"📂 正在讀取原始檔案：{input_file}")
    df = pd.read_csv(input_file, encoding="utf-8-sig")

    # 3. 資料清洗與標準化 (確保 stock_id 為字串且不遺失前導零、統一日期格式)
    if 'stock_id' in df.columns:
        df['stock_id'] = df['stock_id'].astype(str).str.zfill(4)
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 4. 跨平台標題模糊去重 (基於 title 欄位去重，確保進到 LLM 前資料乾淨)
    initial_count = len(df)
    df.drop_duplicates(subset=['title'], keep='first', inplace=True)
    print(f"🧹 [資料清洗] 原始筆數：{initial_count} | 去重後筆數：{len(df)}")

    # 5. 儲存清洗後的中間過渡檔至 temp_data 目錄
    cleaned_temp_path = os.path.join(temp_dir, "news_cleaned.csv")
    df.to_csv(cleaned_temp_path, index=False, encoding="utf-8-sig")
    print(f"💾 [清洗存檔] 中間乾淨資料已暫存至：{cleaned_temp_path}")

    # 6. 進入情緒分析核心 (執行 Groq 批次評分與字典保底)
    print("\n🤖 [情緒分析] 啟動 sentiment_analyzer 進行評分...")
    df_dict, df_llm = analyze_and_save_csv(df, output_dir=output_dir)

    print("\n✨ [Pipeline] 輿情處理流程全部執行完畢！所有結果已安全歸檔至 output/ 目錄。")

if __name__ == "__main__":
    run_news_pipeline()