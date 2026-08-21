#
# 需要先安裝 python 套件: torch, transfomers
#
# 測試在以下套件版本執行成功
#   torch: 2.11.0+cpu
#   transformers: 5.13.1
#   ckip_transformers: 0.3.4
#
# 安裝指令:
#   pip torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
#   pip transformers==5.13.1
#   pip ckip_transformers==0.3.4
#


## Packages ##
import os
import time
import math
import pandas as pd
from ckip_transformers.nlp import CkipWordSegmenter



def ckipbert_sent_test_func(news_dir, ckip_model_dir, ntusd_dir, score_dir, news_title_fname, output_fname, ckip_proc_size):

    # 0. 建立變數名稱
    news_title_fpath = f"{news_dir}/{news_title_fname}"
    processed_dir = f"{score_dir}/processed"

    model_dir = ckip_model_dir

    pos_fpath = f"{ntusd_dir}/正面詞無重複_9365詞.txt"
    neg_fpath = f"{ntusd_dir}/負面詞無重複_11230詞.txt"

    proc_fprefix = news_title_fname.replace(".csv", "")

    news_ws_fpath = f"{processed_dir}/{proc_fprefix}_ws_ckip_1.json"
    news_dicts_fpath = f"{processed_dir}/{proc_fprefix}_dicts_ckip_1.json"
    news_score_fpath = f"{score_dir}/{output_fname}"

    proc_size = ckip_proc_size

    # 1. 載入新聞標題
    news_title_df = pd.read_csv(news_title_fpath)
    print(f"載入新聞標題: {news_title_fpath}")

    news_title_list = news_title_df["title"].tolist()
    #print(f"news_title_list: {news_title_list}")
    news_num = len(news_title_list)


    # 2. 載入 CKIP Transformers (bert-chinese) 模型
    # 如果模型沒有儲存在local，會從hugging face下載模型
    if model_dir is None:
        model_dir = "models/ckip_bert_chinese_ws"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print("下載 CKIP BERT-base 斷詞模型")
        ws_driver  = CkipWordSegmenter(model="bert-base")

        # 儲存模型在local，避免超過hugging face的下載次數
        ws_driver.tokenizer.save_pretrained(model_dir)
        ws_driver.model.save_pretrained(model_dir)
        print(f"儲存 CKIP BERT-base 在本地: {model_dir}")
    else:
        ws_driver  = CkipWordSegmenter(model_name=model_dir)
    print(f"載入 CKIP BERT-base 斷詞模型: {model_dir}")


    # 3. 載入斷詞結果，如果沒有，會進行斷詞
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    if os.path.exists(news_ws_fpath):
        news_ws_df = pd.read_json(news_ws_fpath)
        print(f"載入斷詞結果: {news_ws_fpath}")

        news_ws_list = news_ws_df["token"].tolist()
    else:
        # run pipeline
        # it may take a while...
        # need save results to a tmp file
        news_ws_list = []

        proc_num = math.ceil(news_num / proc_size)

        print(f"使用 CKIP BERT-base 斷詞...")
        print(f"總共{news_num}筆資料，分成{proc_num}份")
        st = time.time()
        for i in range(proc_num):
            sidx = i * proc_size
            eidx = (i + 1) * proc_size

            if sidx >= news_num:
                break

            title_list = news_title_list[sidx:eidx]
            # tokenizate title
            ws_list = ws_driver(title_list)

#            for j in range(len(title_list)):
#                print(f"title_list {j}: {title_list[j]}")
#                print(f"ws_list {j}: {ws_list[j]}")
#                print()

            news_ws_list.extend(ws_list)
            et = time.time()
            print(f"斷詞完成度:{i+1}份/{proc_num}份，共花費: {et - st:.3f} 秒")

