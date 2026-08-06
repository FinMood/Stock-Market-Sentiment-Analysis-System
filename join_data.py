import os
import pandas as pd

def merge_sentiment_and_stock_data(
    news_file="output/news_sentiment_report.csv",
    stock_files=None,
    output_dir="output"
):
    """
    【核心功能：時間序列與位階合併 (Time-Series Alignment)】
    透過 Python Pandas 將每日新聞輿情評分（大批次 LLM 評分結果）與多檔股票價格資料，
    依據「日期 (date)」與「股票代號 (stock_id)」進行時間軸的 LEFT JOIN 對齊。
    同時進行每日群組化計算（Group by），產出每日平均情緒 (avg_sentiment) 與聲量 (news_count)。
    """
    if stock_files is None:
        stock_files = {
            "0050": "source/0050_price.csv",
            "2308": "source/2308_price.csv",
            "2330": "source/2330_price.csv",
            "2454": "source/2454_price.csv"
        }

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(news_file):
        print(f"❌ [錯誤] 找不到新聞輿情檔案：{news_file}")
        return

    print(f"📂 正在讀取總體新聞輿情檔案：{news_file}")
    df_news = pd.read_csv(news_file, encoding="utf-8-sig")

    if 'date' not in df_news.columns:
        print("⚠️ [警告] 新聞資料中缺少 'date' 欄位！")
        return

    # 統一將新聞日期轉為標準字串格式 (YYYY-MM-DD)，以利跨表時間序列對齊
    df_news['date_only'] = pd.to_datetime(df_news['date']).dt.strftime('%Y-%m-%d')

    # 針對每一檔股票分別進行時間序列合併
    for stock_id, stock_path in stock_files.items():
        if not os.path.exists(stock_path):
            print(f"⚠️ [略過] 找不到代號 {stock_id} 的股價檔案：{stock_path}")
            continue

        print(f"\n🔄 正在處理股票代號: {stock_id} (對應檔案: {stock_path})")
        df_stock = pd.read_csv(stock_path, encoding="utf-8-sig")

        if 'date' not in df_stock.columns:
            print(f"⚠️ [略過] 股票 {stock_id} 的資料缺少 'date' 欄位")
            continue

        df_stock['date_only'] = pd.to_datetime(df_stock['date']).dt.strftime('%Y-%m-%d')

        # 執行時間序列與位階合併 (以股價交易日為基準進行 LEFT JOIN)
        df_merged = pd.merge(
            df_stock,
            df_news[['date_only', 'llm_score' if 'llm_score' in df_news.columns else 'sentiment_score', 'title']].rename(columns={'llm_score': 'sentiment_score'}),
            on='date_only',
            how='left'
        )

        # 依交易日群組化計算：當日平均情緒 (avg_sentiment) 與市場聲量 (news_count)
        if 'sentiment_score' in df_merged.columns:
            df_grouped = df_merged.groupby(['date_only', 'stock_id' if 'stock_id' in df_stock.columns else 'date_only']).agg(
                open=('open', 'first'),
                close=('close', 'first'),
                volume=('volume', 'first'),
                avg_sentiment=('sentiment_score', 'mean'),
                news_count=('title', 'count')
            ).reset_index()
            
            df_grouped['stock_id'] = stock_id
        else:
            df_grouped = df_stock.copy()
            df_grouped['avg_sentiment'] = 0.0
            df_grouped['news_count'] = 0

        # 整理最終欄位結構
        cols_to_keep = ['date_only', 'stock_id', 'open', 'close', 'volume', 'avg_sentiment', 'news_count']
        existing_cols = [c for c in cols_to_keep if c in df_grouped.columns]
        df_final_out = df_grouped[existing_cols].rename(columns={'date_only': 'date'})

        # 輸出獨立個股對齊報表至 output/
        output_file = os.path.join(output_dir, f"sentiment_stock_merged_{stock_id}.csv")
        df_final_out.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"✅ [成功] 股票 {stock_id} 時間序列對齊完畢，已儲存至：{output_file} (共 {len(df_final_out)} 筆)")

if __name__ == "__main__":
    print("🚀 === 開始執行多檔股票時間序列與位階合併流程 ===")
    merge_sentiment_and_stock_data()