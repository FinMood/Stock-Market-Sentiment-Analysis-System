# 台灣中央研究院開發，專門針對繁體中文
#pip3 install ckip-transformers
#pip3 install torch
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter
from transformers import pipeline
import re #去除標點符號

import gc
import psutil
import torch, os

torch.set_num_threads(os.cpu_count())

def print_mem(tag=""):
    mem = psutil.virtual_memory()
    print(f"[{tag}] 可用記憶體：{mem.available / (1024**3):.2f} GB / 總量 {mem.total / (1024**3):.2f} GB")

print_mem("開始前")

# 最快（Level 1）： model="albert-tiny"
# 平衡（Level 2）： model="albert-base"
# 最精確（Level 3）： model="bert-base"

# --- CKIP 斷詞模型 ---
ws_driver = CkipWordSegmenter(model="albert-tiny", device=-1)

# 測試一下
text = ["金融新聞情緒分析"]
result = ws_driver(text)
words = result[0]
print(words)

# 讀取CSV
df = pd.read_csv("/home/jessie_wang/Stock-Market-Sentiment-Analysis-System/source/TaiwanStockNews_test.csv")

# --- 去除重複標題 ---
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

# --- 取得所有新聞標題 ---
titles = df["title"].tolist()
# # ---CKIP斷詞---一次全部斷詞
# #ws_result = ws_driver(titles)
# ws_result = ws_driver(titles, batch_size=32)
# # # 跑迴圈印出每一個標題的斷詞結果
# # for i, words in enumerate(result):
# #     print("原始標題：", titles[i])
# #     print("斷詞結果：", words)
# #     print("-" * 40)
# --- CKIP 斷詞：分段跑，避免一次全部塞進去 ---
chunk_size = 300
ws_result = []
for start in range(0, len(titles), chunk_size):
    chunk = titles[start:start+chunk_size]
    ws_result.extend(ws_driver(chunk, batch_size=8))
    gc.collect()
    print(f"斷詞進度：{min(start+chunk_size, len(titles))}/{len(titles)}")

print_mem("斷詞完成後")

# --- 載入 BERT 情緒分析模型 (最準確，需額外安裝 transformers torch)
# 安裝：pip install transformers torch
# 推薦模型：
#       中文二分類：uer/roberta-base-finetuned-jd-binary-chinese
#       中文多分類：IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment
#       金融英文：  ProsusAI/finbert

print("載入 BERT 模型中...")
clf = pipeline(
    "sentiment-analysis",
    model="uer/roberta-base-finetuned-jd-binary-chinese",
    device=-1       # CPU；GPU 改為 device=0
)
print("✅ 模型載入完成")

# --- BERT 情緒分析 ---
print(f"開始分析 {len(titles)} 筆標題...")

# results = []
# for i, title in enumerate(titles):
#     r = clf(title[:512])[0]
#     results.append({
#         "label": "positive" if r["label"] == "POSITIVE" else "negative",
#         "score": round(r["score"], 4),
#         # 轉成 -1~1 方便後續分析（正數=正面，負數=負面）
#         "score_normalized": round(r["score"], 4) 
#         if r["label"] == "POSITIVE" else round(-r["score"], 4),
#     })
    
#     # 每 50 筆顯示進度
#     if (i + 1) % 50 == 0:
#         print(f"  進度：{i+1}/{len(titles)}")

# results_raw = clf(
#     titles,
#     batch_size=32,      # CPU 可先試 16~32，GPU 可以更高
#     truncation=True,
#     max_length=64,      # 新聞標題通常很短，不需要 512，越短越快
# )

# results = []
# for r in results_raw:
#     is_pos = r["label"].upper() == "POSITIVE" or r["label"] == "positive"
#     results.append({
#         "label": "positive" if is_pos else "negative",
#         "score": round(r["score"], 4),
#         "score_normalized": round(r["score"], 4) 
#         if is_pos else round(-r["score"], 4),
#     })
# clf(titles[0])

# --- BERT 情緒分析：同樣分段跑 ---
results = []
for start in range(0, len(titles), chunk_size):
    chunk = titles[start:start+chunk_size]
    chunk_results = clf(chunk, batch_size=8, truncation=True, max_length=64)
    for r in chunk_results:
        is_pos = r["label"].startswith("positive")
        results.append({
            "label": "positive" if is_pos else "negative",
            "score": round(r["score"], 4),
            "score_normalized": round(r["score"], 4) 
            if is_pos else round(-r["score"], 4),
        })
    gc.collect()
    print(f"情緒分析進度：{min(start+chunk_size, len(titles))}/{len(titles)}")

print_mem("情緒分析完成後")

# # --- 寫回 DataFrame ---
# df["sentiment"] = [r["label"] for r in results]
# df["score"]     = [r["score"] for r in results]
# df["score_normalized"] = [r["score_normalized"] for r in results]

# # --- 印出結果 ---
# print(f"\n✅ 完成！情緒分布：{df['sentiment'].value_counts().to_dict()}")

# for i, words in enumerate(ws_result):
#     print(f"\n原始標題：{titles[i]}")
#     print(f"斷詞結果：{words}")
#     print(f"情緒標籤：{results[i]['label']}")
#     print(f"情緒分數：{results[i]['score_normalized']:+.4f}")
#     print("-" * 40)

# # --- 儲存結果 ---
# df.to_csv("source/news_sentiment_wang.csv", index=False, encoding="utf-8-sig")
# print("\n✅ 結果已儲存至 news_sentiment_wang.csv")