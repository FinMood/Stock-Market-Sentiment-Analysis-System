#
# 需要先安裝 python 套件: torch, transfomers
# 測試在以下套件版本執行成功
#   torch: 2.11.0+cpu
#   transformers: 5.13.1
#
# 安裝指令:
#   pip torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
#   pip transformers==5.13.1
#

## Packages ##
import os
import time
import math
import pandas as pd

from transformers import TextClassificationPipeline
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from transformers import AutoTokenizer, BertTokenizerFast




def finbert_sent_test_func(news_dir, finbert_model_dir, score_dir, news_title_fname, output_fname, finbert_proc_size):

    # 0. 建立變數名稱
    news_title_fpath = f"{news_dir}/{news_title_fname}"
    processed_dir = f"{score_dir}/processed"

    model_dir = finbert_model_dir

    proc_fprefix = news_title_fname.replace(".csv", "")

    news_sent_fpath = f"{processed_dir}/{proc_fprefix}_w_finbert_sents_1.csv"
    news_score_fpath = f"{score_dir}/{output_fname}"

    proc_size = finbert_proc_size


    # 1. 載入新聞標題
    news_title_df = pd.read_csv(news_title_fpath)
    print(f"載入新聞標題: {news_title_fpath}")

    news_title_list = news_title_df["title"].tolist()
    news_num = len(news_title_list)

    # 2. 載入 FinBERT 模型
    # 如果模型沒有儲存在local，會從hugging face下載模型
    if model_dir is None:
        model_dir = "models/finbert_chinese"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print("下載 FinBERT 情緒分析模型")
        model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone-chinese", output_attentions=True)
        tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone-chinese")

        # 儲存模型在local，避免超過hugging face的下載次數
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        print(f"儲存 FinBERT 在本地: {model_dir}")
    else:
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, output_attentions=True)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
    print("載入 FinBERT 情緒分析模型\n")

    # make a classifier
    classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)


    # 3. 使用 FinBERT 進行情緒分析，收集結果到 clf_results_list
    #
    clf_results_list = []
    proc_num = math.ceil(news_num / proc_size)
    print("使用 FinBERT 進行情緒分析...")
    print(f"總共{news_num}筆資料，分成{proc_num}份")
    st = time.time()
    for i in range(proc_num):
        sidx = i * proc_size
        eidx = (i+1) * proc_size

        if sidx >= news_num:
            break

        news_titles = news_title_list[sidx:eidx]
        # make a classification
        results_list = classifier(news_titles)

    #    for j in range(len(results_list)):
    #        print(f"news_titles {j}: {news_titles[j]}")
    #        print(f"results_list {j}: {results_list[j]}")
    #        print()

        clf_results_list.extend(results_list)
        et = time.time()
        print(f"情緒分析完成度: {i+1}份/{proc_num}份, 共耗時: {et - st:.3f} 秒")
    print()

    #4. 建立情緒分數表: 建立label和score
    news_sent_list = []

    print("建立情緒分數表...")
    st = time.time()
    for i in range(news_num):

        result = clf_results_list[i]
    #    print(f"news_title: {news_title}")

        # make a sentiment dict
        sent_dict = {"label": "", "conf_score": 0.0,
                    "my_score": 0.0, "score": 0.0}

        # compute sentiment score
        # compute score = confidence * {pos:1, neu:0, neg:-1} by now
        label = result['label']
        conf_score = result['score']

        sent_dict["conf_score"] = conf_score
        if label == "Positive":
            sent_dict["label"] = "正面"
            sent_dict["score"] = 1 * conf_score
            sent_dict["my_score"] = 0.5 + conf_score
        elif label == "Negative":
            sent_dict["label"] = "負面"
            sent_dict["score"] = -1 * conf_score
            sent_dict["my_score"] = -1 * 0.5 - conf_score
        else:
            sent_dict["label"] = "中性"
            sent_dict["score"] = 0
            sent_dict["my_score"] = conf_score - 0.5

    #    print(f"sent_dict: {sent_dict}")
    #    print()

        news_sent_list.append(sent_dict)
    et = time.time()
    print(f"建立情緒分數表共花費: {et - st:.3f} 秒\n")

    # 5. 檢查情緒分析的結果
    print("輸出情緒分析的結果(前100筆):")
    for i in range(min(100, news_num)):
        print(news_title_list[i])
        print(news_sent_list[i])
        print()


    # 6. 將情緒分析做後處理: 改變float位數、合併DataFrame
    # create a sentiment df
    news_sent_df = pd.DataFrame(news_sent_list)

    # round float number
    news_sent_df["conf_score"] = news_sent_df["conf_score"].round(4)
    news_sent_df["my_score"] = news_sent_df["my_score"].round(4)
    news_sent_df["score"] = news_sent_df["score"].round(4)

    # copy a single score column
    news_score_df = news_sent_df[["score"]].copy()

    # concatenate title with sentiment results into a DataFrame
    news_title_sent_df = pd.concat([news_title_df, news_sent_df], axis=1)
    news_title_score_df = pd.concat([news_title_df, news_score_df], axis=1)


    # 7. 儲存情緒分析的結果和情緒分數
    if not os.path.exists(score_dir):
        os.makedirs(score_dir)
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    news_title_sent_df.to_csv(news_sent_fpath, index=False)
    news_title_score_df.to_csv(news_score_fpath, index=False)
    print("儲存情緒分析表和分數")
    print(news_sent_fpath)
    print(news_score_fpath)

    # 8. 驗證資料: 確認資料的正確性
    # 載入 CSV 檔
    news_title_score_df2 = pd.read_csv(news_score_fpath)

    # 確認儲存和載入的資料一樣
    is_df_equal = news_title_score_df2.equals(news_title_score_df)
    print(f"情緒分數結果儲存成功?: {is_df_equal}")

    # 新聞標題欄位是否相同
    is_title_equal = news_title_score_df2["title"].equals(news_title_df["title"])
    print(f"新聞標題欄位相同?: {is_title_equal}")

    # 情緒分數是否都介於[-1, 1]之間
    is_scores_in_range = news_title_score_df2["score"].between(-1, 1).all()
    print(f"情緒分數都介於[-1, 1]之間?: {is_scores_in_range}\n")


