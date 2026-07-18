# 台灣中央研究院開發，專門針對繁體中文
#pip3 install ckip-transformers
#pip3 install torch
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter
import re #去除標點符號

# 最快（Level 1）： model="albert-tiny"
# 平衡（Level 2）： model="albert-base"
# 最精確（Level 3）： model="bert-base"

ws_driver = CkipWordSegmenter(model="albert-base", device=-1)
# 測試一下
text = ["金融新聞情緒分析"]

result = ws_driver(text)

words = result[0]

print(words)

# 讀取CSV
df = pd.read_csv("TaiwanStockNews_test.csv")

# ── 去除重複標題 ──────────────────────────────────────
before = len(df)

# 去除重複標題 (# 整列完全相同才去除 # 只看 title 欄是否重複)

df["title"] = (
    df["title"]
    .str.strip()
    .str.replace(r"[\s,，。！？、；：""''【】《》()（）]", "", regex=True)
)
df = df.drop_duplicates(subset=["date","title"]) 
after = len(df)

print(f"去重前：{before} 筆")
print(f"去重後：{after} 筆")
print(f"移除了：{before - after} 筆重複標題")

# 取得所有新聞標題
titles = df["title"].tolist()
# # 一次全部斷詞
# result = ws_driver(titles)
# # 跑迴圈印出每一個標題的斷詞結果
# for i, words in enumerate(result):
#     print("原始標題：", titles[i])
#     print("斷詞結果：", words)
#     print("-" * 40)

#