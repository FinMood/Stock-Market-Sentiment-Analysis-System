import os
import pandas as pd

def verify_all_merged_data(output_dir="output"):
    stock_ids = ["0050", "2308", "2330", "2454"]
    print("🔍 開始全面驗證各股合併後的資料完整性...")

    for stock_id in stock_ids:
        file_path = os.path.join(output_dir, f"sentiment_stock_merged_{stock_id}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ [略過] 找不到 {stock_id} 的合併報表：{file_path}")
            continue

        print(f"\n-----------------------------------------")
        print(f"📊 正在檢查股票：{stock_id} ({file_path})")
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        
        print(f"• 總交易日數 (Rows)：{len(df)}")
        print(f"• 資料日期區間：{df['date'].min()} ～ {df['date'].max()}")
        print(f"• 前 2 筆預覽：\n{df.head(2)}")

    print("\n✨ [驗證作業全部完成]")

if __name__ == "__main__":
    verify_all_merged_data()