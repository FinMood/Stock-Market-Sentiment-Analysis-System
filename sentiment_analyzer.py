import json
import os
import re
import time
import pandas as pd
import jieba
from openai import OpenAI

try:
    import llm_config
except ImportError:
    llm_config = None

# ==================== 1. API 初始化 (Groq -> Cerebras -> OpenRouter) ====================
def init_ai_client():
    if not llm_config:
        print("⚠️ [警告] 找不到 llm_config.py，將僅使用台大字典評分。")
        return None, "none"

    groq_key = getattr(llm_config, "GROQ_API_KEY", "")
    cerebras_key = getattr(llm_config, "CEREBRAS_API_KEY", "")
    openrouter_key = getattr(llm_config, "OPENROUTER_API_KEY", "")

    # 1. 首選: Groq
    if groq_key and "你的" not in groq_key and groq_key.startswith("gsk_"):
        print("🤖 [API 初始化] 啟用首選極速引擎：Groq (llama-3.1-8b-instant)")
        return OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1"), "llama-3.1-8b-instant"

    # 2. 次選: Cerebras
    if cerebras_key and "你的" not in cerebras_key and cerebras_key.startswith("csk-"):
        print("🤖 [API 初始化] 啟用備援引擎：Cerebras (llama3.1-70b)")
        return OpenAI(api_key=cerebras_key, base_url="https://api.cerebras.ai/v1"), "llama3.1-70b"

    # 3. 三選: OpenRouter
    if openrouter_key and "你的" not in openrouter_key and openrouter_key.startswith("sk-or-"):
        print("🤖 [API 初始化] 啟用備援引擎：OpenRouter (llama-3.3-70b-instruct:free)")
        return OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        ), "meta-llama/llama-3.3-70b-instruct:free"

    print("⚠️ [警告] 未設置任何有效 API Key，將切換為純台大字典模式！")
    return None, "none"


client, MODEL_NAME = init_ai_client()

# ==================== 2. NTUSD 台大字典載入 ====================
degree_dict = {"非常": 1.5, "極度": 1.8, "稍微": 0.6, "爆發": 1.3, "勁揚": 1.4, "飆": 1.5, "衝": 1.3}
not_words = ["不", "沒", "沒有", "未", "無", "並非", "逆勢"]

pos_words = set()
neg_words = set()

def load_ntusd_dictionaries():
    global pos_words, neg_words
    pos_path = os.path.join("NTUSD", "正面詞無重複_9365詞.txt")
    neg_path = os.path.join("NTUSD", "負面詞無重複_11230詞.txt")

    try:
        with open(pos_path, "r", encoding="utf-8") as f:
            pos_words = set([line.strip() for line in f if line.strip()])
        with open(neg_path, "r", encoding="utf-8") as f:
            neg_words = set([line.strip() for line in f if line.strip()])
        print("✅ [字典載入] 成功載入 NTUSD 金融詞典！")
    except Exception:
        pos_words = {"利多", "漲", "報喜", "超預期", "買超", "強勁", "營收新高", "大漲", "新高", "勁揚", "飆漲", "創新高"}
        neg_words = {"跌", "危機", "提款", "減產", "賣超", "衰退", "虧損", "下挫", "爆砍", "保衛戰"}


load_ntusd_dictionaries()


# ==================== 3. 台大字典評分引擎 ====================
def get_dictionary_score(title):
    words = list(jieba.cut(str(title)))
    score = 0.0
    hit_count = 0

    for i, word in enumerate(words):
        word_score = 1.0 if word in pos_words else (-1.0 if word in neg_words else 0.0)
        if word_score != 0.0:
            hit_count += 1
            modifier = 1.0
            for look_back in [1, 2]:
                if i - look_back >= 0:
                    prev_word = words[i - look_back]
                    if prev_word in not_words:
                        modifier *= -1.0
                    elif prev_word in degree_dict:
                        modifier *= degree_dict[prev_word]
            score += word_score * modifier

    if hit_count == 0:
        return 0.0

    return round(max(min(score / max(hit_count, 1), 1.0), -1.0), 2)


