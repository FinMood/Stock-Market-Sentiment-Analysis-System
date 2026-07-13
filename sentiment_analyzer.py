import jieba

# 全局自訂修飾詞與否定詞
degree_dict = {"非常": 1.5, "極度": 1.8, "稍微": 0.6, "爆發": 1.3}
not_words = ["不", "沒", "沒有", "未", "無", "並非"]

def calculate_sentiment_score(title, pos_words, neg_words):
    """
    根據外部載入的正負向詞典，計算單一標題的情緒分數 (-1.0 ~ 1.0)
    """
    words = list(jieba.cut(title))
    score = 0.0
    i = 0
    
    while i < len(words):
        word = words[i]
        word_score = 0.0
        
        # 判斷是否在外部 NTUSD 詞典中
        if word in pos_words:
            word_score = 1.0  # 正面詞
        elif word in neg_words:
            word_score = -1.0 # 負面詞
            
        if word_score != 0.0:
            modifier = 1.0
            # 往前檢查前兩個詞（處理否定詞與程度副詞）
            for look_back in [1, 2]:
                if i - look_back >= 0:
                    prev_word = words[i - look_back]
                    if prev_word in not_words:
                        modifier *= -1.0
                    elif prev_word in degree_dict:
                        modifier *= degree_dict[prev_word]
            score += word_score * modifier
        i += 1
        
    # 保持 -1.0 ~ 1.0 的標準區間
    final_score = max(min(score / 2.0, 1.0), -1.0)
    return round(final_score, 2)