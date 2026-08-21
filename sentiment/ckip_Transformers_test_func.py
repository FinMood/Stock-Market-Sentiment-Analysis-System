# 台灣中央研究院開發，專門針對繁體中文斷詞
# Roberta情緒分析模型，中文二分類
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




## 新增一個函數 ckip_Transformers_test_func()，方便串接專案
def ckip_Transformers_test_func(input_dir, input_fname, output_dir, output_fname):


    def print_mem(tag=""):
        mem = psutil.virtual_memory()
        print(f"[{tag}] 可用記憶體：{mem.available / (1024**3):.2f} GB / 總量 {mem.total / (1024**3):.2f} GB")

    print_mem("開始前")

    # 最快（Level 1）： model="albert-tiny"
    # 平衡（Level 2）： model="albert-base"
    # 最精確（Level 3）： model="bert-base"

    # # --- CKIP 斷詞模型 ---
    ws_driver = CkipWordSegmenter(model="albert-tiny", device=-1)

    # # 測試一下
    # text = ["金融新聞情緒分析"]
    # result = ws_driver(text)
    # words = result[0]
    # print(words)

#    # 讀取CSV
#    input_file = (
#        "/home/jessie_wang/"
#        "Stock-Market-Sentiment-Analysis-System/"
#        "source/TaiwanStockNews_test.csv"
#    )
    input_file = f"{input_dir}/{input_fname}"

    try:
        df = pd.read_csv(input_file)

    except FileNotFoundError:
        print("❌ 找不到 CSV")
        exit()

    # --- 去除重複標題 ---
    before = len(df)

    # 去除重複標題 (# 整列完全相同才去除 # 只看 title 欄是否重複)

    df["title"] = (
        df["title"]
        .fillna("")
        .str.strip()
        .str.replace(r"[\s,，。！？、；：""''【】《》()（）]", "", regex=True)
    )
    df = df.drop_duplicates(subset=["date","title"])
    after = len(df)

    print(f"去重前：{before} 筆")
    print(f"去重後：{after} 筆")
    print(f"移除了：{before - after} 筆重複標題")

    # # --- 取得所有新聞標題 ---
    titles = df["title"].tolist()
    # # ---CKIP斷詞---一次全部斷詞
    # ws_result = ws_driver(titles)
    # ws_result = ws_driver(titles, batch_size=32)
    # # # 跑迴圈印出每一個標題的斷詞結果
    # # for i, words in enumerate(result):
    # #     print("原始標題：", titles[i])
    # #     print("斷詞結果：", words)
    # #     print("-" * 40)
    # --- CKIP 斷詞：分段跑，避免一次全部塞進去 ---
    chunk_size = 500
    ws_result = []
    print("\n開始 CKIP 斷詞...")
    for start in range(0, len(titles), chunk_size):
        chunk = titles[start:start + chunk_size]
        ws_result.extend(ws_driver(chunk, batch_size=16))
        gc.collect()
        print(f"斷詞進度：{min(start+chunk_size, len(titles))}/{len(titles)}")

    print_mem("斷詞完成後")

    # --- 載入 BERT 情緒分析模型 (最準確，需額外安裝 transformers torch)
    # 安裝：pip install transformers torch
    # 模型：中文二分類：IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment

    print("載入 BERT 模型中...")
    # clf = pipeline(
    #     "sentiment-analysis",
    #     model="IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment",
    #     device=-1       # CPU；GPU 改為 device=0
    # )

    def load_sentiment_model():
        return pipeline(
            "sentiment-analysis",
            model="IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment",
            #模型改為五分類，方便後續做情緒分數計算(不準確)
            #model="tabularisai/multilingual-sentiment-analysis",
            device=-1
        )
    print("\n載入情緒分析模型中...")

    clf = load_sentiment_model()

    print("✅ 情緒模型載入完成")

    #看模型有哪些分類 label
    print("模型標籤：")
    print(clf.model.config.id2label)

    print("模型分類數：")
    print(clf.model.config.num_labels)


    # --- BERT 情緒分析：同樣分段跑 ---
    # results = []
    # for start in range(0, len(titles), chunk_size):
        # chunk = titles[start:start+chunk_size]
        # chunk_results = clf(chunk, batch_size=8, truncation=True, max_length=64)
        # for r in chunk_results:
            # is_pos = r["label"].startswith("positive")
            # results.append({
                # "label": "positive" if is_pos else "negative",
                # "score": round(r["score"], 4),
                # "score_normalized": round(r["score"], 4)
                # if is_pos else round(-r["score"], 4),
            # })
        # gc.collect()
        # print(f"情緒分析進度：{min(start+chunk_size, len(titles))}/{len(titles)}")
    #
    # print_mem("情緒分析完成後")

    # label_map = {
    #     "LABEL_0": "neutral",
    #     "LABEL_1": "positive",
    #     "LABEL_2": "negative",
    # }
    # --- BERT 情緒分析 ---
    results = []

    print(f"開始分析 {len(titles)} 筆標題...")

    for start in range(0, len(titles), chunk_size):
        chunk = titles[start:start+chunk_size]
        chunk_results = clf(chunk, batch_size=8, truncation=True, max_length=64)
        for r in chunk_results:
            sentiment = r["label"].lower()
            confidence = r["score"]
            if sentiment == "positive":
                score_norm = round(confidence, 4)
            elif sentiment == "negative":
                score_norm = round(-confidence, 4)
            else:  # neutral
                print(f"⚠️ 未知情緒標籤：{sentiment}")
                score_norm = 0.0
            # #五分類(不準確)
            # score_map = {
            #     "very negative": -2,
            #     "negative": -1,
            #     "neutral": 0,
            #     "positive": 1,
            #     "very positive": 2
            # }
            # #score_norm = score_map.get(sentiment, 0)
            # score_norm = score_map[sentiment] * r["score"]#保留信心強度

            results.append({
                "label": sentiment,
                "score": round(confidence, 4), #模型對這個判斷的信心強度, 0 ~ 1（永遠正數）
                "score_normalized": score_norm, #信心強度 + 方向(正面/負面)，-1 ~ 1(正負皆有)
            })
        gc.collect()
        print(f"情緒分析進度：{min(start+chunk_size, len(titles))}/{len(titles)}")

    print_mem("情緒分析完成")

    # --- 寫回 DataFrame ---
    df["sentiment"] = [r["label"] for r in results]
    df["score"]     = [r["score"] for r in results]
    df["score_normalized"] = [r["score_normalized"] for r in results]

    # --- 印出結果 ---
    print(f"\n✅ 完成！情緒分布：{df['sentiment'].value_counts().to_dict()}")

    for i in range(min(20, len(titles))):
        print(f"\n原始標題：{titles[i]}")
        #print(f"斷詞結果：{words}")
        print(f"CKIP 斷詞結果：{' / '.join(ws_result[i])}")
        print(f"情緒標籤：{results[i]['label']}")
        print(f"模型信心：{results[i]['score']:.4f}")
        print(f"情緒分數：{results[i]['score_normalized']:+.4f}")
        print("-" * 50)

    # --- 儲存結果 ---
    #output_dir = "score_data"
    #output_fname = "news_sentiment_wang.csv"
    os.makedirs("score_data", exist_ok=True)
    df.to_csv(f"{output_dir}/{output_fname}", index=False, encoding="utf-8-sig")
    print(f"\n✅ 結果已儲存至 {output_fname}")

