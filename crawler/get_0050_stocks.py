from io import StringIO
from pathlib import Path
import pandas as pd


def get_0050_stocks(csv_path="source/0050_list.csv"):
    """讀取元大 0050 持股 CSV"""

    # 💡 修正關鍵 1：鎖定相對於當前專案/腳本的絕對路徑，避免執行目錄搞錯
    current_dir = Path(__file__).resolve().parent.parent  
    target_path = current_dir / csv_path
    if not target_path.exists():
        raise FileNotFoundError(
            f"找不到 CSV 檔案！請確認路徑是否存在：{target_path}"
        )

    # 讀取整個 CSV
    with open(target_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    stock_header = None
    stock_end = None

    # 找股票表開始
    for i, line in enumerate(lines):
        clean_line = line.strip().replace(" ", "")  # 移除所有隱形空格

        # 💡 修正關鍵 2：改用包含比對 (in)，避免因為官方微調欄位或多逗號而抓不到
        if "商品代碼" in clean_line and "商品名稱" in clean_line:
            stock_header = i
            continue

        # 找股票表結束（遇到下一個區塊）
        if stock_header is not None:
            if clean_line.startswith("基金權重-期貨") or "期貨" in clean_line:
                stock_end = i
                break

    if stock_header is None:
        raise ValueError(
            "在 CSV 內找不到含有 '商品代碼' 與 '商品名稱' 的標頭欄位！"
        )

    # 如果沒找到結尾，就直接切到檔案末尾
    stock_lines = (
        lines[stock_header:stock_end] if stock_end else lines[stock_header:]
    )

    df = pd.read_csv(StringIO("".join(stock_lines)))

    # 清洗欄位名稱的空格（防止 "商品代碼 " 後面帶空白）
    df.columns = df.columns.str.strip()

    df = df[["商品代碼", "商品名稱"]]
    df["商品代碼"] = df["商品代碼"].astype(str)

    return df

# 測試用
if __name__ == "__main__":
    try:
        stocks = get_0050_stocks()
        print(stocks.head())  # 先印出前幾行測試
        print("-" * 40)
        print(f"共 {len(stocks)} 檔股票")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
