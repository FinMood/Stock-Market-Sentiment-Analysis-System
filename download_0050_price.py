import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def main():
    ticker = "0050.TW"
    start_date = "2026-02-23"
    
    # 防錯機制：如果設定的結束時間比今天還晚，就自動以今天作為結束日
    end_date = "2026-06-23"
    if datetime.strptime(end_date, "%Y-%m-%d") > datetime.now():
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"正在從 Yahoo Finance 下載 {ticker} 歷史股價 ({start_date} ~ {end_date})...")
    
    # 下載歷史股價
    df = yf.download(ticker, start=start_date, end=end_date)
    
    if df.empty:
        print("❌ 下載失敗，可能該區間尚無交易資料，請確認時間設定。")
        return
        
    # 清洗與結構化重組
    df = df.reset_index()
    df['stock_id'] = '0050'
    
    # 修改欄位名稱為小寫，符合資料庫欄位
    df = df.rename(columns={
        'Date': 'date',
        'Open': 'open',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # 轉換時間為標準 YYYY-MM-DD 格式
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # 只篩選出需要的標準欄位
    final_df = df[['date', 'stock_id', 'open', 'close', 'volume']]
    
    # 儲存到 source 資料夾覆蓋原本錯誤的檔案，作為正確的 Input
    os.makedirs("source", exist_ok=True)
    correct_stock_fname = "source/0050.csv"
    final_df.to_csv(correct_stock_fname, index=False, encoding="utf-8")
    
    print(f"🎉 正確的 0050 歷史股價已成功下載並覆蓋至：{correct_stock_fname}")
    print(final_df.head(3))

if __name__ == "__main__":
    main()