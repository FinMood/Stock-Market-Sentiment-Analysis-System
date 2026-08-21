# 這個檔案的寫法來自課程 Github 下的 crawler/config.py 和 專案 Github 下的 crawler/config.py 。

import os

# 要抓什麼: 股票清單與日期範圍
STOCK_IDS = ["2330", "2454", "2308"]
START_DATE = os.environ.get("START_DATE", "2026-02-23")
END_DATE = os.environ.get("END_DATE", "2026-02-24")

# 怎麼拿: FinMind API 位址與資料集名稱
FINMIND_NEWS_DATA = os.environ.get("FINMIND_NEWS_DATA", "TaiwanStockNews")

# 資料.csv檔案儲存的資料夾
SOURCE_DIR = os.environ.get("SOURCE_DIR", "source")
SCORE_DATA_DIR = os.environ.get("SCORE_DATA_DIR", "score_data")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")

# 情緒分數輸出結果的名稱
JIEBA_SCORE = os.environ.get("JIEBA_SCORE", "jieba_score")
CKIPBERT_SCORE = os.environ.get("CKIPBERT_SCORE", "ckipbert_score")
FINBERT_SCORE = os.environ.get("FINBERT_SCORE", "finbert_score")
ROBERTA_SCORE = os.environ.get("ROBERTA_SCORE", "roberta_score")
LLM_SCORE = os.environ.get("LLM_SCORE", "llm_score")
SENT_ALL_SCORES = os.environ.get("SENT_ALL_SCORES", "all_scores")

# 情緒分數模型儲存的資料夾
NTUSD_DIR = os.environ.get("NTUSD", "NTUSD")
CKIPBERT_DIR = os.environ.get("CKIPBERT_DIR", "models/ckip_bert_chinese_ws")
FINBERT_DIR = os.environ.get("FINBERT_DIR", "models/finbert_chinese")

# 情緒分數模型的參數
#LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-20b")
LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")

CKIPBERT_PROC_SIZE = int(os.environ.get("CKIPBERT_PROC_SIZE", 100))
FINBERT_PROC_SIZE = int(os.environ.get("FINBERT_PROC_SIZE", 100))
LLM_MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", 3))
LLM_BATCH_SLEEP = float(os.environ.get("LLLM_BATCH_SLEEP", 3.0))