# ==================== 4. Batch 20 打包 LLM 評分引擎 ====================
def get_llm_score_batch(titles):
    if not client or not titles:
        return [None] * len(titles)

    formatted_titles = "\n".join([f"{i}: {t}" for i, t in enumerate(titles)])
    
    prompt = f"""你是一位精通台灣股市的資深金融分析師。請評估以下新聞標題的情緒分數 (-1.0 到 1.0)。
1.0 代表極度利多，0.0 代表中立，-1.0 代表極度利空。
請嚴格回傳一個 JSON 數字陣列，陣列長度必須剛好等於 {len(titles)}。
格式範例：[0.55, -0.2, 0.0, 0.8]
絕對不要包含任何 Markdown 標籤或說明文字。

新聞標題清單：
{formatted_titles}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        raw_content = response.choices[0].message.content.strip()
        cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()
        
        match = re.search(r'\[\s*[-+]?\d*\.?\d+.*\]', cleaned_content, re.DOTALL)
        if match:
            scores = json.loads(match.group(0))
            if isinstance(scores, list) and len(scores) == len(titles):
                return [round(float(s), 2) for s in scores]

    except Exception as e:
        print(f"⚠️ [Batch API 呼叫異常]: {str(e)[:80]}")
    
    return [None] * len(titles)


def process_news_in_batches(titles, batch_size=20):
    all_scores = []
    total = len(titles)
    
    for i in range(0, total, batch_size):
        batch_titles = titles[i:i + batch_size]
        print(f"📦 正處理批次 [{i+1} ~ {min(i+batch_size, total)} / {total}]...")
        
        scores = get_llm_score_batch(batch_titles)
        all_scores.extend(scores)
        time.sleep(0.1)
        
    return all_scores


# ==================== 5. 增量快取評分與導出 CSV ====================
def analyze_and_save_csv(df, output_dir="./output"):
    os.makedirs(output_dir, exist_ok=True)
    cache_file = os.path.join(output_dir, "sentiment_cache.csv")

    if 'title' not in df.columns:
        print("⚠️ [錯誤] 傳入的 DataFrame 缺少 'title' 欄位！")
        return df, df

    # 1. 讀取歷史評分快取
    if os.path.exists(cache_file):
        df_cache = pd.read_csv(cache_file, encoding="utf-8-sig")
        print(f"📦 [快取機制] 成功載入歷史評分快取，已保存 {len(df_cache)} 筆紀錄。")
    else:
        df_cache = pd.DataFrame(columns=['title', 'dict_score', 'llm_score'])
        print("📦 [快取機制] 未發現歷史紀錄，建立全新快取檔案。")

    # 2. 找出未曾評分過的新新聞
    existing_titles = set(df_cache['title'].dropna())
    df_new = df[~df['title'].isin(existing_titles)].copy().reset_index(drop=True)

    print(f"🔍 [增量比對] 輸入資料 {len(df)} 筆 | 歷史快取 {len(existing_titles)} 筆 | 待計算新新聞：{len(df_new)} 筆")

    # 3. 僅對「新新聞」進行評分
    if len(df_new) > 0:
        new_titles = df_new['title'].tolist()

        print("\n🔍 [1/2] 開始對新新聞計算台大字典 (NTUSD) 分數...")
        df_new['dict_score'] = [get_dictionary_score(t) for t in new_titles]

        print("\n🤖 [2/2] 開始對新新聞計算 LLM (AI) 分數...")
        df_new['llm_score'] = process_news_in_batches(new_titles)

        # 4. 將評分好的新資料追加進歷史快取中
        new_cache_items = df_new[['title', 'dict_score', 'llm_score']]
        df_updated_cache = pd.concat([df_cache, new_cache_items], ignore_index=True)
        df_updated_cache.drop_duplicates(subset=['title'], keep='first', inplace=True)
        
        df_updated_cache.to_csv(cache_file, index=False, encoding="utf-8-sig")
        print(f"✅ [快取更新] 評分完成！已將 {len(df_new)} 筆新紀錄寫入：{cache_file}")
    else:
        print("⚡ [快速完成] 所有新聞均已在快取中，跳過重複計算！\n")
        df_updated_cache = df_cache

    # 5. 將評分對齊回原始資料 (保留原本的 date 欄位等)
    df_final = pd.merge(df, df_updated_cache[['title', 'dict_score', 'llm_score']], on='title', how='left')

    # 6. 導出結果 CSV
    df_dict = df_final.drop(columns=['llm_score'], errors='ignore')
    df_llm = df_final.drop(columns=['dict_score'], errors='ignore')

    df_dict.to_csv(os.path.join(output_dir, "dictionary_results.csv"), index=False, encoding="utf-8-sig")
    df_llm.to_csv(os.path.join(output_dir, "llm_results.csv"), index=False, encoding="utf-8-sig")
    df_final.to_csv(os.path.join(output_dir, "sentiment_comparison.csv"), index=False, encoding="utf-8-sig")

    print(f"📊 [檔案輸出] 成功寫入 output 目錄（已完成資料對齊）")

    return df_dict, df_llm