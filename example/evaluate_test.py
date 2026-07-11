import jieba
import pandas as pd

# 1. 讀取台大情緒字典（請確保這兩個 txt 檔放在你的專案目錄下）
# 提示：讀取時可以用 readlines() 把所有詞抓出來，並用 strip() 去除換行符號
with open("正面詞無重複_9365詞.txt", "r", encoding="big5") as f:
    pos_words = set([line.strip() for line in f.readlines()])

with open("負面詞無重複_11230詞.txt", "r", encoding="big5") as f:
    neg_words = set([line.strip() for line in f.readlines()])


# 2. 定義一個函數：用來計算單一文本的情緒分數
def calculate_sentiment(text):
    if pd.isna(text):
        return 0

    # 使用 jieba 斷詞
    words = jieba.lcut_for_search(str(text))

    # 計算正面詞與負面詞出現的次數
    pos_count = sum(1 for word in words if word in pos_words)
    neg_count = sum(1 for word in words if word in neg_words)

    # 計算最終情緒分數 (正面減負面)
    score = pos_count - neg_count
    return score


# 3. 讀取你的股市新聞檔案
df = pd.read_csv("TaiwanStockNews_test.csv")

# 4. 將函數套用到每一個 title（或內文），產生新的一欄叫 'sentiment_score'
df["sentiment_score"] = df["title"].apply(calculate_sentiment)


# 5. 根據分數標記情緒類別
def get_label(score):
    if score > 0:
        return "正面"
    elif score < 0:
        return "負面"
    else:
        return "中立"


df["sentiment_label"] = df["sentiment_score"].apply(get_label)

# 6. 顯示結果並存檔
print(df[["title", "sentiment_score", "sentiment_label"]].head(10))


df.to_csv(
    "TaiwanStockNews_with_sentiment.csv", index=False, encoding="utf-8-sig"
)
print("\n情緒分析完成，已存檔！")