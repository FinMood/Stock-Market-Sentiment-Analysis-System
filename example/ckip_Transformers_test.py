# 台灣中央研究院開發，專門針對繁體中文
#pip3 install ckip-transformers
#pip3 install torch
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter

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
# 取得所有新聞標題
titles = df["title"].tolist()
# 一次全部斷詞
result = ws_driver(titles)
# 跑迴圈印出每一個標題的斷詞結果
for i, words in enumerate(result):
    print("原始標題：", titles[i])
    print("斷詞結果：", words)
    print("-" * 40)

#