import pandas as pd
import jieba

# 1. 載入新聞標題
news_title_fname = "tsmc_news_2026_back.csv"

news_title_df = pd.read_csv(news_title_fname)
news_title_list = news_title_df["title"].tolist()


# 2. 載入 NTUSD 正向/負向詞
pos_fpath = "NTUSD/正面詞無重複_9365詞.txt"
neg_fpath = "NTUSD/負面詞無重複_11230詞.txt"

pos_df = pd.read_csv(pos_fpath, header=None, names=["word"], encoding="big5")
pos_words_list = pos_df["word"].tolist()
#print(pos_words_list)

neg_df = pd.read_csv(neg_fpath, header=None, names=["word"], encoding="big5")
neg_words_list = neg_df["word"].tolist()
#print(neg_words_list)


# 3. 製作新聞字典 (包含 斷詞結果 和 情緒字典)
news_dicts_list = []
for title in news_title_list:
    news_dict = {}

    # tokenize with Jieba
    tokens_list = jieba.cut(title, cut_all=False)
#    tokens_list = jieba.cut_for_search(title)
    tokens_list = list(tokens_list)

    # make NTUSD sentiment dict
    sent_dict = {"pos":{}, "neg":{}, "pos_cnt":0, "neg_cnt":0}
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

    # record tokens and sentiment dict
    news_dict["tokens"] = tokens_list
    news_dict["sent_dict"] = sent_dict
    news_dicts_list.append(news_dict)

# 4. 檢查 斷詞 和 情緒字典 的結果
for news_dict in news_dicts_list:
    print(news_dict["tokens"])
    print(news_dict["sent_dict"])
    print()


# 5. 儲存結果為一份 JSON 檔
save_news_fname = "tsmc_news_2026_tokens_n_sents_1.json"
news_dict_df = pd.DataFrame(news_dicts_list)
news_dict_df.to_json(save_news_fname, orient="records")


# 6. 載入 JSON 檔，確認儲存和載入的資料一樣
load_news_fname = "tsmc_news_2026_tokens_n_sents_1.json"
news_dict_df2 = pd.read_json(load_news_fname)

print(f"news_dict_df and news_dict_df2 are equal: {news_dict_df.equals(news_dict_df2)}")

