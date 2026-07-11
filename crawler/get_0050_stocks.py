from pathlib import Path
import pandas as pd


def get_0050_stocks(csv_path="source/0050.csv"):
    """
    讀取元大 0050 持股 CSV

    Returns
    -------
    pandas.DataFrame
        欄位：
        商品代碼
        商品名稱
    """

    csv_path = Path(csv_path)

    # 讀取整個 CSV
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    stock_header = None
    stock_end = None

    # 找股票表開始
    for i, line in enumerate(lines):
        if line.strip() == "商品代碼,商品名稱,商品數量,商品權重":
            stock_header = i
            continue

        # 找股票表結束（遇到下一個區塊）
        if stock_header is not None:
            if line.startswith("基金權重-期貨"):
                stock_end = i
                break

    if stock_header is None:
        raise ValueError("找不到股票資料表")

    # 股票資料
    stock_lines = lines[stock_header:stock_end]

    from io import StringIO

    df = pd.read_csv(StringIO("".join(stock_lines)))

    df = df[["商品代碼", "商品名稱"]]

    df["商品代碼"] = df["商品代碼"].astype(str)

    return df

# 驗證是否成功
# if __name__ == "__main__":
#     stocks = get_0050_stocks()
#     print(stocks)
#     print("-" * 40)
#     print(f"共 {len(stocks)} 檔股票")