#        for i in range(news_num):
#            print(news_title_list[i])
#            print(news_ws_list[i])
#            print()

        # 儲存 CKIP Transformers 斷詞結果
        # transform list to DataFrame
        news_token_df = pd.DataFrame({"token": news_ws_list})
        # save dataframe to JSON file
        news_token_df.to_json(news_ws_fpath, orient="records")
        print(f"儲存斷詞結果: {news_ws_fpath}")

    # 4. 載入 NTUSD 正向/負向詞
    pos_df = pd.read_csv(pos_fpath, header=None, names=["word"], encoding="utf-8")
    pos_words_list = pos_df["word"].tolist()
    #print(pos_words_list)

    neg_df = pd.read_csv(neg_fpath, header=None, names=["word"], encoding="utf-8")
    neg_words_list = neg_df["word"].tolist()
    #print(neg_words_list)
    print("載入 NTUSD 情緒字典")


    # 5. 載入情緒評分結果，如果沒有，會計算情緒評分
    if os.path.exists(news_dicts_fpath):
        sent_dicts_df = pd.read_json(news_dicts_fpath)
        sent_dicts_list = sent_dicts_df.to_dict(orient="records")
        print(f"載入情緒評分結果: {news_dicts_fpath}")
    else:
        sent_dicts_list = []
        print("進行情緒評分...")
        st = time.time()
        for i in range(news_num):

            title = news_title_list[i]
            tokens_list = news_ws_list[i]

            # make NTUSD sentiment dict
            sent_dict = {"pos": {}, "neg": {},
                        "pos_cnt": 0, "neg_cnt": 0,
                        "score": 0, "label": ""}

            for token in tokens_list:
                if token in pos_words_list:
                    sent_dict["pos_cnt"] += 1

                    if token in sent_dict["pos"]:
                        sent_dict["pos"][token] += 1
                    else:
                        sent_dict["pos"][token] = 1

                if token in neg_words_list:
                    sent_dict["neg_cnt"] += 1

                    if token in sent_dict["neg"]:
                        sent_dict["neg"][token] += 1
                    else:
                        sent_dict["neg"][token] = 1

            # compute score
            pos_cnt = sent_dict["pos_cnt"]
            neg_cnt = sent_dict["neg_cnt"]
            total_cnt = pos_cnt + neg_cnt
            sent_dict["score"] = (pos_cnt - neg_cnt) / max(total_cnt, 1.)

            # label based on socre
            if pos_cnt > neg_cnt:
                sent_dict["label"] = "正面"
            elif pos_cnt == neg_cnt:
                sent_dict["label"] = "中立"
            else:
                sent_dict["label"] = "負面"

            sent_dicts_list.append(sent_dict)

        et = time.time()
        print(f"情緒評分花費: {et - st:.3f} 秒")
        # 儲存情緒評分結果
        sent_dicts_df = pd.DataFrame(sent_dicts_list)
        sent_dicts_df.to_json(news_dicts_fpath, orient="records")
        print(f"儲存情緒評分結果: {news_dicts_fpath}")


    # 6. 檢查 斷詞 和 情緒評分 的結果
    print("輸出斷詞和情緒評分結果(前100筆):")
    for i in range(min(100, news_num)):
        print(news_title_list[i])
        print(news_ws_list[i])
        print(sent_dicts_list[i])
        print()


    # 7. 儲存 新聞標題 和 情緒分數 為一份 CSV 檔
    if not os.path.exists(score_dir):
        os.makedirs(score_dir)

    sent_scores_df = sent_dicts_df[["score"]].copy()

    # round float number
    sent_scores_df["score"] = sent_scores_df["score"].round(4)

    news_title_scores_df = pd.concat([news_title_df, sent_scores_df], axis=1)
    news_title_scores_df.to_csv(news_score_fpath, index=False)
    print(f"儲存新聞標題情緒分數: {news_score_fpath}")


    # 8. 驗證資料: 確認資料的正確性
    # 載入 CSV 檔
    news_title_scores_df2 = pd.read_csv(news_score_fpath)

    # 確認儲存和載入的資料一樣
    is_df_equal = news_title_scores_df2.equals(news_title_scores_df)
    print(f"情緒分數結果儲存成功?: {is_df_equal}")

    # 新聞標題欄位是否相同
    is_title_equal = news_title_scores_df2["title"].equals(news_title_df["title"])
    print(f"新聞標題欄位相同?: {is_title_equal}")

    # 情緒分數是否都介於[-1, 1]之間
    is_scores_in_range = news_title_scores_df2["score"].between(-1, 1).all()
    print(f"情緒分數都介於[-1, 1]之間?: {is_scores_in_range}\n")

