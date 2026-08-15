import os
import pandas as pd


def verify_all_merged_data(output_dir="output"):
    stock_ids = ["2308", "2330", "2454"]
    print("🔍 開始全面驗證各股合併後的資料完整性...\n")

    all_pass = True

    for stock_id in stock_ids:
        file_path = os.path.join(output_dir, f"sentiment_stock_merged_{stock_id}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ [略過] 找不到 {stock_id} 的合併報表：{file_path}")
            all_pass = False
            continue

        print(f"-----------------------------------------")
        print(f"📊 正在檢查股票：{stock_id} ({file_path})")
        df = pd.read_csv(file_path, encoding="utf-8-sig")

        # 基本資訊
        print(f"  • 總交易日數 (Rows)：{len(df)}")
        print(f"  • 資料日期區間：{df['date'].min()} ～ {df['date'].max()}")

        # 檢查必要欄位是否存在
        required_cols = ["date", "stock_id", "open", "close", "volume", "avg_sentiment", "news_count"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            print(f"  ❌ 缺少欄位：{missing_cols}")
            all_pass = False
        else:
            print(f"  ✅ 欄位完整：{list(df.columns)}")

        # 檢查 avg_sentiment 是否有 NaN（代表完全沒新聞覆蓋的交易日）
        if "avg_sentiment" in df.columns:
            nan_count = df["avg_sentiment"].isna().sum()
            total = len(df)
            if nan_count > 0:
                print(f"  ⚠️ avg_sentiment 有 {nan_count}/{total} 筆為 NaN（{nan_count/total*100:.1f}% 交易日無新聞覆蓋）")
                all_pass = False
            else:
                print(f"  ✅ avg_sentiment 無 NaN")

        # 檢查 news_count 為 0 的比例（情緒覆蓋率）
        if "news_count" in df.columns:
            zero_news = (df["news_count"] == 0).sum()
            coverage = (1 - zero_news / len(df)) * 100
            print(f"  • 新聞覆蓋率：{coverage:.1f}%（{zero_news}/{len(df)} 個交易日無新聞）")

        # 檢查日期是否有重複
        dup_dates = df["date"].duplicated().sum()
        if dup_dates > 0:
            print(f"  ⚠️ 發現 {dup_dates} 筆重複日期")
            all_pass = False
        else:
            print(f"  ✅ 日期無重複")

        # 情緒分數分布摘要
        if "avg_sentiment" in df.columns and not df["avg_sentiment"].isna().all():
            print(f"  • 情緒分數統計：mean={df['avg_sentiment'].mean():.4f}, "
                  f"min={df['avg_sentiment'].min():.4f}, "
                  f"max={df['avg_sentiment'].max():.4f}")

        # 前 2 筆預覽
        print(f"  • 前 2 筆預覽：\n{df.head(2).to_string(index=False)}")
        print()

    if all_pass:
        print("✨ [驗證全部通過] 所有股票的合併報表資料完整無誤！")
    else:
        print("⚠️ [驗證完成] 有部分檢查項目需要注意，請查看上方詳情。")


if __name__ == "__main__":
    verify_all_merged_data()