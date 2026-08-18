import os
import glob
import pandas as pd


def merge_sentiment_and_stock_data(
    score_dir="score_data",
    stock_files=None,
    output_dir="output"
):
    """
    【核心功能：時間序列與位階合併 (Time-Series Alignment)】
    透過 Python Pandas 將每日新聞輿情評分（多引擎評分結果）與多檔股票價格資料，
    依據「日期 (date)」與「股票代號 (stock_id)」進行時間軸的 LEFT JOIN 對齊。
    同時進行每日群組化計算（Group by），產出每日平均情緒 (avg_sentiment) 與聲量 (news_count)。

    修正項目：
    - 支援統一格式 all_scores CSV（含 score_Roberta / score_ckipbert / score_finbert / score_jieba / score_llm）
    - 支援 llm_results.csv（欄位為 llm_score）
    - 支援舊版獨立引擎 CSV（使用 score 或 score_normalized 欄位）
    - merge 時以 date + stock_id 為複合 key，避免跨股票新聞交叉污染
    """
    if stock_files is None:
        stock_files = {
            "2308": "source/2308_price.csv",
            "2330": "source/2330_price.csv",
            "2454": "source/2454_price.csv"
        }

    os.makedirs(output_dir, exist_ok=True)

    # ── 讀取所有評分引擎的 CSV 並合併 ──
    score_files = glob.glob(os.path.join(score_dir, "*.csv"))
    if not score_files:
        print(f"❌ [錯誤] 在 {score_dir}/ 底下找不到任何評分 CSV 檔案")
        return

    # 辨識所有 score_* 欄位前綴，用於偵測 all_scores 統一格式
    SCORE_COL_PREFIX = "score_"
    KNOWN_SCORE_COLS = ["score_Roberta", "score_ckipbert", "score_finbert", "score_jieba", "score_llm"]

    frames = []
    for sf in score_files:
        print(f"📂 讀取評分檔案：{sf}")
        df_tmp = pd.read_csv(sf, encoding="utf-8-sig")
        basename = os.path.basename(sf)

        # ── 格式一：統一 all_scores CSV（含多個 score_* 欄位）──
        found_score_cols = [c for c in KNOWN_SCORE_COLS if c in df_tmp.columns]
        if len(found_score_cols) >= 2:
            print(f"   ↳ 偵測為統一格式 (all_scores)，包含引擎：{found_score_cols}")
            id_cols = [c for c in df_tmp.columns if c not in found_score_cols]
            df_melted = df_tmp.melt(
                id_vars=id_cols,
                value_vars=found_score_cols,
                var_name="engine",
                value_name="score"
            )
            # 清理引擎名稱：score_Roberta -> roberta, score_llm -> llm
            df_melted["engine"] = df_melted["engine"].str.replace(SCORE_COL_PREFIX, "", n=1).str.lower()
            # 移除 score 為 NaN 的列（某些引擎可能對該筆新聞沒有評分）
            df_melted = df_melted.dropna(subset=["score"])
            frames.append(df_melted)
            continue

        # ── 格式二：llm_results.csv（欄位為 llm_score）──
        if "llm_score" in df_tmp.columns:
            print(f"   ↳ 偵測為 LLM 獨立格式 (llm_score)")
            df_tmp["score"] = df_tmp["llm_score"]
            df_tmp["engine"] = "llm"
            frames.append(df_tmp)
            continue

        # ── 格式三：舊版獨立引擎 CSV ──
        engine = "unknown"
        for tag in ["finbert", "ckipbert", "jieba", "roberta", "wang", "llm"]:
            if tag in basename.lower():
                engine = tag
                break
        df_tmp["engine"] = engine
        
        # RoBERTa / wang 的 CSV 用 score_normalized 作為方向正規化分數
        if "score_normalized" in df_tmp.columns and engine in ("roberta", "wang"):
            df_tmp["score"] = df_tmp["score_normalized"]
        
        frames.append(df_tmp)

    df_news = pd.concat(frames, ignore_index=True)
    print(f"✅ 合併後的新聞情緒總筆數：{len(df_news)}")

    # 驗證必要欄位
    for col in ["date", "stock_id", "score"]:
        if col not in df_news.columns:
            print(f"❌ [錯誤] 合併後的新聞資料缺少 '{col}' 欄位！")
            return

    # 統一日期格式
    df_news["date_only"] = pd.to_datetime(df_news["date"]).dt.strftime("%Y-%m-%d")
    # 將 stock_id 轉成字串以統一型態
    df_news["stock_id"] = df_news["stock_id"].astype(str)

    # ── 針對每一檔股票分別進行時間序列合併 ──
    for stock_id, stock_path in stock_files.items():
        if not os.path.exists(stock_path):
            print(f"⚠️ [略過] 找不到代號 {stock_id} 的股價檔案：{stock_path}")
            continue

        print(f"\n🔄 正在處理股票代號: {stock_id} (對應檔案: {stock_path})")
        df_stock = pd.read_csv(stock_path, encoding="utf-8-sig")

        if "date" not in df_stock.columns:
            print(f"⚠️ [略過] 股票 {stock_id} 的資料缺少 'date' 欄位")
            continue

        df_stock["date_only"] = pd.to_datetime(df_stock["date"]).dt.strftime("%Y-%m-%d")

        # ★ 關鍵修正：先按 stock_id 過濾新聞，避免跨股票污染
        df_news_filtered = df_news[df_news["stock_id"] == stock_id].copy()

        if df_news_filtered.empty:
            print(f"⚠️ [警告] 股票 {stock_id} 在新聞資料中沒有對應的情緒評分")
            df_grouped = df_stock.copy()
            df_grouped["stock_id"] = stock_id
            df_grouped["avg_sentiment"] = None
            df_grouped["news_count"] = 0
        else:
            # 先群組化計算每日平均情緒 (avg_sentiment) 與聲量 (news_count)
            df_daily_sentiment = (
                df_news_filtered
                .groupby("date_only")
                .agg(
                    avg_sentiment=("score", "mean"),
                    news_count=("score", "count")
                )
                .reset_index()
            )

            # 以股價交易日為基準，用 date_only 進行 LEFT JOIN
            df_grouped = pd.merge(
                df_stock,
                df_daily_sentiment,
                on="date_only",
                how="left"
            )
            df_grouped["stock_id"] = stock_id
            # 沒有新聞的交易日，填入 0
            df_grouped["avg_sentiment"] = df_grouped["avg_sentiment"].fillna(0.0)
            df_grouped["news_count"] = df_grouped["news_count"].fillna(0).astype(int)

        # 整理最終欄位結構
        cols_to_keep = ["date_only", "stock_id", "open", "close", "volume", "avg_sentiment", "news_count"]
        existing_cols = [c for c in cols_to_keep if c in df_grouped.columns]
        df_final_out = df_grouped[existing_cols].rename(columns={"date_only": "date"})

        # 輸出獨立個股對齊報表
        output_file = os.path.join(output_dir, f"sentiment_stock_merged_{stock_id}.csv")
        df_final_out.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"✅ [成功] 股票 {stock_id} 時間序列對齊完畢，已儲存至：{output_file} (共 {len(df_final_out)} 筆)")

    print("\n🎉 全部股票合併流程完成！")


if __name__ == "__main__":
    print("🚀 === 開始執行多檔股票時間序列與位階合併流程 ===")
    merge_sentiment_and_stock_data()