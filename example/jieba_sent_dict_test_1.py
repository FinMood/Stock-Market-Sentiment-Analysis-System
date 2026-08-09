import os
import time
import pandas as pd
import jieba



# 1. 載入新聞標題
news_title_fpath = "source/TaiwanStockNews_test.csv"


news_title_df = pd.read_csv(news_title_fpath)
print(f"載入新聞標題: {news_title_fpath}")

news_title_list = news_title_df["title"].tolist()
news_num = len(news_title_list)


# 2. 載入斷詞結果，如果沒有，會進行斷詞
processed_dir = "processed"

news_ws_fpath = f"{processed_dir}/TaiwanStockNews_test_ws_jieba_1.json"

if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

if os.path.exists(news_ws_fpath):
    news_ws_df = pd.read_json(news_ws_fpath)
    news_ws_list = news_ws_df["token"].tolist()
    print(f"載入斷詞結果: {news_ws_fpath}")
else:
    print(f"使用 Jieba 斷詞...")
    st = time.time()
    news_ws_list = []
    for title in news_title_list:
#        tokens_list = jieba.cut(title, cut_all=False)
        tokens_list = jieba.lcut_for_search(title)
        tokens_list = list(tokens_list)
        news_ws_list.append(tokens_list)

    et = time.time()
    print(f"Jieba 花費: {et - st:.3f} 秒")

    #for i in range(news_num):
    #    print(news_title_list[i])
    #    print(news_ws_list[i])
    #    print()

    # 儲存 Jieba 斷詞結果
    # transform list to DataFrame
    news_token_df = pd.DataFrame({"token": news_ws_list})
    # save dataframe to JSON file
    news_token_df.to_json(news_ws_fpath, orient="records")
    print(f"儲存斷詞結果: {news_ws_fpath}")


# 3. 載入 NTUSD 正向/負向詞
pos_fpath = "NTUSD/正面詞無重複_9365詞.txt"
neg_fpath = "NTUSD/負面詞無重複_11230詞.txt"

pos_df = pd.read_csv(pos_fpath, header=None, names=["word"], encoding="big5")
pos_words_list = pos_df["word"].tolist()
#print(pos_words_list)

neg_df = pd.read_csv(neg_fpath, header=None, names=["word"], encoding="big5")
neg_words_list = neg_df["word"].tolist()
#print(neg_words_list)
print("載入 NTUSD 情緒字典")


# 4. 載入情緒評分結果，如果沒有，會計算情緒評分
sent_dicts_fpath = f"{processed_dir}/TaiwanStockNews_test_sent_dicts_jieba_1.json"
if os.path.exists(sent_dicts_fpath):
    sent_dicts_df = pd.read_json(sent_dicts_fpath)
    sent_dicts_list = sent_dicts_df.to_dict(orient="records")
    print(f"載入情緒評分結果: {sent_dicts_fpath}")
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
    sent_dicts_df.to_json(sent_dicts_fpath, orient="records")
    print(f"儲存情緒評分結果: {sent_dicts_fpath}")


# 5. 檢查 斷詞 和 情緒評分 的結果
print("輸出斷詞和情緒評分結果(前100筆):")
for i in range(min(100, news_num)):
    print(news_title_list[i])
    print(news_ws_list[i])
    print(sent_dicts_list[i])
    print()


# 6. 儲存 新聞標題 和 情緒分數 為一份 CSV 檔
score_data_dir = "score_data"
if not os.path.exists(score_data_dir):
    os.makedirs(score_data_dir)

news_title_scores_fpath = f"{score_data_dir}/TaiwanStockNews_test_w_scores_jieba_1.csv"

sent_scores_df = sent_dicts_df[["score"]].copy()

# round float number
sent_scores_df["score"] = sent_scores_df["score"].round(4)

news_title_scores_df = pd.concat([news_title_df, sent_scores_df], axis=1)
news_title_scores_df.to_csv(news_title_scores_fpath, index=False)
print(f"儲存新聞標題情緒分數: {news_title_scores_fpath}")


# 7. 驗證資料，確認資料的正確性
# 載入 CSV 檔
news_title_scores_df2 = pd.read_csv(news_title_scores_fpath)

# 確認儲存和載入的資料一樣
is_df_equal = news_title_scores_df2.equals(news_title_scores_df)
print(f"情緒分數結果儲存成功?: {is_df_equal}")

# 新聞標題欄位是否相同
is_title_equal = news_title_scores_df2["title"].equals(news_title_df["title"])
print(f"新聞標題欄位相同?: {is_title_equal}")

# 情緒分數是否都介於[-1, 1]之間
is_scores_in_range = news_title_scores_df2["score"].between(-1, 1).all()
print(f"情緒分數都介於[-1, 1]之間?: {is_scores_in_range}")
