import os
import glob
import pandas as pd
import numpy as np


def compute_divergence_signals(
    input_dir="output",
    output_dir="output",
    return_window=3
):
    """
    【量化門檻定義 & 背離訊號矩陣 (Divergence Signal Matrix)】

    讀取 join_data.py 產出的各股合併報表，計算：
    1. return_3d：近 3 個交易日累積漲跌幅
    2. 以三檔合併的歷史資料計算統計分位數 (Percentile) 門檻
    3. 依據 README 定義的背離訊號矩陣，產出紅綠燈決策警示

    策略：三檔股票合併計算分位數（增加樣本量，適用 PoC 階段）
    未來資料量充足後，可改為各股獨立計算。
    """
    stock_ids = ["2308", "2330", "2454"]

    # ── Step 1：讀取所有個股合併報表 ──
    all_frames = []
    for stock_id in stock_ids:
        file_path = os.path.join(input_dir, f"sentiment_stock_merged_{stock_id}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ [略過] 找不到 {stock_id} 的合併報表：{file_path}")
            continue

        df = pd.read_csv(file_path, encoding="utf-8-sig")
        df["date"] = pd.to_datetime(df["date"])
        df["stock_id"] = str(stock_id)
        df = df.sort_values("date").reset_index(drop=True)

        # 計算近 N 日累積漲跌幅 (per stock)
        df["return_3d"] = (df["close"] - df["close"].shift(return_window)) / df["close"].shift(return_window)

        all_frames.append(df)
        print(f"📂 已讀取 {stock_id}：{len(df)} 筆交易日")

    if not all_frames:
        print("❌ 沒有任何可用的合併報表，請先執行 join_data.py")
        return

    df_all = pd.concat(all_frames, ignore_index=True)
    print(f"\n📊 三檔合併共 {len(df_all)} 筆，用於統一分位數計算")

    # ── Step 2：計算統一分位數門檻 ──
    # 移除 return_3d 為 NaN 的前 N 筆（因 shift 產生）
    df_valid = df_all.dropna(subset=["return_3d", "avg_sentiment"])
    print(f"📊 有效計算筆數（排除前 {return_window} 日 NaN）：{len(df_valid)}")

    # 情緒分數分位數
    sent_p10 = df_valid["avg_sentiment"].quantile(0.10)
    sent_p25 = df_valid["avg_sentiment"].quantile(0.25)
    sent_p50 = df_valid["avg_sentiment"].quantile(0.50)
    sent_p75 = df_valid["avg_sentiment"].quantile(0.75)
    sent_p90 = df_valid["avg_sentiment"].quantile(0.90)

    # 股價漲跌幅分位數
    ret_p10 = df_valid["return_3d"].quantile(0.10)
    ret_p25 = df_valid["return_3d"].quantile(0.25)
    ret_p75 = df_valid["return_3d"].quantile(0.75)
    ret_p90 = df_valid["return_3d"].quantile(0.90)

    print(f"\n{'='*50}")
    print(f"📈 統一分位數門檻（三檔合併計算）")
    print(f"{'='*50}")
    print(f"  情緒分數 P10={sent_p10:.4f}  P25={sent_p25:.4f}  P75={sent_p75:.4f}  P90={sent_p90:.4f}")
    print(f"  漲跌幅   P10={ret_p10:.4f}  P25={ret_p25:.4f}  P75={ret_p75:.4f}  P90={ret_p90:.4f}")
    print(f"{'='*50}")

    # ── Step 3：標記情緒等級與漲跌等級 ──
    def label_sentiment(score):
        if pd.isna(score):
            return "無資料"
        if score < sent_p10:
            return "🔴 極度悲觀"
        elif score < sent_p25:
            return "🟠 偏空"
        elif score <= sent_p75:
            return "⚪ 中性"
        elif score <= sent_p90:
            return "🟢 偏多"
        else:
            return "🟢🟢 極度樂觀"

    def label_return(ret):
        if pd.isna(ret):
            return "無資料"
        if ret < ret_p10:
            return "📉 大跌"
        elif ret < ret_p25:
            return "小跌"
        elif ret <= ret_p75:
            return "平盤震盪"
        elif ret <= ret_p90:
            return "小漲"
        else:
            return "📈 大漲"

    df_all["sentiment_level"] = df_all["avg_sentiment"].apply(label_sentiment)
    df_all["return_level"] = df_all["return_3d"].apply(label_return)

    # ── Step 4：計算背離訊號（紅綠燈） ──
    df_all["red_light"] = (df_all["avg_sentiment"] > sent_p90) & (df_all["return_3d"] > ret_p90)
    df_all["green_light"] = (df_all["avg_sentiment"] < sent_p10) & (df_all["return_3d"] < ret_p10)

    def assign_signal(row):
        if pd.isna(row["return_3d"]) or pd.isna(row["avg_sentiment"]):
            return "—"
        if row["red_light"]:
            return "🔴 紅燈（利多出盡，追高風險大）"
        elif row["green_light"]:
            return "🟢 綠燈（恐慌超賣，反彈機率高）"
        elif row["avg_sentiment"] > sent_p90 and row["return_3d"] < 0:
            return "🟡 觀望（樂觀但股價不買單）"
        elif row["avg_sentiment"] < sent_p10 and row["return_3d"] > 0:
            return "🟡 觀望（悲觀但股價未跌）"
        else:
            return "⚪ 正常"

    df_all["signal"] = df_all.apply(assign_signal, axis=1)

    # ── Step 5：輸出結果 ──
    os.makedirs(output_dir, exist_ok=True)

    # 輸出各股獨立決策表
    for stock_id in stock_ids:
        df_stock = df_all[df_all["stock_id"] == stock_id].copy()
        if df_stock.empty:
            continue

        output_cols = [
            "date", "stock_id", "open", "close", "volume",
            "avg_sentiment", "news_count", "return_3d",
            "sentiment_level", "return_level", "signal"
        ]
        existing_cols = [c for c in output_cols if c in df_stock.columns]
        df_out = df_stock[existing_cols].copy()
        df_out["date"] = df_out["date"].dt.strftime("%Y-%m-%d")

        out_path = os.path.join(output_dir, f"divergence_signal_{stock_id}.csv")
        df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ {stock_id} 決策表已儲存：{out_path} (共 {len(df_out)} 筆)")

    # 輸出合併總表
    all_output_cols = [
        "date", "stock_id", "open", "close", "volume",
        "avg_sentiment", "news_count", "return_3d",
        "sentiment_level", "return_level", "signal"
    ]
    existing_all_cols = [c for c in all_output_cols if c in df_all.columns]
    df_all_out = df_all[existing_all_cols].copy()
    df_all_out["date"] = df_all_out["date"].dt.strftime("%Y-%m-%d")

    all_path = os.path.join(output_dir, "divergence_signal_all.csv")
    df_all_out.to_csv(all_path, index=False, encoding="utf-8-sig")
    print(f"✅ 合併決策總表已儲存：{all_path} (共 {len(df_all_out)} 筆)")

    # ── Step 6：統計報告 ──
    print(f"\n{'='*50}")
    print("📋 背離訊號統計摘要")
    print(f"{'='*50}")

    signal_counts = df_all["signal"].value_counts()
    for sig, cnt in signal_counts.items():
        print(f"  {sig}：{cnt} 次")

    # 紅燈觸發後隔日表現
    df_red = df_all[df_all["red_light"]].copy()
    if not df_red.empty:
        print(f"\n🔴 紅燈觸發 {len(df_red)} 次")
        for stock_id in stock_ids:
            stock_red = df_red[df_red["stock_id"] == stock_id]
            if not stock_red.empty:
                dates = stock_red["date"].dt.strftime("%Y-%m-%d").tolist()
                print(f"  {stock_id}：{', '.join(dates)}")

    # 綠燈觸發後表現
    df_green = df_all[df_all["green_light"]].copy()
    if not df_green.empty:
        print(f"\n🟢 綠燈觸發 {len(df_green)} 次")
        for stock_id in stock_ids:
            stock_green = df_green[df_green["stock_id"] == stock_id]
            if not stock_green.empty:
                dates = stock_green["date"].dt.strftime("%Y-%m-%d").tolist()
                print(f"  {stock_id}：{', '.join(dates)}")

    # 輸出分位數門檻參考表
    thresholds = pd.DataFrame({
        "指標": ["情緒分數", "情緒分數", "情緒分數", "情緒分數",
                 "漲跌幅", "漲跌幅", "漲跌幅", "漲跌幅"],
        "分位": ["P10", "P25", "P75", "P90", "P10", "P25", "P75", "P90"],
        "門檻值": [sent_p10, sent_p25, sent_p75, sent_p90,
                   ret_p10, ret_p25, ret_p75, ret_p90]
    })
    thresholds_path = os.path.join(output_dir, "percentile_thresholds.csv")
    thresholds.to_csv(thresholds_path, index=False, encoding="utf-8-sig")
    print(f"\n📊 分位數門檻參考表已儲存：{thresholds_path}")

    print("\n🎉 背離訊號分析完成！")


if __name__ == "__main__":
    print("🚀 === 開始計算量化門檻與背離訊號 ===\n")
    compute_divergence_signals()
